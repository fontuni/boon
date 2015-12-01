#!/usr/bin/env fontforge
#
# Copyright (c) 2015, Sungsit Sawaiwan (https://sungsit.com | gibbozer [at] gmail [dot] com).
#
# This Font Software is licensed under the SIL Open Font License, Version 1.1 (OFL).
# You should have received a copy of the OFL License along with this file.
# If not, see http://scripts.sil.org/OFL
#

# This script will create font instances from SFD files 
# and it will only work with FontForge's Python extension.
import fontforge
import os
import subprocess
import shutil
import time
import datetime
import glob

# Boon customization
import boon

family = 'Boon'
version = '1.1'
foundry = 'FontUni'
sfd_dir = 'sfd/'

build_dir = 'fonts/'
if os.path.exists(build_dir):
  shutil.rmtree(build_dir)

unhinted_dir = build_dir + 'unhinted/'
if not os.path.exists(unhinted_dir):
  os.makedirs(unhinted_dir)
  
def fontPath(ext,name):
  path = build_dir + ext
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

def otfHint(unhinted,hinted):
  subprocess.call([
    'autohint',
    '-q',
    '-o',
    hinted,
    unhinted
  ])
  print(hinted, 'autohinted.')

def ttfHint(unhinted,hinted):
  subprocess.call([
    'ttfautohint',
    '--default-script=latn',
    '--fallback-script=thai',
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
  print(hinted, 'autohinted.')

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
  print(fontfile, 'optimized.')

# http://wizard.ae.krakow.pl/~jb/ttf2woff/
def ttf2Woff(ttf,woff):
  subprocess.call([ 'ttf2woff', '-v', ttf, woff ])
  print(woff, 'instance generated.')

def ttf2Woff2(ttf,woff2):
  subprocess.call(['woff2_compress',ttf])
  (root, ext) = os.path.splitext(ttf)
  os.rename(root + '.woff2', woff2)
  print(woff2, 'instance generated.')

def ttf2Eot(ttf,eot):
  subprocess.call(['ttf2eot',ttf,eot])
  print(eot, 'instance generated.')

def buildFont(sfd):
  font = fontforge.open(sfd)

  # UniqueID with timestamp
  ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  uniqueid = foundry + ' : ' + font.fullname + ' ' + font.version + ' : ' + ts
  font.appendSFNTName('English (US)', 'UniqueID', uniqueid)

  otf = fontPath('otf',font.fontname)
  ttf = fontPath('ttf',font.fontname)
  woff = fontPath('woff',font.fontname)
  woff2 = fontPath('woff2',font.fontname)
  eot = fontPath('eot',font.fontname)
  svg = fontPath('svg',font.fontname)
  tempwoff2 = build_dir + 'ttf/' + font.fontname + '.woff2'

  # generate otf
  otfgenflags  = ('opentype', 'PfEd-lookups')
  otfunhinted = unhinted_dir + font.fontname + '-unhinted.otf'
  font.generate(otfunhinted, flags=otfgenflags)
  print(otfunhinted, 'instance generated.')

  # AFDKO autohint
  otfHint(otfunhinted,otf)
  fontOptimize(otf)
  printFontInfo(otf)

  # generate unhinted ttf
  ttfgenflags  = ('opentype', 'no-hints')
  ttfunhinted = unhinted_dir + font.fontname + '-unhinted.ttf'
  font.generate(ttfunhinted, flags=ttfgenflags)
  print(ttfunhinted, 'instance generated.')

  # ttfautohint
  ttfHint(ttfunhinted,ttf)
  #fontOptimize(ttf)
  printFontInfo(ttf)

  # ttf2woff
  ttf2Woff(ttf,woff)

  # ttf2woff2
  ttf2Woff2(ttf,woff2)

  # ttf2eot
  ttf2Eot(ttf,eot)

  # gen svg
  font.generate(svg, flags=otfgenflags)
  print(svg, 'instance generated.')

  font.close()

for sfd in sorted(glob.glob('./sfd/*.sfd')):
  buildFont(sfd)

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

exts = ['otf', 'ttf', 'woff', 'woff2', 'eot', 'svg']

for ext in exts:
  fontZip(family,version,ext)
