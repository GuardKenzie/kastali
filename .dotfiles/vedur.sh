#!/bin/sh
echo "$(curl -s wttr.in/?0?q?T  | awk '/°(C|F)/ {printf $(NF-1) $(NF) " ("a")"} /,/ {a=$1}' | sed 's/\.\./-/g' | sed 's/,//g')" > $HOME/.dotfiles/vedur-nuna

