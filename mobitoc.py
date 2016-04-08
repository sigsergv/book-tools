#!/usr/bin/env python
"""
Extract and compile epub files produced by calibre ebook-convert script from amazon mobi file
"""

import os
import shutil
import zipfile
import re
import uuid
from sys import exit
from optparse import OptionParser
from pprint import pprint as pp

description = '''Available commands are: extract, makebook
'''
usage = 'Usage:\n    %prog <command> [options] [FILE]'

parser = OptionParser(usage=usage, description=description)
parser.add_option('', '--remove-dir', dest='remove_dir',
    help="Remove target directory if it's already exists", default=False, action='store_true')

(options, args) = parser.parse_args()

def help():
    pass

if len(args) == 0:
    print('Arguments is required')
    exit(1)

command = args[0]
args = args[1:]

# commands
def extract(options, args):
    if len(args) != 1:
        print('Filename is required')
        exit(1)

    filename = args[0]
    directory = os.path.dirname(os.path.abspath(filename))

    if not os.path.exists(filename):
        print('Filename `{0}` doesn\'t exist'.format(filename) )
        exit(1)

    bn = os.path.basename(filename)
    fn, _ = os.path.splitext(bn)

    # try to open file as ZIP archive
    try:
        z = zipfile.ZipFile(filename, 'r')
    except zipfile.BadZipfile:
        print("`{0}` is not a valid epub document".format(filename))
        exit(1)

    # create directory to extract data
    target_dir = os.path.join(directory, fn)

    if os.path.exists(target_dir):
        if options.remove_dir:
            # delete the directory
            shutil.rmtree(target_dir)
        else:
            print("Cannot create directory `{0}`, it's already exists, use option --remove-dir to overwrite it.".format(target_dir) )
            exit(1)

    os.mkdir(target_dir)

    # extract archive content to that dir
    z.extractall(target_dir)

    # open `toc.ncx` and try to ipdate it with the new data
    toc_fn = os.path.join(target_dir, 'toc.ncx')

    if not os.path.exists(toc_fn):
        print(">> No TOC file, skipping toc.ncx update")
    else:
        html_file_re = re.compile('split_[0-9]{3}\.html$')
        # read listing of target_dir and find all html files that match 
        # specific mask
        scan_files = []
        for _ in os.listdir(target_dir):
            if html_file_re.search(_) is not None:
                scan_files.append(_)

        base_uuid = str(uuid.uuid4())
        scan_files = sorted(scan_files)
        
        toc_item_tpl = '''
    <navPoint id="{id}" playOrder="{order}">
      <navLabel>
        <text>{label}</text>
      </navLabel>
      <content src="{contentsrc}"/>
    </navPoint>
'''
        toc_fp = open(toc_fn, 'a')
        hre = re.compile('<h2[^>]+>')

        toc_fp.write('<!--\n')
        for sfn in scan_files:
            with open(os.path.join(target_dir, sfn)) as fp:
                start = fp.read(1000)
                hpos = start.find('<h2 ')
                fragment = start[hpos:hpos+300]
                fragment = hre.sub('', fragment)
                toc_fp.write(sfn + '\n' + fragment + '\n')

        toc_fp.write('-->\n')

        toc_fp.write('<!--\n $TITLE ($AUTHOR)')

        order = 0
        for sfn in scan_files:
            order += 1
            item = toc_item_tpl.format(order=order, id='{0}-{1}'.format(base_uuid, order),
                label=' ()', contentsrc=sfn)
            toc_fp.write(item)
        toc_fp.write('-->\n')
        toc_fp.close()
            

def makebook(options, args):
    # check that we are in epub source dir and compress all it's content to single file `../$FOLDER_NAME.epub`
    cwd = os.path.abspath(os.getcwd())
    dirname  = os.path.basename(cwd)
    output_fn = os.path.abspath( os.path.join(cwd, '..', dirname+'.epub') )
    if os.path.exists(output_fn):
        os.unlink(output_fn)
    z = zipfile.ZipFile(output_fn, 'w', zipfile.ZIP_DEFLATED)

    for dirpath, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            filename = os.path.join(dirpath, fn)
            # remove heading './'
            arcname = filename[2:]
            z.write(filename)

    z.close()

if command == 'extract':
    extract(options, args)
elif command == 'makebook':
    makebook(options, args)
