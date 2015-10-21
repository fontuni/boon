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
import os
import subprocess

# Predifined vars
family = 'Boon'
version = '1.0-beta2'
source = 'sources/boon-master.sfd'
layers = ['300', '400', '500', '600', '700']
copyright =  'Copyright 2013-2015, Sungsit Sawaiwan (https://fontuni.com | uni@fontuni.com). This Font Software is licensed under the SIL Open Font License, Version 1.1 (http://scripts.sil.org/OFL).'
features = ['boon-normal']
feature_dir = 'sources/'
build_dir = 'fonts/'
unhinted_dir = 'fonts/unhinted/'

def printFontInfo(fontfile):
  font = fontforge.open(fontfile)
  print('\nFont File: ' + fontfile)
  print('Family Name: ' + font.familyname)
  print('Font Name: ' + font.fontname)
  print('Full Name: ' + font.fullname)
  print('Font Weight: ' + font.weight)
  print('OS2 Weight: ' + str(font.os2_weight))
  print('Italic Angle: ' + str(font.italicangle))
  print('Font Version: ' + font.version)
  print('Font Copyright: ' + font.copyright)
  font.close()

def ttfHint(unhinted,hinted):
  subprocess.call([
    'ttfautohint',
    '--default-script=thai',
    '--fallback-script=latn',
    '--strong-stem-width=gGD',
    '--hinting-range-min=8',
    '--hinting-range-max=50',
    '--hinting-limit=200',
    '--increase-x-height=13',
    '--no-info',
    '--verbose',
    unhinted,
    hinted
  ])

def ttf2Woff(ttf,woff,genflags):
  font = fontforge.open(ttf)
  font.generate(woff, flags=genflags)
  font.close()

def buildFont(source,family):

  # prepare master
  font = fontforge.open(source)
  font.familyname = family
  font.version = version
  font.copyright = copyright
  font.save()

  # loop through each layer & save it as sfd files
  # then generate ttf, autohint & make woff + woff2
  for layer in layers:

    layername = font.layers[layer].name
    subfamily = layername

    font.weight = layername
    font.os2_weight = int(layername)
  
    font.italicangle = 0.0
      
    if layername.endswith('Oblique'):
      subfamily += '-Oblique'
      font.italicangle = -9.0

    font.fontname = family + '-' + subfamily
    font.fullname = font.fontname.replace('-',' ')

    tempsfd = 'sources/'+ font.fontname +'-temp.sfd'
    font.save(tempsfd)

    temp = fontforge.open(tempsfd)

    if temp.fullname.endswith('Oblique'):
      temp.mergeFeature(feature_dir + features[1] + '.fea')
    else:
      temp.mergeFeature(feature_dir + features[0] + '.fea')

    genflags  = ('opentype', 'PfEd-lookups', 'no-hints')
    ttfunhinted = unhinted_dir + font.fontname + '-unhinted.ttf'

    # generate unhinted ttf
    temp.generate(ttfunhinted, flags=genflags, layer = layername)
    print(font.fullname, 'TTF instance generated.')

    temp.close()
    subprocess.call(['rm',tempsfd])

    ttf = build_dir + font.fontname + '.ttf'
    woff = build_dir + font.fontname + '.woff'

    # ttfautohint
    ttfHint(ttfunhinted,ttf)
    printFontInfo(ttf)
    print(font.fullname, 'TTF autohinted.')

    # hinted ttf to woff
    ttf2Woff(ttf,woff,genflags)
    print(font.fullname, 'WOFF instance generated.')

    # hinted ttf to woff2
    subprocess.call(['woff2_compress',ttf])
    print(font.fullname, 'WOFF2 instance generated.')

  font.save('sources/boon-master-temp.sfd')
  font.close()

if not os.path.exists(unhinted_dir):
  os.makedirs(unhinted_dir)

buildFont(source,family)
