#!/bin/sh
vedur="$(curl -s wttr.in/?0?q?T  | awk '/°(C|F)/ {printf $(NF-1) $(NF) " ("a")"} /,/ {a=$1}' | sed 's/\.\./-/g' | sed 's/,//g')"

if [[ $vedur == '' ]]
then
    echo Could not get wttr.in > $HOME/.dotfiles/vedur-nuna
else
    echo $vedur > $HOME/.dotfiles/vedur-nuna
fi

