#! /bin/sh
#
# setup-trilli-kb.sh
# Copyright (C) 2021 kenzie <kenzie@willowroot>
#
# Distributed under terms of the MIT license.
#

XKB_SYMBOLS="/usr/share/X11/xkb/symbols/us"

echo >> $XKB_SYMBOLS
cat /home/kenzie/.dotfiles/trillikb >> $XKB_SYMBOLS

su kenzie -c "setxkbmap us -variant trilli"
