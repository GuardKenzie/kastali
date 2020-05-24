#! /bin/sh
#
# texmode.sh
# Copyright (C) 2020 mononoke <mononoke@ookami-zoku>
#
# Distributed under terms of the MIT license.
#


if [ $(bspc config -d focused window_gap) -eq 5 ]; then \
            bspc config -d focused left_padding 5; \
            bspc config -d focused right_padding 5; \
            bspc config -d focused top_padding 5; \
            bspc config -d focused bottom_padding 5; \
            bspc config -d focused window_gap 0; \
            bspc config -d focused border_width 0; \
        else \
            bspc config -d focused left_padding 0; \
            bspc config -d focused right_padding 0; \
            bspc config -d focused top_padding 0; \
            bspc config -d focused bottom_padding 0; \
            bspc config -d focused window_gap 5; \
            bspc config -d focused border_width 2; \
        fi;
