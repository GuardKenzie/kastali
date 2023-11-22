#!/bin/python
import dbus
from argparse import ArgumentParser
import json
import math
import os
import time
import sys

from mpd import MPDClient

from hashlib import md5

# MPD
client = MPDClient()
client.connect("localhost", 6600)

# Args
parser = ArgumentParser()
subparsers = parser.add_subparsers(dest="action")

subparsers.add_parser("art")

info_parser = subparsers.add_parser("info")
info_parser.add_argument("--monitor", action="store_true")


args = parser.parse_args()

# Spotify
session_bus = dbus.SessionBus()


def getArt():
    return metadata.get("mpris:artUrl")

def getMPDInfo():
    status = client.status()
    song   = client.currentsong()

    if status["state"] == "stop":
        return {"stop": True}


    current_time = float(status["elapsed"])
    track_length = float(status["duration"])

    position = 100 * current_time / track_length

    current_time_seconds = math.floor(current_time % 60)
    current_time_minutes = math.floor(current_time // 60)

    track_length_seconds = math.floor(track_length % 60)
    track_length_minutes = math.floor(track_length // 60)

    album = song["album"] if "album" in song.keys() else ""
    artist = song["artist"] if "artist" in song.keys() else ""
    title = song["title"] if "title" in song.keys() else os.path.basename(song["file"])

    album_art = f"/tmp/album{md5(song['file'].encode()).hexdigest()}.jpg"

    if not os.path.exists(album_art):
        with open(album_art, "wb+") as f:
            f.write(client.albumart(song["file"])["binary"])

    return {
        "stop": False,
        "art": album_art,
        "title": title,
        "album": album,
        "artist": artist,
        "progress": position,
        "current_time": f"{current_time_minutes}:{current_time_seconds:02d}",
        "length": f"{track_length_minutes}:{track_length_seconds:02d}",
        "service": "MPD"
    }


spotify_bus = None
spotify_properties = None

def getSpotifyInfo():
    global spotify_bus
    global spotify_properties

    if spotify_bus is None:
        spotify_bus = session_bus.get_object(
            "org.mpris.MediaPlayer2.spotify",
            "/org/mpris/MediaPlayer2"
        )

        spotify_properties = dbus.Interface(
            spotify_bus,
            "org.freedesktop.DBus.Properties"
        )

    metadata = spotify_properties.Get(
        "org.mpris.MediaPlayer2.Player", 
        "Metadata"
    )

    current_time = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Position")
    track_length = metadata.get("mpris:length")
    position = 100 * current_time / track_length

    current_time /= 1_000_000
    track_length /= 1_000_000

    current_time_seconds = math.floor(current_time % 60)
    current_time_minutes = math.floor(current_time // 60)

    track_length_seconds = math.floor(track_length % 60)
    track_length_minutes = math.floor(track_length // 60)

    return {
        "stop": False,
        "art": metadata.get("mpris:artUrl"),
        "title": metadata.get("xesam:title"),
        "album": metadata.get("xesam:album"),
        "artist": ", ".join(metadata.get("xesam:artist")),
        "progress": position,
        "current_time": f"{current_time_minutes}:{current_time_seconds:02d}",
        "length": f"{track_length_minutes}:{track_length_seconds:02d}",
        "service": "Spotify"
    }


def getInfo():
    try:
        return getSpotifyInfo()
    except dbus.exceptions.DBusException:
        spotify_bus = None
        return getMPDInfo()


        
if args.action == "art":
    print(getArt())

elif args.action == "info":
    if args.monitor:
        info = None

        while True:
            new_info = getInfo()

            if new_info != info:
                sys.stdout.write(json.dumps(new_info).strip())
                sys.stdout.flush()
                info = new_info

            time.sleep(1)
            sys.stdout.write("\n")

    else:
        res = getInfo()
        print(json.dumps(res))
