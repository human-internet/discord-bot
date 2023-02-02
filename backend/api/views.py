from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pyshorteners as ps
from . serializers import *
import requests
from datetime import datetime, timedelta


@api_view(['GET'])
def getRedirect(request):
    # TODO pass in hashed version of server ID to identify the clientID and secret to use?
    idQuery = request.query_params.get('serverId', None) # unhash here?
    userQuery = request.query_params.get('userId', None) # unhash here?

    if not idQuery:
        return HttpResponse(status=500)

    # Grabs the required data about the server to generate the unique humanID link
    servers = Server.objects.get(serverId=idQuery)
    serializer = ServerSerializer(servers, many=False).data
    CLIENT_ID = serializer['clientId']
    cs = serializer['clientSecret']
    headers = {
        'client-id': CLIENT_ID,
        'client-secret': cs ,
        'Content-Type' : 'application/json'
    }
    json = {
        'userId': userQuery,
    }

    response = requests.post(
        'https://core.human-id.org/v0.0.3/server/users/web-login',
        headers=headers,
        json=json
    )

    return_url = response.json()['data']['webLoginUrl']
    short_url = ps.Shortener().tinyurl.short(return_url)

    # Generate the link and send it back
    return Response(short_url)


@api_view(['PUT'])
def verifyAttempt(request):
    userQuery = request.query_params.get('userId', None) # unhash here?

    if not userQuery:
        return HttpResponse(status=500)

    duplicate = Person.objects.filter(userId=userQuery).exists()
    if duplicate:
        # If the user has a duplicate entry, just update the created time
        user = Person.objects.get(userId=userQuery)
        user.created = timezone.now()
        user.save()
        return Response('done')

    else:
        # Create an entry representing the user trying to verify
        Person.objects.create(
            userId = userQuery,
            created = timezone.now()
        )

        return Response('done')


@api_view(['DELETE'])
def closeVerify(request):
    userQuery = request.query_params.get('userId', None) # unhash here?

    if not userQuery:
        return HttpResponse(status=500)

    validAttempt = Person.objects.filter(userId=userQuery).exists()
    if not validAttempt:
        return HttpResponse(status=404)

    user = Person.objects.get(userId=userQuery)
    status = None
    serializer = PersonSerializer(user, many=False).data
    created = (datetime.fromisoformat(serializer['created']
        .replace('T', ' ')
        .replace('Z', '')))


    if created - datetime.now() < timedelta(minutes=30):
        # If the attempt to verify was within a 30 minute time frame
        status = 200

    else:
        # Create an entry representing the user trying to verify
        status = 504

    user.delete()
    return HttpResponse(status=status)
