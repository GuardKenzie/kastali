alias em='emacsclient -c'
alias emt='emacsclient -t'

# Commands redefinition
alias clear='clear;neofetch'

function icat
    convert $argv[1] -resize 600x png:- | kitty +kitten icat --align left $argv[2..-1]
end
