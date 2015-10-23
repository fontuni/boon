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

# Predifined vars
family = 'Boon'
version = '1.0'
sources = ['sources/boon-master.sfd', 'sources/boon-master-oblique.sfd']
layers = ['300', '400', '500', '600', '700']
copyright =  'Copyright 2013-2015, Sungsit Sawaiwan (https://fontuni.com | uni@fontuni.com). This Font Software is licensed under the SIL Open Font License, Version 1.1 (http://scripts.sil.org/OFL).'
features = ['boon-normal', 'boon-oblique']
feature_dir = 'sources/'
build_dir = 'fonts/'
unhinted_dir = 'fonts/unhinted/'
if not os.path.exists(unhinted_dir):
  os.makedirs(unhinted_dir)

def weights2Strings(layer):
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
  return switcher.get(layer, "Regular")

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

def fontPath(ext,name):
  path = build_dir + ext
  if not os.path.exists(path):
    os.makedirs(path)
  fontfile = path + '/' + name + '.' + ext
  return fontfile

def otf2Sfd(otf):
  font = fontforge.open(otf)
  path = 'sfd/'
  sfd = path + font.fontname + '.sfd'
  if not os.path.exists(path):
    os.makedirs(path)
  font.appendSFNTName('English (US)', 'UniqueID', '')
  font.save(sfd)
  print(font.fontname, '.sfd saved.')
  font.close()

def buildFont(source,family):

  # prepare master
  font = fontforge.open(source)
  font.familyname = family
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
    subfamily = weights2Strings(font.os2_weight)
    font.fontname = family + '-' + layername
    font.fullname = font.fontname.replace('-',' ')
    font.italicangle = 0.0

    # Customize subfamily name
    if source.endswith('oblique.sfd'):
      font.fontname += 'i'
      font.fullname += ' Oblique'
      font.appendSFNTName('English (US)', 'SubFamily', subfamily + ' Oblique')
      font.italicangle = -9.0
    else:
      font.appendSFNTName('English (US)', 'SubFamily', subfamily)


    otf = fontPath('otf',font.fontname)
    ttf = fontPath('ttf',font.fontname)
    woff = fontPath('woff',font.fontname)
    woff2 = fontPath('woff2',font.fontname)
    tempwoff2 = build_dir + 'ttf/' + font.fontname + '.woff2'

    # generate unhinted ttf
    ttfgenflags  = ('opentype', 'no-hints')
    ttfunhinted = unhinted_dir + font.fontname + '-unhinted.ttf'
    font.generate(ttfunhinted, flags=ttfgenflags, layer = layername)
    print(font.fullname, 'Unhinted TTF instance generated.')

    # ttfautohint
    ttfHint(ttfunhinted,ttf)
    printFontInfo(ttf)
    print(font.fullname, 'TTF autohinted.')

    # hinted ttf to woff
    ttf2Woff(ttf,woff,ttfgenflags)
    print(font.fullname, 'WOFF instance generated.')

    # hinted ttf to woff2
    subprocess.call(['woff2_compress',ttf])
    os.rename(tempwoff2, woff2)
    print(font.fullname, 'WOFF2 instance generated.')

    # generate otf
    otfgenflags  = ('opentype', 'PfEd-lookups')
    font.generate(otf, flags=otfgenflags, layer = layername)
    print(font.fullname, 'OTF instance generated.')

    # save sfd
    otf2Sfd(otf)

  font.close()

for source in sources:
  buildFont(source,family)

# Create zip package
package = family + '-v' + version + '.zip'
shutil.copy2('LICENSE', build_dir)
os.chdir(build_dir)

try:
  os.remove(package)
except OSError:
  pass

subprocess.call(['zip', '-r', package, '.'])
print(package, 'created.')
