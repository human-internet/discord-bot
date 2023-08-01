from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, QueryDict
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pyshorteners as ps
from .serializers import *
import requests
import urllib.parse
import environ
from hashlib import blake2b
from hmac import compare_digest

from datetime import datetime, timedelta

env = environ.Env()

# TODO TODO TODO SHOULD BE SECRET
SECRET_KEY = b'pseudorandomly generated server secret key'
AUTH_SIZE = 16

def sign(userId):
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
    h.update(userId)
    return h.hexdigest().encode('utf-8')

def verify(userId, storedId):
    return compare_digest(userId, storedId)


@api_view(['PUT'])
def addServer(request):
    body = QueryDict(request.body)

    if 'serverId' not in body:
        return Response("The server id is required", status=400)

    elif 'clientId' not in body:
        return Response("The client id is required", status=400)

    elif 'secret' not in body:
        return Response("The client secret is required", status=400)

    serverId = body['serverId']
    clientId = body['clientId']
    clientSecret = body['secret']

    duplicate = Server.objects.filter(serverId=serverId).exists()
    if duplicate:
        # TODO do we replace the client id/secret?
        return Response("This server already has an associated credential", status=400)

    else:
        # Create an entry representing the user trying to verify
        Server.objects.create(
            serverId=serverId,
            clientId=clientId,
            clientSecret=clientSecret,
        )

    return HttpResponse(status=200)


@api_view(['GET'])
def getRedirect(request):
    serverQuery = request.query_params.get('serverId', None)

    # Does not have a query
    if not serverQuery:
        return Response("The server id is required", status=400)

    exist = Server.objects.filter(serverId=serverQuery).exists()
    if not exist:
        return Response("This server does not have associated credentials", status=400)

    # Grabs the required data about the server to generate the unique humanID link
    servers = Server.objects.get(serverId=serverQuery)
    serializer = ServerSerializer(servers, many=False).data
    CLIENT_ID = serializer['clientId']
    CLIENT_SECRET = serializer['clientSecret']

    headers = {
        'client-id': CLIENT_ID,
        'client-secret': CLIENT_SECRET,
        'Content-Type': 'application/json'
    }

    # generate weblogin url
    response = requests.post(
        'https://api.human-id.org/v1/server/users/web-login',
        headers=headers,
    )
    if response.status_code != 200:
        return Response("Unable to generate url. Please double check your credentials", status=403)

    resJson = response.json()['data']
    return_url = resJson['webLoginUrl']
    requestId = resJson['requestId']
    short_url = ps.Shortener().tinyurl.short(return_url)

    # Generate the link and send it back
    return Response({
        'url': short_url,
        'requestId': requestId,
    })


@api_view(['PUT'])
def verifyAttempt(request):
    userQuery = request.query_params.get('userId', None)
    reqQuery = request.query_params.get('requestId', None)

    # Does not have a query
    if not userQuery:
        return Response("The user id is required", status=400)

    duplicate = Request.objects.filter(requestId=reqQuery).exists()
    if duplicate:
        # If the user has a duplicate entry, just update the created time
        req = Request.objects.get(requestId=reqQuery)
        req.created  = timezone.now()
        req.userId   = sign(bytes(str(userQuery), 'utf-8'))
        req.verified = False
        req.save()

    else:
        # Create an entry representing the user trying to verify
        Request.objects.create(
            requestId=reqQuery,
            created=timezone.now(),
            userId=sign(bytes(str(userQuery), 'utf-8')),
            verified=False,
        )

    return Response(status=200)


@api_view(['GET'])
def checkVerify(request):
    userQuery = request.query_params.get('requestId', None)
    # Does not have a query
    if not userQuery:
        return Response("The user id is required", status=400)

    # entry with the given requestId doesnt exist
    validAttempt = Request.objects.filter(requestId=userQuery).exists()
    if not validAttempt:
        return Response('No attempt matching the given request id.', status=404)

    req       = Request.objects.get(requestId=userQuery)
    status     = None
    serializer = RequestSerializer(req, many=False).data
    created    = (datetime.fromisoformat(serializer['created']
                                      .replace('T', ' ')
                                      .replace('Z', '')))

    if created - datetime.now() < timedelta(minutes=10) and serializer['verified']:
        # If the attempt to verify was within a 5 minute time frame
        req.verified = False
        req.save()
        status = 200

    elif created - datetime.now() < timedelta(minutes=10) and not serializer['verified']:
        # Verification still in progress without timeout
        status = 202

    else:
        # 5 minute timeout has been reached
        status = 504

    return Response(status=status)


@api_view(['DELETE'])
def closeVerify(request):
    userQuery = request.query_params.get('requestId', None)

    # Does not have a query
    if not userQuery:
        return Response("The request id is required", status=400)

    # entry with the given requestId doesnt exist
    validAttempt = Request.objects.filter(requestId=userQuery).exists()
    if not validAttempt:
        return Response('No attempt matching the given request id.', status=404)

    req = Request.objects.get(requestId=userQuery)
    req.delete()

    return Response(status=200)



@api_view(['GET'])
def verification_successful(request):
    serverQuery = request.query_params.get('serverId', None)
    exchangeToken = request.query_params.get('et')

    if not serverQuery:
        return Response("The server id is required", status=400)

    if not exchangeToken:
        return Response("The exchange token is required", status=400)


    exchangeToken = urllib.parse.unquote(exchangeToken)

    exist = Server.objects.filter(serverId=serverQuery).exists()
    if not exist:
        return Response("The server could not be found. Please try again.", status=400)

    # Grabs the required data about the server to generate the unique humanID link
    servers = Server.objects.get(serverId=serverQuery)
    serializer = ServerSerializer(servers, many=False).data
    CLIENT_ID = serializer['clientId']
    CLIENT_SECRET = serializer['clientSecret']

    headers = {
        'client-id': CLIENT_ID,
        'client-secret': CLIENT_SECRET,
        'Content-Type': 'application/json'
    }

    # verify exchange token
    response = requests.post(
        'https://api.human-id.org/v1/server/users/exchange',
        headers=headers,
        json={"exchangeToken": exchangeToken.replace(" ", "+")}
    )

    resJson = response.json()
    if response.status_code != 200:
        # fail
        return Response(resJson, status=400)


    requestId = resJson['data']['requestId']
    humanUserId = resJson['data']['appUserId']
    # In case the request id doesnt exist
    reqExist = Request.objects.filter(requestId=requestId).exists()
    if not reqExist:
        return Response("The server returned a request id of requestId, which does not match our records.", status=400)

    # Check if the discord userId from the request matches the one from the humanID server
    # TODO: Check if every server creates different clientID
    associatedAccount = Person.objects.filter(humanUserId=humanUserId).exists()
    associatedAccountUser = Person.objects.filter(humanUserId=humanUserId).first()
    req = Request.objects.get(requestId=requestId)
    if associatedAccount and not verify(req.userId, associatedAccountUser.userId):
        return Response(
            'The provided credentials are already associated with another user in the server with the server id {}'.format(serverQuery),
            status=409
        )

    elif not associatedAccount:
        # Associate the humanID user with their discord id
        Person.objects.create(
            humanUserId=humanUserId,
            userId=req.userId,
        )

    # success
    req.verified = True
    req.save()

    return Response(status=200)
