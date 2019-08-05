#!/usr/bin/env python3
# replace PDF bookmarks tree with a new one
# 
# Requires pdftk installed, it must be visible through $PATH variable

import argparse
import os
import subprocess
import tempfile
import codecs

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

# process metadata and write to file

os.write(metadata_tmp_file_h, metadata.encode('utf-8'))
os.fsync(metadata_tmp_file_h)
# print(metadata_tmp_file)

# write pdf
subprocess.run(['pdftk', pdf_in_file, 'update_info_utf8', metadata_tmp_file, 'output', pdf_out_file])

os.unlink(metadata_tmp_file)

# print((pdf_in_file, toc_file, pdf_out_file))