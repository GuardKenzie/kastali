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
        play_pause = play_pause[0]
    elif state == "pause":
        play_pause = play_pause[1]
    else:
        play_pause = str()

    song = client.currentsong()
    album = song["album"] if "album" in song.keys() else ""
    artist = song["artist"] if "album" in song.keys() else ""
    title = song["title"] if "album" in song.keys() else os.path.basename(song["file"])

    return play_pause, artist, title, album


def printInfo(play_pause, artist, song, album, mpd=True):
    if play_pause_font:
        play_pause = label_with_font.format(font=play_pause_font, label=play_pause)

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
    status = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
    mpd_status = client.status()["state"]

    if status == 'Playing':
        play_pause = play_pause[0]
        use_mpd = False
    elif status == 'Paused' and mpd_status != "play":
        play_pause = play_pause[1]
        use_mpd = False
    elif status == 'Paused' and mpd_status == "play":
        play_pause = play_pause[0]
        use_mpd = True
    elif mpd_status == "play":
        use_mpd = True
        play_pause = play_pause[0]
    elif mpd_status == "pause":
        play_pause = play_pause[1]
        use_mpd = True
    else:
        use_mpd = False
        raise dbus.exceptions.DBusException

    if use_mpd:
        play_payse, album, artist, song = getMPDInfo()
    else:
        artist = fix_string(metadata['xesam:artist'][0]) if metadata['xesam:artist'] else ''
        song = fix_string(metadata['xesam:title']) if metadata['xesam:title'] else ''
        album = fix_string(metadata['xesam:album']) if metadata['xesam:album'] else ''

    printInfo(play_pause, artist, song, album, use_mpd)



except Exception as e:
    if isinstance(e, dbus.exceptions.DBusException):
        if client.status()["state"] != "stop":
            play_pause, artist, song, album = getMPDInfo()
            printInfo(play_pause, artist, song, album, True)
        else:
            print("Nothin's jammin', bud")
    else:
        print(e)
