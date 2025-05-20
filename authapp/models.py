from django.db import models
from django.conf import settings
from supabase import create_client, Client
import os


class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    audio_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
