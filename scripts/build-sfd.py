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
sources = ['Boon-300', 'Boon-300i', 'Boon-400', 'Boon-400i', 'Boon-500', 'Boon-500i', 'Boon-600', 'Boon-600i', 'Boon-700', 'Boon-700i']
copyright =  'Copyright 2013-2015, Sungsit Sawaiwan (https://fontuni.com | uni@fontuni.com). This Font Software is licensed under the SIL Open Font License, Version 1.1 (http://scripts.sil.org/OFL).'
build_dir = './fonts/'
unhinted_dir = './fonts/unhinted/'

def weights2Strings(weight):
    switcher = {
      100: "Thin",
      200: "Extra-Light",
      300: "Light",
      400: "Regular",
      500: "Medium",
      600: "Semi-Bold",
      700: "Bold",
      800: "Extra-Bold",
      900: "Black"
    }
    return switcher.get(weight, "Regular")

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

def buildFont(family):

  # loop through each sfd file & save it
  # then generate ttf, autohint & make woff + woff2
  for source in sources:

    font = fontforge.open(build_dir + 'sfd/' + source + '.sfd')
    font.version = version
    font.copyright = copyright
    font.familyname = family
    font.fontname = source

    # Customize subfamily name
    if source.endswith('i'):
      font.fullname = source.replace('-',' ').replace('i',' Oblique')
      font.appendSFNTName('English (US)', 'SubFamily', weights2Strings(font.os2_weight) + ' Oblique')
    else:
      font.fullname = source.replace('-',' ')
      font.appendSFNTName('English (US)', 'SubFamily', weights2Strings(font.os2_weight))

    font.save()

    genflags  = ('opentype', 'no-hints')
    ttfunhinted = unhinted_dir + source + '-unhinted.ttf'
    
    # generate unhinted ttf
    font.generate(ttfunhinted, flags=genflags)
    print(font.fullname, 'TTF instance generated.')

    ttf = build_dir + 'ttf/' + font.fontname + '.ttf'
    woff = build_dir + 'woff/'+ font.fontname + '.woff'
    woff2 = build_dir + 'woff2/' + font.fontname + '.woff2'
    tempwoff2 = build_dir + 'ttf/' + font.fontname + '.woff2'

    # ttfautohint
    ttfHint(ttfunhinted,ttf)
    printFontInfo(ttf)
    print(font.fullname, 'TTF autohinted.')

    # hinted ttf to woff
    ttf2Woff(ttf,woff,genflags)
    print(font.fullname, 'WOFF instance generated.')

    # hinted ttf to woff2
    subprocess.call(['woff2_compress',ttf])
    os.rename(tempwoff2, woff2)
    print(font.fullname, 'WOFF2 instance generated.')

    font.close()

if not os.path.exists(unhinted_dir):
  os.makedirs(unhinted_dir)

buildFont(family)
