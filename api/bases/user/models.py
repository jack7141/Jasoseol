import uuid

from django.db import models

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    username = models.CharField(max_length=100, unique=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username