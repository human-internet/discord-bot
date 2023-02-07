from django.db import models

class Server(models.Model):
    serverId = models.TextField(null=False)
    channelName = models.TextField(null=False)
    roleName = models.TextField(null=False)
    clientId = models.TextField(null=False)
    clientSecret = models.TextField(null=False)

    def __str__(self):
        return self.serverId

# When the user does /verify, store user id and the time they tried to verify into the db
# if the link is used, check if the time between the stored time and now is below a set time. If it is, remove entry from the table and verify user
# Otherwise, send timeout message and remove their entry in the db
class Person(models.Model):
    userId = models.TextField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.userId
