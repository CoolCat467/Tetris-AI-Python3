#!/usr/bin/env python3
# Install sdl-config for ubuntu
# -*- coding: utf-8 -*-

__title__ = 'Install sdl-config'
__author__ = 'CoolCat467'
__version__ = '0.0.0'
__ver_major__ = 0
__ver_minor__ = 0
__ver_patch__ = 0

import os

#commands = ['hg clone https://hg.libsdl.org/SDL SDL',
#            'cd SDL',
#            'mkdir build',
#            'cd build',
#            '../configure',
#            'make',
#            'sudo make install']
#
#for command in commands:
out = os.system('sudo apt-get install libsdl2-2.0 libsdl2-dev')
if out != 0:
    exit(1)
#        break
exit(0)
