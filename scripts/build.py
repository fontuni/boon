#!/usr/bin/env fontforge
#
# Copyright (c) 2016, Sungsit Sawaiwan (https://sungsit.com | gibbozer [at] gmail [dot] com).
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

# SFD building process
import buildsfd
from buildsfd import *

unhinted_dir = build_dir + 'unhinted/'
if not os.path.exists(unhinted_dir):
  os.makedirs(unhinted_dir)

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
    '--default-script=thai',
    '--fallback-script=lao',
    #'--hinting-range-min=9',
    #'--hinting-range-max=18',
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
def font2Woff(font,woff):
  subprocess.call([ 'ttf2woff', '-v', font, woff ])
  print(woff, 'instance generated.')

# https://github.com/google/woff2
def font2Woff2(font,woff2):
  subprocess.call(['woff2_compress',font])
  (root, ext) = os.path.splitext(font)
  os.rename(root + '.woff2', woff2)
  print(woff2, 'instance generated.')

# https://code.google.com/archive/p/ttf2eot/
#def font2Eot(font,eot):
#  os.system('ttf2eot <' + font+ '>' + eot)
#  print(eot, 'instance generated.')

def buildFont(sfd):
  font = fontforge.open(sfd)

  # UniqueID with timestamp
  ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  uniqueid = foundry + ' : ' + font.fullname + ' ' + font.version + ' : ' + ts
  font.appendSFNTName('English (US)', 'UniqueID', uniqueid)

  # Correct Italic name
  if font.os2_weight == 400:
    genname = font.fontname
  else:
    genname = font.fontname.replace('-Italic','Italic')

  otf = fontPath('otf','otf',genname)
  ttf = fontPath('ttf','ttf',genname)
  woffTtf = fontPath('woff-ttf','woff',genname)
  woffOtf = fontPath('woff-otf','woff',genname)
  woff2Ttf = fontPath('woff2-ttf','woff2',genname)
  woff2Otf = fontPath('woff2-otf','woff2',genname)
  #eotTtf = fontPath('eot-ttf','eot',font.fontname)
  #eotOtf = fontPath('eot-otf','eot',font.fontname)
  #svg = fontPath('svg','svg',font.fontname)
  tempwoff2Ttf = build_dir + 'ttf/' + genname + '.woff2'
  tempwoff2Otf = build_dir + 'otf/' + genname + '.woff2'

  # generate otf
  otfgenflags  = ('opentype', 'PfEd-lookups')
  otfunhinted = unhinted_dir + genname + '-unhinted.otf'
  font.generate(otfunhinted, flags=otfgenflags)
  print(otfunhinted, 'instance generated.')

  # AFDKO autohint
  otfHint(otfunhinted,otf)
  #fontOptimize(otf)
  printFontInfo(otf)

  # generate unhinted ttf
  ttfgenflags  = ('opentype', 'no-hints')
  ttfunhinted = unhinted_dir + genname + '-unhinted.ttf'
  font.generate(ttfunhinted, flags=ttfgenflags)
  print(ttfunhinted, 'instance generated.')

  # ttfautohint
  ttfHint(ttfunhinted,ttf)
  #fontOptimize(ttf)
  printFontInfo(ttf)

  # font2woff
  font2Woff(otf,woffOtf)
  font2Woff(ttf,woffTtf)

  # font2woff2
  font2Woff2(otf,woff2Otf)
  font2Woff2(ttf,woff2Ttf)

  # font2eot
  #font2Eot(otf,eotOtf)
  #font2Eot(ttf,eotTtf)

  # gen svg
  #font.generate(svg, flags=otfgenflags)
  #print(svg, 'instance generated.')

  font.close()

for sfd in sorted(glob.glob('./sfd/*.sfd')):
  buildFont(sfd)

# Create zip package for each font pathension
def fontZip(family,version,pkg):
  path = build_dir + pkg + '/'
  package = family + '-v' + version + '-' + pkg + '.zip'
  shutil.copy2('OFL.txt', path)
  os.chdir(build_dir)
  subprocess.call(['zip', '-r', package, pkg])
  os.chdir('..')
  print(package, 'created.')

pkgs = ['otf', 'ttf', 'woff-otf', 'woff-ttf', 'woff2-otf', 'woff2-ttf']

for pkg in pkgs:
  fontZip(family,version,pkg)
