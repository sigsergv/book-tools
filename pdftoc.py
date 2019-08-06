#!/usr/bin/env python3
# replace PDF bookmarks tree with a new one
# 
# Requires pdftk installed, it must be visible through $PATH variable

import argparse
import os
import subprocess
import tempfile
import codecs
import re

parser = argparse.ArgumentParser()
parser.add_argument('pdf_in', help='Input PDF file.')
parser.add_argument('toc', help='File with bookmarks tree.')
parser.add_argument('pdf_out', help='Output PDF file.')

args = parser.parse_args()

pdf_in_file = os.path.abspath(args.pdf_in)
toc_file = os.path.abspath(args.toc)
pdf_out_file = os.path.abspath(args.pdf_out)

# extract metadata
metadata_tmp_file_h, metadata_tmp_file = tempfile.mkstemp()

r = subprocess.run(['pdftk', pdf_in_file, 'dump_data_utf8'], stdout=subprocess.PIPE, universal_newlines=True)
metadata = r.stdout

# read and parse TOC
with codecs.open(toc_file, encoding='utf8') as fp:
    lines = [x.strip('\n') for x in fp]

LINE_RE = re.compile('^( *)([0-9]+)\\s+(.+)')

output = []
for n,line in enumerate(lines):
    mo = LINE_RE.match(line)
    if mo is None:
        print('Incorrect text on line {0}: {1}', n+1, line)
        sys.exit(1)
    level = len(mo.group(1))+1
    page = int(mo.group(2))
    title = mo.group(3)

    output.append('BookmarkBegin')
    output.append('BookmarkTitle: {0}'.format(title))
    output.append('BookmarkLevel: {0}'.format(level))
    output.append('BookmarkPageNumber: {0}'.format(page))


# process metadata and write to file
metadata_lines = [x for x in metadata.splitlines() if not x.startswith('Bookmark')]
insert_position = metadata_lines.index('PageMediaBegin')

metadata_lines = metadata_lines[:insert_position] + output + metadata_lines[insert_position:]

os.write(metadata_tmp_file_h, '\n'.join(metadata_lines).encode('utf-8'))
os.fsync(metadata_tmp_file_h)
# print(metadata_tmp_file)

# write pdf
subprocess.run(['pdftk', pdf_in_file, 'update_info_utf8', metadata_tmp_file, 'output', pdf_out_file])

os.unlink(metadata_tmp_file)

# print((pdf_in_file, toc_file, pdf_out_file))