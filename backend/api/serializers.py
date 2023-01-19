from rest_framework.serializers import ModelSerializer
from . models import *

class ServerSerializer(ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'
