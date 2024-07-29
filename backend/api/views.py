from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, QueryDict, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pyshorteners as ps
from .serializers import *
import requests
import urllib.parse
import environ
import json
from hashlib import blake2b
from hmac import compare_digest
import json
from datetime import datetime, timedelta

env = environ.Env()

# TODO TODO TODO SHOULD BE SECRET
SECRET_KEY = b'pseudorandomly generated server secret key'
AUTH_SIZE = 16

def sign(userId):
    print("info", AUTH_SIZE, SECRET_KEY)
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
    h.update(userId)
    return h.hexdigest().encode('utf-8')

def verify(userId, storedId):
    return compare_digest(userId, storedId)

# This function un-verifies a user in the database.
# It deletes the entry for the user with the given discord_id.
@api_view(['DELETE'])
def unverify_user(request):
    print("unverify_user called")
    user = request.query_params.get('userId')
    print("Unverify user:", user) 
    user_id = sign(bytes(str(user), 'utf-8'))
    server_id = request.query_params.get('serverId')
    print("Unverify signed ID:", user_id)
    
    if not user_id or not server_id:
        return Response("The user id and server id are required", status=400)
    
    user_entry = Person.objects.filter(userId=user_id, serverId=server_id).first()
    
    if user_entry:
        user_entry.delete()
        return JsonResponse({'status': 'success'}, status=200)
    
    return JsonResponse({'status': 'failed'}, status=404)


""" 
1. Get the parameters sent in the body of the request
2. Check that the parameters are valid (i.e. not empty)
3. Check that the serverId is not already in the database
4. If the serverId is not already in the database, insert it into the database
5. Return an appropriate response to the request 
"""

@api_view(['PUT'])
def addServer(request):
    print("addServer called")
    body = json.loads(request.body)
    if 'serverId' not in body:
        return Response("The server id is required", status=400)
    elif 'clientId' not in body:
        return Response("The client id is required", status=400)
    elif 'secret' not in body:
        return Response("The client secret is required", status=400)
    elif 'clientEmail' not in body:
        return Response("The client email is required", status=400)

    clientEmail = body['clientEmail']
    serverId = body['serverId']
    clientId = body['clientId']
    clientSecret = body['secret']

    duplicate = Server.objects.filter(serverId=serverId).exists()
    if duplicate:
        return Response("This server already has an associated credential", status=400)
    # Create an entry representing the user trying to verify; we replace the client id/secret if the request sender email is the same
    Server.objects.create(
        serverId=serverId,
        clientId=clientId,
        clientSecret=clientSecret,
        clientEmail=clientEmail
    )
    return HttpResponse(status=200)

"""
1. Grabs the serverId from the request
2. Checks if the serverId exists
3. Grabs the clientId and clientSecret from the database
4. Generate the weblogin url
5. Generate the short url
6. Send back the short url and the requestId to the frontend 
"""
@api_view(['GET'])
def getRedirect(request):
    print("getRedirect called")
    serverQuery = request.query_params.get('serverId', None)

    # Case: does not have a query
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
        env.get_value("PYTHON_WEB_LOGIN_URL"),
        headers=headers,
    )
    # get the response mes

    if response.status_code != 200:
        return Response("Unable to generate url. Please double check your credentials", status=403)

    resJson = response.json()['data']
    return_url = resJson['webLoginUrl']
    requestId = resJson['requestId']
    short_url = ps.Shortener().tinyurl.short(return_url)
    print(f'Server ID received: {serverQuery}')  # Print the serverId for debugging

    # Generate the link and send it back
    return Response({
        'url': short_url,
        'requestId': requestId,
    })

""" 
1. Get the user id and request id from the request parameters
2. Check if the user has a duplicate entry
3. If the user has a duplicate entry, update the created time of the duplicate entry
4. If the user does not have a duplicate entry, create a new entry
5. Return a 200 response if successfully created/updated
"""
@api_view(['PUT'])
def verifyAttempt(request):
    print("verifyAttempt called")
    userQuery = request.query_params.get('userId', None)
    reqQuery = request.query_params.get('requestId', None)
    serverId = request.query_params.get('serverId', None)

    print("verify user:", userQuery)
    signed_user = sign(bytes(str(userQuery), 'utf-8'))
    print("Verify signed ID", signed_user)
    
    # Case: request does not have a userId
    if not userQuery:
        return Response("The user id is required", status=400)

    if not reqQuery:
        return Response("The request id is required", status=400)

    if not serverId:
        return Response("The server id is required", status=400)

    duplicate = Request.objects.filter(requestId=reqQuery).exists()
    if duplicate:
        # If the user has a duplicate entry, just update the created time
        req = Request.objects.get(requestId=reqQuery)
        req.created  = timezone.now()
        req.userId   = sign(bytes(str(userQuery), 'utf-8'))
        req.verified = False
        req.serverId = serverId
        req.save()

    else:
        # Create an entry representing the user trying to verify
        Request.objects.create(
            requestId=reqQuery,
            userId=sign(bytes(str(userQuery), 'utf-8')),
            #implemented new field
            serverId = serverId,
            created=timezone.now(),
            verified=False,
        )
    
    serverId = request.query_params.get('serverId', None)
    print(f'Server ID received: {serverId}')  # Print the serverId for debugging

    return Response(status=200)


