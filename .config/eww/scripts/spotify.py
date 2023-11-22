#!/bin/python
import dbus
from argparse import ArgumentParser
import json
import math
import os
import time
import sys
from subprocess import check_output, CalledProcessError, DEVNULL

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

info_parser = subparsers.add_parser("time")
info_parser.add_argument("--monitor", action="store_true")

args = parser.parse_args()

# Spotify
session_bus = dbus.SessionBus()

def getTime():
    playerctl_length   = ["playerctl", "metadata", "-f", "{{mpris:length}}"]
    playerctl_position = ["playerctl", "position"]

    mpc = ["mpc", "status", "'%totaltime%',%currenttime%,%percenttime%'"]

    try:
        length   = float(check_output(playerctl_length, stderr=DEVNULL).decode())
        position = float(check_output(playerctl_position, stderr=DEVNULL).decode())

        length /= 1_000_000

        percent = int(100 * position / length)

        length = f"{int(length // 60)}:{int(length % 60):02d}"
        position = f"{int(position // 60)}:{int(position % 60):02d}"


    except (ValueError, CalledProcessError, ZeroDivisionError):
        try:
            length, position, pct = check_output(mpc, stderr=DEVNULL).decode().split(",")
            length = length.replace("'","")
            percent = int(pct.replace(" ", "0")[:-3])

        except (ValueError, CalledProcessError):
            length = position = "0:00"
            percent = 0


    return {
        "length": length, 
        "position": position, 
        "percent": percent
    }



def getArt():
    return metadata.get("mpris:artUrl")

def getMPDInfo():
    status = client.status()
    song   = client.currentsong()

    if status["state"] == "stop":
        return {"stop": True}


    album = song["album"] if "album" in song.keys() else ""
    artist = song["artist"] if "artist" in song.keys() else ""
    title = song["title"] if "title" in song.keys() else os.path.basename(song["file"])

    album_art = f"/tmp/album{md5(song['file'].encode()).hexdigest()}.jpg"

    if not os.path.exists(album_art):
        with open(album_art, "wb+") as f:
            f.write(client.albumart(song["file"])["binary"])

    return {
        "stop": False,
        "status": status["state"],
        "art": album_art,
        "title": title,
        "album": album,
        "artist": artist,
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
    play = spotify_properties.Get(
        "org.mpris.MediaPlayer2.Player", 
        "PlaybackStatus"
    )

    return {
        "stop": play == "Paused",
        "state": play.lower(),
        "art": metadata.get("mpris:artUrl"),
        "title": metadata.get("xesam:title"),
        "album": metadata.get("xesam:album"),
        "artist": ", ".join(metadata.get("xesam:artist")),
        "service": "Spotify"
    }


def getInfo():
    global spotify_bus
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

            if info != new_info:
                sys.stdout.write(json.dumps(new_info).strip())
                sys.stdout.write("\n")
                sys.stdout.flush()
                info = new_info

            time.sleep(2)


    else:
        res = getInfo()
        print(json.dumps(res))

elif args.action == "time":
    if args.monitor:
        old_time = None

        while True:
            new_time = getTime()

            if old_time != new_time:
                sys.stdout.write(json.dumps(new_time).strip())
                sys.stdout.write("\n")
                sys.stdout.flush()
                old_time = new_time

            time.sleep(0.1)


    else:
        res = getTime()
        print(json.dumps(res))
