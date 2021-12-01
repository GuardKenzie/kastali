#! /bin/sh
#
# polybar-fuckery.sh
# Copyright (C) 2021 kenzie <kenzie@willowroot>
#
# Distributed under terms of the MIT license.
#

xwininfo -name bspwm -wm | grep "Window id" | cut -d" " -f4 | xargs -I {} xdo above -N Polybar -t {}
