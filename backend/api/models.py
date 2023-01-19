from django.db import models

class Server(models.Model):
    serverId = models.TextField(null=False)
    channelName = models.TextField(null=False)
    roleName = models.TextField(null=False)
    clientId = models.TextField(null=False)
    clientSecret = models.TextField(null=False)

    def __str__(self):
        return self.serverId
    

class Person(models.Model):
    userId = models.TextField(null=False)
    name = models.TextField(null=False)

    def __str__(self):
        return self.userId
