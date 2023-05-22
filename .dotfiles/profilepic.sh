#! /bin/sh
#
# profilepic.sh
# Copyright (C) 2023 kenzie <kenzie@willowroot>
#
# Distributed under terms of the MIT license.
#


if [ "$#" -ne 1 ]; then
    echo "No arguments passed!"
    exit 1
fi

user=$(whoami)

echo "Converting $1 to 96x96 and storing in /tmp/$user.png..."
convert -geometry 96x96 $1 /tmp/$user.png

echo "Applying profile picture"
sudo mv /tmp/$user.png /var/lib/AccountsService/icons/$user
