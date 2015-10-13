#!/usr/bin/env fontforge
#
# Copyright (c) 2015, Sungsit Sawaiwan (https://sungsit.com | gibbozer [at] gmail [dot] com).
#
# This Font Software is licensed under the SIL Open Font License, Version 1.1 (OFL).
# You should have received a copy of the OFL License along with this file.
# If not, see http://scripts.sil.org/OFL
#

# This script will only work with FontForge's Python extension.
import fontforge

# Predifined vars
source = 'sources/boon-master.sfd'

# I just can't find better ways to list all anchors yet ...
anchors = [
  'ThaiBelow.mark',
  'ThaiAbove.mark',
  'ThaiTone.mark',
  'ThaiExtendedAbove.mkmk',
  'ThaiExtendedAbove.left.mkmk',
  'ThaiExtendedBelow.mkmk',
  'LatinBelow.mark',
  'LatinAbove.mark',
  'LatinCedilla.mark',
  'LatinOgonek.mark',
  'LatinBelow.mkmk',
  'LatinAbove.mkmk'
]

font = fontforge.open(source)

for anchor in anchors:
  font.removeAnchorClass(anchor)

font.save()
font.close()