@api_view(['GET'])
def checkVerify(request):
    print("checkVerify called")
    # TODO: Check if the Discord Server ID is also present
    serverId = request.query_params.get('serverId', None)
    print(f'Server ID received: {serverId}')  # Print the serverId for debugging

    userQuery = request.query_params.get('requestId', None)
    # Case: requestID is not present
    if not userQuery:
        return Response("The user id is required", status=400)

    # Check if entry with the given requestId exists
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
        req.verified = True
        req.save()
        status = 200

    elif created - datetime.now() < timedelta(minutes=10) and not serializer['verified']:
        # Verification still in progress without timeout
        status = 202

    else:
        # 5 minute timeout has been reached
        status = 504

    return Response(status=status)

"""
1. Get the requestId from the query parameters in the request
2. If there is no query parameter, return a 400 error
3. If there is a query parameter, check if there is an entry in the database with that requestId
4. If there is no entry, return a 404 error
5. Otherwise, delete the entry from the database
6. Return a 200 status code 
"""
@api_view(['DELETE'])
def closeVerify(request):
    print("closeVerify called")
    userQuery = request.query_params.get('requestId', None)

    # Does not have a query
    if not userQuery:
        return Response("The request id is required", status=400)

    # Check if entry with the given requestId exists
    validAttempt = Request.objects.filter(requestId=userQuery).exists()
    if not validAttempt:
        return Response('No attempt matching the given request id.', status=404)

    req = Request.objects.get(requestId=userQuery)
    req.delete()

    return Response(status=200)

# Check if a particular humanID user is already associated with a discord user, within the scope of the bot server
def check_server_duplicate(humanUserId, serverQuery):
    print("check_server_duplicate called")
    associatedAccount = Person.objects.filter(humanUserId=humanUserId).exists()
    if associatedAccount:
        associatedCredentialList = Person.objects.filter(humanUserId=humanUserId)
        for associatedCredential in associatedCredentialList:
            if associatedCredential.serverId == serverQuery:
                return True
        return False
    else:
        return False


"""
1. Checks if the serverId exists in the Server table.
2. Checks if the exchange token is valid by sending a POST request to the humanID server
3. Checks if the requestId of the exchange token matches our records
4. Checks if the discord userId from the request matches the one from humanID
5. Checks if a particular humanID user is already associated with a discord user, within the whole scope of the bot server
6. If all the above conditions are met, then the humanID user is associated with their discord id
7. The request is marked as verified 
"""
@api_view(['GET'])
def verification_successful(request):
    print("verification_successful called")
    serverQuery = request.query_params.get('serverId', None)
    exchangeToken = request.query_params.get('et')
    print(f"Server ID received: {serverQuery}")  # Print the serverId for debugging
    print(f"Exchange token received: {exchangeToken}")  # Print the exchange token for debugging
    
    if not serverQuery:
        return Response("The server id is required", status=400)

    if not exchangeToken:
        return Response("The exchange token is required", status=400)
    

    exchangeToken = urllib.parse.unquote(exchangeToken)
    serverExist = Server.objects.filter(serverId=serverQuery).exists()
    if not serverExist:
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

    # 3. Checks if the requestId of the exchange token matches our records
    reqExist = Request.objects.filter(requestId=requestId).exists()
    if not reqExist:
        message = "The server returned a request id of {}, which does not match our records.".format(requestId)
        return Response(message, status=400)
    else:
        req = Request.objects.get(requestId=requestId)
        server_duplicate = check_server_duplicate(humanUserId, serverQuery)
        if server_duplicate:
            return Response(
                'The provided credentials are already associated with another user in the server {}'
                .format(serverQuery), status=409)
            # No Discord Server - humanID repeat, putting new person in database
        Person.objects.create(
            humanUserId=humanUserId,
            userId=req.userId,
            serverId=serverQuery,
        )
        req.verified = True
        req.save()     
        # success
        return Response(status=200)
