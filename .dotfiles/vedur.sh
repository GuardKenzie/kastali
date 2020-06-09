#!/bin/sh

stat=0
count=0

while [[ $stat == 0 && $count < 60 ]]
do
    vedur="$(curl -s wttr.in/?0?q?T  | awk '/°(C|F)/ {printf $(NF-1) $(NF) " ("a")"} /,/ {a=$1}' | sed 's/\.\./-/g' | sed 's/,//g')"
    if [[ $vedur == '' ]]
    then
        echo Could not get wttr.in > $HOME/.dotfiles/vedur-nuna
        sleep 1
        count=$((count+1))
    else
        echo $vedur > $HOME/.dotfiles/vedur-nuna
        stat=1
    fi
done

