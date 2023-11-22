# Author: Erica Ferrua
# 2023-11-19 15:54
# Filename: spotify.py 

import dbus

session_bus = dbus.SessionBus()

spotify_bus = session_bus.get_object(
    "org.mpris.MediaPlayer2.spotify",
    "/org/mpris/MediaPlayer2"
)

spotify_properties = dbus.Interface(
    spotify_bus,
    "org.freedesktop.DBus.Properties"
)

metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

print(metadata)
