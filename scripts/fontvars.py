#!/usr/bin/env fontforge
#
# Copyright (c) 2017, Sungsit Sawaiwan (https://sungsit.com | gibbozer [at] gmail [dot] com).
#
# This Font Software is licensed under the SIL Open Font License, Version 1.1 (OFL).
# You should have received a copy of the OFL License along with this file.
# If not, see http://scripts.sil.org/OFL
#

# This script will create SFD files from multi-layers source to prepare for later build process
# and it will only work with FontForge's Python extension.
import fontforge
import os
import subprocess
import shutil
import time
import datetime

# Font props
family = 'Boon'
version = '3.0'
foundry = 'FontUni'
os2_vendor = 'FUni'
foundry_url = 'https://fontuni.com/'
designer = 'Sungsit Sawaiwan'
designer_url = 'https://sungsit.com/'
license_url = 'http://scripts.sil.org/OFL'
copyright = 'Copyright 2013-2017, Sungsit Sawaiwan (https://fontuni.com | uni@fontuni.com). This Font Software is licensed under the SIL Open Font License, Version 1.1 (http://scripts.sil.org/OFL).'

# Building sources
feature_dir = 'sources/'
sources = ['sources/boon-master.sfd', 'sources/boon-master-oblique.sfd']
features = ['boon-roman', 'boon-oblique']
layers = ['300','400','500','600','700']

# Dir names
build_dir = 'fonts/'
if os.path.exists(build_dir):
  shutil.rmtree(build_dir)

sfd_dir = 'sfd/'
if os.path.exists(sfd_dir):
  shutil.rmtree(sfd_dir)

# Release packages
pkgs = ['otf', 'ttf', 'woff-otf', 'woff-ttf', 'woff2-otf', 'woff2-ttf']

# PS private values
def BlueValues(weight):
  switcher = {
    300: (-17, 0, 600, 617, 780, 797, 810, 827),
    400: (-18, 0, 600, 618, 780, 798, 810, 828),
    500: (-19, 0, 600, 619, 780, 799, 810, 829),
    600: (-20, 0, 600, 620, 780, 800, 810, 830),
    700: (-21, 0, 600, 621, 780, 801, 810, 831)
  }
  return switcher.get(weight)

def OtherBlues(weight):
  switcher = {
    300: (-222, -210),
    400: (-223, -210),
    500: (-224, -210),
    600: (-225, -210),
    700: (-226, -210)
  }
  return switcher.get(weight)

def StdHW(weight):
  switcher = {
    300: (52,),
    400: (64,),
    500: (79,),
    600: (98,),
    700: (110,)
  }
  return switcher.get(weight)

def StdVW(weight):
  switcher = {
    300: (67,),
    400: (85,),
    500: (113,),
    600: (137,),
    700: (160,)
  }
  return switcher.get(weight)

