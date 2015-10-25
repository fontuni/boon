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
import shutil
import time
import datetime

# Predifined vars
foundry = 'FontUni'
family = 'Boon'
version = '1.0-beta3'
sources = ['sources/boon-master.sfd', 'sources/boon-master-oblique.sfd']
layers = ['300', '400', '500', '600', '700']
copyright =  'Copyright 2013-2015, Sungsit Sawaiwan (https://fontuni.com | uni@fontuni.com). This Font Software is licensed under the SIL Open Font License, Version 1.1 (http://scripts.sil.org/OFL).'
features = ['boon-roman', 'boon-oblique']
feature_dir = 'sources/'

build_dir = 'fonts/'
if os.path.exists(build_dir):
  shutil.rmtree(build_dir)

sfd_dir = 'sfd/'
if os.path.exists(sfd_dir):
  shutil.rmtree(sfd_dir)

unhinted_dir = build_dir + 'unhinted/'
if not os.path.exists(unhinted_dir):
  os.makedirs(unhinted_dir)

exts = ['otf', 'ttf', 'woff', 'woff2']

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
  return switcher.get(weight, "Regular")

# Microsoft compat
def msFamilyName(weight):
  switcher = {
    100: family + " Thin",
    200: family + "ExtraLight",
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
    '--strong-stem-width=G',
    '--hinting-range-min=7',
    '--hinting-range-max=28',
    '--hinting-limit=50',
    '--increase-x-height=13',
    '--no-info',
    '--verbose',
    unhinted,
    hinted
  ])

# Optimize
def fontOptimize(fontfile):
  subprocess.call([
    'pyftsubset',
    fontfile,
    '--glyphs=*',
    '--layout-features=*',
    '--name-IDs=*',
    '--hinting',
    '--legacy-kern',
    '--notdef-outline',
    '--no-subset-tables+=DSIG',
    '--drop-tables-=DSIG',
    '--output-file=' + fontfile
  ])

def ttf2Woff(ttf,woff,genflags):
  font = fontforge.open(ttf)
  font.generate(woff, flags=genflags)
  font.close()

def fontPath(ext,name):
  path = build_dir + ext
  if not os.path.exists(path):
    os.makedirs(path)
  fontfile = path + '/' + name + '.' + ext
  return fontfile

def otf2Sfd(otf,sfd_dir):
  font = fontforge.open(otf)
  sfd = sfd_dir + font.fontname + '.sfd'
  if not os.path.exists(sfd_dir):
    os.makedirs(sfd_dir)
  font.appendSFNTName('English (US)', 'UniqueID', '')
  font.save(sfd)
  print(font.fontname, 'SFD files saved.')
  font.close()

def buildFont(source,family):

  # prepare master
  font = fontforge.open(source)
  font.familyname = family
  font.appendSFNTName('English (US)', 'Preferred Family', family)
  font.version = version
  font.copyright = copyright
  font.save()

  if source.endswith('oblique.sfd'):
    font.mergeFeature(feature_dir + features[1] + '.fea')
  else:
    font.mergeFeature(feature_dir + features[0] + '.fea')

  # loop through each layer & save it as sfd files
  # then generate ttf, autohint & make woff + woff2
  for layer in layers:

    layername = font.layers[layer].name
    font.weight = layername
    font.os2_weight = int(layername)

    font.fontname = family.replace(' ','-') + '-' + layername
    subfamily = weights2Strings(font.os2_weight)
    font.fullname = family + ' ' + subfamily
    font.italicangle = 0.0
    font.familyname = msFamilyName(font.os2_weight)

    # Customize preferred subfamily & styles
    if source.endswith('oblique.sfd'):
      font.fontname += 'i'
      font.fullname += ' Oblique'
      font.italicangle = -9.0
      if subfamily == 'Bold':
        font.appendSFNTName('English (US)', 'SubFamily', 'Bold Oblique')
      else:
        font.appendSFNTName('English (US)', 'SubFamily', 'Oblique')
      font.appendSFNTName('English (US)', 'Preferred Styles', subfamily + ' Oblique')
  
    else:
      font.appendSFNTName('English (US)', 'SubFamily', 'Regular')
      if subfamily == 'Bold':
        font.appendSFNTName('English (US)', 'SubFamily', 'Bold')
      else:
        font.appendSFNTName('English (US)', 'SubFamily', 'Regular')
      font.appendSFNTName('English (US)', 'Preferred Styles', subfamily)

    # UniqueID with timestamp
    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    uniqueid = foundry + ' : ' + font.fullname + ' ' + version + ' : ' + ts
    font.appendSFNTName('English (US)', 'UniqueID', uniqueid)
    

    otf = fontPath('otf',font.fontname)
    ttf = fontPath('ttf',font.fontname)
    woff = fontPath('woff',font.fontname)
    woff2 = fontPath('woff2',font.fontname)
    tempwoff2 = build_dir + 'ttf/' + font.fontname + '.woff2'

    # generate otf
    otfgenflags  = ('opentype', 'PfEd-lookups')
    font.generate(otf, flags=otfgenflags, layer = layername)
    print(font.fullname, 'OTF instance generated.')

    # save sfd
    otf2Sfd(otf,sfd_dir)

    # generate unhinted ttf
    ttfgenflags  = ('opentype', 'no-hints')
    ttfunhinted = unhinted_dir + font.fontname + '-unhinted.ttf'
    font.generate(ttfunhinted, flags=ttfgenflags, layer = layername)
    print(font.fullname, 'Unhinted TTF instance generated.')

    # ttfautohint
    ttfHint(ttfunhinted,ttf)
    fontOptimize(ttf)
    printFontInfo(ttf)
    print(font.fullname, 'TTF autohinted.')

    # hinted ttf to woff
    ttf2Woff(ttf,woff,ttfgenflags)
    print(font.fullname, 'WOFF instance generated.')

    # hinted ttf to woff2
    subprocess.call(['woff2_compress',ttf])
    os.rename(tempwoff2, woff2)
    print(font.fullname, 'WOFF2 instance generated.')

  font.close()

for source in sources:
  buildFont(source,family)

# Create zip package for each font extension
def fontZip(family,version,ext):
  path = build_dir + ext + '/'
  package = family + '-v' + version + '-' + ext + '.zip'
  shutil.copy2('OFL.txt', path)
  os.chdir(build_dir)
  subprocess.call(['zip', '-r', package, ext])
  os.remove(ext + '/OFL.txt')
  os.chdir('..')
  print(package, 'created.')

for ext in exts:
  fontZip(family,version,ext)
