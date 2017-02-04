#!/usr/bin/env fontforge
#
# Copyright (c) 2016, Sungsit Sawaiwan (https://sungsit.com | gibbozer [at] gmail [dot] com).
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

# Predifined vars
import fontvars
from fontvars import * 

# Helpers
def fontPath(path,ext,name):
  path = build_dir + path
  if not os.path.exists(path):
    os.makedirs(path)
  fontfile = path + '/' + name + '.' + ext
  return fontfile

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

# Helpers
def weights2Strings(weight):
  switcher = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black"
  }
  return switcher.get(weight)

# Microsoft compat
def msFamilyName(weight):
  switcher = {
    100: family + " Thin",
    200: family + " ExtraLight",
    300: family + " Light",
    400: family,
    500: family + " Medium",
    600: family + " SemiBold",
    700: family,
    800: family + " ExtraBold",
    900: family + " Black"
  }
  return switcher.get(weight, family)

def msStyleName(weight):
  switcher = {
    100: "Regular",
    200: "Regular",
    300: "Regular",
    400: "Regular",
    500: "Regular",
    600: "Regular",
    700: "Bold",
    800: "Regular",
    900: "Regular"
  }
  return switcher.get(weight)

def msStyleItalicName(weight):
  switcher = {
    100: "Italic",
    200: "Italic",
    300: "Italic",
    400: "Italic",
    500: "Italic",
    600: "Italic",
    700: "Bold Italic",
    800: "Italic",
    900: "Italic"
  }
  return switcher.get(weight)

def otf2Sfd(otf,sfd_dir):

  font = fontforge.open(otf)
  sfd = sfd_dir + font.fontname + '.sfd'
  if not os.path.exists(sfd_dir):
    os.makedirs(sfd_dir)

  # Reset UniqueID
  font.appendSFNTName('English (US)', 'UniqueID', '')

  weight = font.os2_weight

  font.private['BlueValues'] = BlueValues(weight)
  font.private['OtherBlues'] = OtherBlues(weight)
  font.private['StdHW'] = StdHW(weight)
  font.private['StdVW'] = StdHW(weight)
  font.selection.all()
  font.autoHint()
  font.save(sfd)
  font.private.guess('StdHW')
  font.private.guess('StdVW')
  font.private.guess('StemSnapH')
  font.private.guess('StemSnapV')
  font.selection.all()
  font.autoHint()
  font.save(sfd)

  print(sfd, 'file saved.')
  font.close()

def buildSFD(source,family):

  font = fontforge.open(source)

  # prepare master
  font.familyname = family
  font.version = version
  font.copyright = copyright
  font.os2_vendor = os2_vendor
  font.appendSFNTName('English (US)', 'Manufacturer', foundry)
  font.appendSFNTName('English (US)', 'Designer', designer)
  font.appendSFNTName('English (US)', 'Vendor URL', foundry_url)
  font.appendSFNTName('English (US)', 'Designer URL', designer_url)
  font.appendSFNTName('English (US)', 'License URL', license_url)
  font.appendSFNTName('English (US)', 'Preferred Family', family)

  font.save()

  if source == sources[1]:
    font.mergeFeature(feature_dir + features[1] + '.fea')
  else:
    font.mergeFeature(feature_dir + features[0] + '.fea')

  # loop through each layer & save it as sfd files
  for layer in layers:

    layername = font.layers[layer].name
    font.weight = layername
    font.os2_weight = int(layername)

    # Customize preferred subfamily & styles
    subfamily = weights2Strings(font.os2_weight)
    font.fontname = family.replace(' ','') + '-' + subfamily
    font.fullname = family + ' ' + subfamily
    font.italicangle = 0.0
    font.familyname = msFamilyName(font.os2_weight)

    # Normal style
    if source == sources[0]:
      font.appendSFNTName('English (US)', 'Preferred Styles', subfamily)
      if font.os2_weight == 700:
        font.appendSFNTName('English (US)', 'SubFamily', '')
        font.os2_stylemap = 32 # 0x0020
      else:
        font.appendSFNTName('English (US)', 'SubFamily', 'Regular')
        font.os2_stylemap = 64 # 0x0040

    # Italic style
    if source == sources[1]:
      font.fontname += 'Italic'
      font.fullname += ' Italic'
      font.italicangle = -9.0
      font.appendSFNTName('English (US)', 'Preferred Styles', subfamily + ' Italic')
      font.os2_stylemap = 1 # 0x0001

      if font.os2_weight == 400:
        font.fontname = font.fontname.replace('Regular','')
        font.fullname = font.fullname.replace(' Regular','')
        font.appendSFNTName('English (US)', 'Preferred Styles', 'Italic')
      if font.os2_weight == 700:
        font.appendSFNTName('English (US)', 'SubFamily', 'Bold Italic')
        font.os2_stylemap = 33 # 0x0021
      else:
        font.appendSFNTName('English (US)', 'SubFamily', 'Italic')

    # generate otf
    if font.os2_weight == 400:
      genname = font.fullname.replace(' ','-')
    else:
      genname = font.fullname.replace(' ','-').replace('-Italic','Italic')

    otf = fontPath('otf','otf',genname)

    otfgenflags  = ('opentype', 'PfEd-lookups')
    font.generate(otf, flags=otfgenflags, layer = layername)
    print(otf, 'instance generated.')

    # save sfd
    otf2Sfd(otf,sfd_dir)

  font.close()
  shutil.rmtree(build_dir)

for source in sources:
  buildSFD(source,family)
