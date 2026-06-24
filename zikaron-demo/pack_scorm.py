#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pack_scorm.py - Wrap a rendered Quarto book (_book/) as a SCORM 1.2 package
ready to upload to Moodle as a "SCORM package" activity.

Usage:
    python pack_scorm.py [BOOK_DIR] [OUTPUT_ZIP] [--title "..."] [--entry index.html]

Defaults:
    BOOK_DIR    = _book
    OUTPUT_ZIP  = book_scorm.zip
    title       = "Course Book"
    entry       = index.html

What it does:
  * imsmanifest.xml is written to the ROOT of the zip (Moodle requirement)
  * the *contents* of BOOK_DIR are zipped, not the folder itself
  * every file is enumerated in the manifest (spec-compliant + robust)
  * all paths use forward slashes so the package works on any OS
"""

import argparse
import os
import sys
import zipfile
from xml.sax.saxutils import escape

ATTR = {'"': "&quot;"}  # extra escaping for attribute values

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{mid}" version="1.2"
          xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
                              http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG-1">
    <organization identifier="ORG-1">
      <title>{title}</title>
      <item identifier="ITEM-1" identifierref="RES-1" isvisible="true">
        <title>{title}</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-1" type="webcontent" adlcp:scormtype="sco" href="{entry}">
{files}
    </resource>
  </resources>
</manifest>
"""


def collect_files(book_dir, out_zip_abs):
    found = []
    for root, _dirs, names in os.walk(book_dir):
        for name in names:
            ap = os.path.join(root, name)
            if os.path.abspath(ap) == out_zip_abs:
                continue  # don't swallow our own output
            rel = os.path.relpath(ap, book_dir).replace(os.sep, "/")
            if rel == "imsmanifest.xml":
                continue  # drop any manifest from a previous run
            found.append(rel)
    found.sort()
    return found


def main():
    p = argparse.ArgumentParser(description="Package a Quarto _book/ as SCORM 1.2 for Moodle.")
    p.add_argument("book_dir", nargs="?", default="_book")
    p.add_argument("output_zip", nargs="?", default="book_scorm.zip")
    p.add_argument("--title", default="Course Book")
    p.add_argument("--entry", default="index.html")
    args = p.parse_args()

    book_dir = args.book_dir
    if not os.path.isdir(book_dir):
        sys.exit("ERROR: book directory not found: {}".format(book_dir))

    entry_path = os.path.join(book_dir, args.entry)
    if not os.path.isfile(entry_path):
        sys.exit("ERROR: entry file '{}' not found in {}. "
                 "Quarto books normally produce index.html - run `quarto render` first."
                 .format(args.entry, book_dir))

    out_zip_abs = os.path.abspath(args.output_zip)
    files = collect_files(book_dir, out_zip_abs)
    if args.entry not in files:
        files.append(args.entry)
        files.sort()

    file_elements = "\n".join(
        '      <file href="{}"/>'.format(escape(f, ATTR)) for f in files
    )
    manifest = MANIFEST.format(
        mid="QUARTO-BOOK-MANIFEST",
        title=escape(args.title),
        entry=escape(args.entry, ATTR),
        files=file_elements,
    )

    with zipfile.ZipFile(args.output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("imsmanifest.xml", manifest)
        for f in files:
            zf.write(os.path.join(book_dir, *f.split("/")), arcname=f)

    size_kb = os.path.getsize(args.output_zip) / 1024.0
    print("OK  ->  {}".format(args.output_zip))
    print("    entry point : {}".format(args.entry))
    print("    files packed: {} (+ imsmanifest.xml at root)".format(len(files)))
    print("    size        : {:.1f} KB".format(size_kb))
    print("    upload as   : Moodle activity 'SCORM package'")


if __name__ == "__main__":
    main()
