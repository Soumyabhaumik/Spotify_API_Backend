from .models import Song
from django.core.serializers import serialize
import json


def serialize_song(song):
    """
    Serialize a single Song object to a dictionary.
    """
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "audio_url": song.audio_url,
        "image_url": song.image_url,
    }


def serialize_song_list(songs):
    """
    Serialize a list of Song objects to a list of dictionaries.
    """
    return [serialize_song(song) for song in songs]
