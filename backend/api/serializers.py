from rest_framework.serializers import ModelSerializer
from . models import *

class ServerSerializer(ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'

class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class RequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
