#!/usr/bin/env python

import sys
import dbus
import os
import argparse
from mpd import MPDClient

# MPD
client = MPDClient()
client.connect("localhost", 6600)

parser = argparse.ArgumentParser()
parser.add_argument(
    '-t',
    '--trunclen',
    type=int,
    metavar='trunclen'
)
parser.add_argument(
    '-f',
    '--format',
    type=str,
    metavar='custom format',
    dest='custom_format'
)
parser.add_argument(
    '-p',
    '--playpause',
    type=str,
    metavar='play-pause indicator',
    dest='play_pause'
)
parser.add_argument(
    '--font',
    type=str,
    metavar='the index of the font to use for the main label',
    dest='font'
)
parser.add_argument(
    '--playpause-font',
    type=str,
    metavar='the index of the font to use to display the playpause indicator',
    dest='play_pause_font'
)
parser.add_argument(
    '-q',
    '--quiet',
    action='store_true',
    help="if set, don't show any output when the current song is paused",
    dest='quiet',
)

args = parser.parse_args()


def fix_string(string):
    # corrects encoding for the python version used
    if sys.version_info.major == 3:
        return string
    else:
        return string.encode('utf-8')


def truncate(name, trunclen):
    if len(name) > trunclen:
        name = name[:trunclen]
        name += '...'
        if ('(' in name) and (')' not in name):
            name += ')'
    return name



# Default parameters
output = fix_string(u'{play_pause} {artist}: {song}')
trunclen = 35
play_pause = fix_string(u'\u25B6,\u23F8') # first character is play, second is paused

label_with_font = '%{{T{font}}}{label}%{{T-}}'
font = args.font
play_pause_font = args.play_pause_font

quiet = args.quiet

# parameters can be overwritten by args
if args.trunclen is not None:
    trunclen = args.trunclen
if args.custom_format is not None:
    output = args.custom_format
if args.play_pause is not None:
    play_pause = args.play_pause

play_pause = play_pause.split(',')

def getMPDInfo():
    global play_pause
    state = client.status()["state"]
    
    if state == "play":
        playing = True

    elif state == "pause":
        playing = False

    else:
        playing = None

    song = client.currentsong()
    album = song["album"] if "album" in song.keys() else ""
    artist = song["artist"] if "album" in song.keys() else ""
    title = song["title"] if "album" in song.keys() else (os.path.basename(song["file"]) if "file" in song.keys() else "")

    return {"playing": playing, "artist": artist, "song": title, "album": album}


def getSpotifyInfo():
    try:
        session_bus = dbus.SessionBus()
        spotify_bus = session_bus.get_object(
            'org.mpris.MediaPlayer2.spotify',
            '/org/mpris/MediaPlayer2'
        )

        spotify_properties = dbus.Interface(
            spotify_bus,
            'org.freedesktop.DBus.Properties'
        )

        metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        state = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus').lower()

        if state == "playing":
            playing = True
        else:
            playing = False

        artist = fix_string(metadata['xesam:artist'][0]) if metadata['xesam:artist'] else ''
        song = fix_string(metadata['xesam:title']) if metadata['xesam:title'] else ''
        album = fix_string(metadata['xesam:album']) if metadata['xesam:album'] else ''

    except dbus.exceptions.DBusException:
        playing = None
        artist = song = album = str()

    finally:
        return {"playing": playing, "artist": artist, "song": song, "album": album}


def printInfo():
    global play_pause
    spotify_info = getSpotifyInfo()
    mpd_info = getMPDInfo()

    # Check if nothing is playing
    if spotify_info["playing"] is mpd_info["playing"] is None:
        print("Nothin's jammin', bud")
        return

    # Check if spotify is open and mpd is not playing
    if spotify_info["playing"] is not None and not mpd_info["playing"]:
        playing, artist, song, album = spotify_info.values()
        
        if playing:
            play_pause_action = "sp pause"
        else:
            play_pause_action = "sp play"

        mpd = False

    else:
        playing, artist, song, album = mpd_info.values()
        play_pause_action = "mpc toggle"
        mpd = True

    play_pause = play_pause[int(not playing)]

    if play_pause_font:
        play_pause = label_with_font.format(font=play_pause_font, label=play_pause)
    
    play_pause = f"%{{A1:{play_pause_action}:}}{play_pause}%{{A}}"

    # Handle main label

    if (quiet and status == 'Paused') or (not artist and not song and not album):
        print('')
    else:
        if font:
            artist = label_with_font.format(font=font, label=artist)
            song = label_with_font.format(font=font, label=song)
            album = label_with_font.format(font=font, label=album)

        # Add 4 to trunclen to account for status symbol, spaces, and other padding characters
        print(output.format(artist=artist, 
                                     song=song, 
                                     play_pause=play_pause, 
                                     album=album) + f" on {'MPD' if mpd else 'Spotify'}")


printInfo()
