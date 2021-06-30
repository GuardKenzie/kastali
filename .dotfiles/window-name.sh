#! /bin/sh
#
# window-name.sh
# Copyright (C) 2021 kenzie <kenzie@willowroot>
#
# Distributed under terms of the MIT license.
#


node=`bspc query -N focused -n focused`
name=`xprop -id $node WM_NAME | cut -d \" -f2`

echo $name
