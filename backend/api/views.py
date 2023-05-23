from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pyshorteners as ps
from .serializers import *
import requests
import urllib.parse
import environ

from datetime import datetime, timedelta

env = environ.Env()


@api_view(['GET'])
def getRedirect(request):
    serverQuery = request.query_params.get('serverId', None)  # unhash here?

    # Does not have a query
    if not serverQuery:
        return Response("The server id is required", status=400)

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
    userQuery = request.query_params.get('requestId', None)  # unhash here?

    # Does not have a query
    if not userQuery:
        return Response("The user id is required", status=400)

    duplicate = Person.objects.filter(requestId=userQuery).exists()
    if duplicate:
        # If the user has a duplicate entry, just update the created time
        user = Person.objects.get(requestId=userQuery)
        user.created = timezone.now()
        user.verified = False
        user.save()
        return Response('done')

    else:
        # Create an entry representing the user trying to verify
        Person.objects.create(
            requestId=userQuery,
            created=timezone.now(),
            verified=False,
        )

        return Response('done')


@api_view(['GET'])
def checkVerify(request):
    userQuery = request.query_params.get('requestId', None)  # unhash here?
    # Does not have a query
    if not userQuery:
        return Response("The user id is required", status=400)

    # entry with the given requestId doesnt exist
    validAttempt = Person.objects.filter(requestId=userQuery).exists()
    if not validAttempt:
        return HttpResponse(status=404)

    user       = Person.objects.get(requestId=userQuery)
    status     = None
    serializer = PersonSerializer(user, many=False).data
    created    = (datetime.fromisoformat(serializer['created']
                                      .replace('T', ' ')
                                      .replace('Z', '')))

    if created - datetime.now() < timedelta(minutes=5) and serializer['verified']:
        # If the attempt to verify was within a 5 minute time frame
        user = Person.objects.get(requestId=userQuery)
        user.verified = False
        user.save()
        status = 200

    elif created - datetime.now() < timedelta(minutes=5) and not serializer['verified']:
        # Verification still in progress without timeout
        status = 202

    else:
        # 5 minute timeout has been reached
        status = 504

    return HttpResponse(status=status)


@api_view(['DELETE'])
def closeVerify(request):
    userQuery = request.query_params.get('requestId', None)  # unhash here?

    # Does not have a query
    if not userQuery:
        return HttpResponse(status=500)

    # entry with the given requestId doesnt exist
    validAttempt = Person.objects.filter(requestId=userQuery).exists()
    if not validAttempt:
        return HttpResponse(status=404)

    user = Person.objects.get(requestId=userQuery)
    user.delete()

    return HttpResponse(status=200)



@api_view(['GET'])
def verification_successful(request):
    idQuery = request.query_params.get('serverId', None)  # unhash here?
    exchangeToken = request.query_params.get('et')

    if not serverQuery:
        return Response("The server id is required", status=400)

    if not exchangeToken:
        return Response("The exchange token is required", status=400)


    exchangeToken = urllib.parse.unquote(exchangeToken)
    identifier = '{}-{}'.format(userQuery, serverQuery)

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

    # bug catch
    # avoids recalling with the same exchange token
    if (user.verified):
        return HttpResponse(status=200)

    # verify exchange token
    response = requests.post(
        'https://api.human-id.org/v1/server/users/exchange',
        headers=headers,
        json={"exchangeToken": exchangeToken.replace(" ", "+")}
    )

    resJson = response.json()

    if response.status_code == 200:
        requestId = resJson['data']['requestId']

        # success
        user = Person.objects.get(requestId=requestId)
        user.verified = True
        user.save()

        return HttpResponse(status=200)
    else:
        # fail
        return Response(resJson, status=400)