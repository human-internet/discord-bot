from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . serializers import *


@api_view(['GET'])
def getRedirect(request):
    return Response('test')


@api_view(['GET'])
def getServers(request):
    servers = Server.objects.all()
    serializer = ServerSerializer(servers, many=True)
    return Response(serializer.data)

