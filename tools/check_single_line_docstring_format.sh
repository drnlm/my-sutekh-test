#!/bin/bash
# Neil Muller <drnlmuller+sutekh@gmail.com>, 2008
# Very simple check for single line docstrings without """
# We rely on pygettext to pull out the doc-strings, and grep
# to check for """
# GPL license, see COPYRIGHT file for details.
pyfile=${1?'No file specified'}
if [ ! -f $pyfile ]; then
   echo "No file found" >&2
   exit 1
fi
DOC_LIST=`mktemp /tmp/docstrings.list.XXXXXXXXXX`
pygettext -D -o - $pyfile \
    | grep ^msgid \
    | grep -v \"\"  \
    | cut -d " " -f 2-  > $DOC_LIST
echo "$pyfile: Possible single line docstrings not using \"\"\":"
grep -n -F -f $DOC_LIST $pyfile | grep -v \"\"\"
rm $DOC_LIST
