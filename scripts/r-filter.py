#!/usr/bin/env python2

"""
Pandoc filter to process code blocks with class "R" into
R-generated images.
"""

import subprocess
import hashlib
import os
import sys
from pandocfilters import toJSONFilter, Str, Para, Image, attributes

def sha1(x):
  return hashlib.sha1(x).hexdigest()

def out(s):
    sys.stderr.write('[R     ] ' + s + '\n');

imagedir = "generated-images"

def pipe(cmd, data):
    p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    p.stdin.write(data)
    p.stdin.close()
    data = p.stdout.read()
    p.stdout.close()
    err = p.stderr.read()
    p.stderr.close()
    return data, err

def graphviz(key, value, fmt, meta):
  if key == 'CodeBlock':
    [[ident,classes,keyvals], raw_code] = value
    caption = ""
    if "r" in classes:
      path = os.path.dirname(os.path.abspath(__file__))
      filename = sha1(raw_code)
      alt = Str(caption)
      tit = ""
      src = imagedir + '/' + filename + '.png'
      out(src);
      if not os.path.isfile(src):
        try:
            os.mkdir(imagedir)
        except OSError:
            pass
        code = "ppi <- 300\npng('" + src + \
                "', width=6*ppi, height=6*ppi, res=ppi)\n" + raw_code
        data, err = pipe(["R", "--no-save"], code)
        if (len(err) > 0):
            return Para([Str(err)])
      try:
        image = Image(attributes({}), [alt], [src,tit])
        return Para([image])
      except:
        try:
          image = Image([alt], [src,tit])
          return Para([image])
        except:
          pass

if __name__ == "__main__":
  toJSONFilter(graphviz)
