#!/usr/bin/env python3

## Convert text file to pdftk toc
## Example:
##
## 1 TOC
## 2 Preface
## 3 Chapter 1
##  3 Section 1.1
##  10 Section 1.2
## 21 Chapter 2
## ..... etc ......
##

import sys
import codecs
import re

if len(sys.argv) != 2:
    print('Toc file is required (e.g. toc.txt)')
    print('See https://blog.regolit.com/2017/04/13/adding-index-to-pdf-document-using-pdftk')
    sys.exit(1)

with codecs.open(sys.argv[1], encoding='utf8') as fp:
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

print('\n'.join(output))