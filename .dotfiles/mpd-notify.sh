#!/bin/bash
while :
do
    file=`mpc -f "$HOME/Music/%file%" current --wait`

    $HOME/.dotfiles/nowplaying "$file"
done
