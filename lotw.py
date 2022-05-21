#!/bin/env python3
# ------------------------------------
# Link of the Week Bot 2.0
# by @blu256@koyu.space
#
# Released to the Public Domain.
# ------------------------------------

from os       import environ
from random   import choice
from datetime import datetime as dt

try:
  from mastodon import Mastodon

except ImportError:
  print("Error: please install the Mastodon.py module:")
  print("\t$ pip3 install Mastodon.py")
  exit(2)

DEBUG_SKIP_MASTODON  = False
DEBUG_DO_NOT_COMMENT = False

SITECAT = "sitecat.txt"
entries = []

if not DEBUG_SKIP_MASTODON:
  client = Mastodon(
    access_token = environ['ACCESS_TOKEN'],
    api_base_url = 'https://botsin.space'
  )

try:
  catalog = open(SITECAT, "r")

except FileNotFoundError:
  print("Error: site catalog file ({}) not found!".format(SITECAT))
  exit(1)

lines = catalog.readlines()
catalog.close()

category = None
for line in enumerate(lines):
  i = line[0]
  l = line[1].replace("\n", "")

  # Skip empty lines
  if not len(l):
    continue

  # Skip comments
  if l[0] == ";":
    continue

  # Store current category
  if l[0] == "%":
    category = l[1:].split("/")
    continue

  # Parse entries
  ls = l.split(" ")
  try:
    entries.append(
      {
        'line': i,
        'link': ls[0],
        'desc': " ".join(ls[1:]),
        'cat' : "no category" if category is None else " » ".join(category)
      }
    )

  except:
    print("Warning: line {} is probably faulty".format(i))
    pass # skip faulty lines

# Pick a random link
lotw = choice(entries)

# Pick appropriate tags
tags = ["lotw"]
if lotw['link'].startswith("http"):
  tags += ["web", "www"]

elif lotw['link'].startswith("gemini"):
  tags += ["gemini"]

# Add hashes to tags
for t in enumerate(tags):
  tags[t[0]] = "#" + t[1]

message  = f"📎 Link of the week: {lotw['link']}\n"
message += f"📂 Category: {lotw['cat']}\n"
message += f"\n{lotw['desc']}\n\n"
message += " ".join(tags)

if not DEBUG_SKIP_MASTODON:
  client.toot(message)
else:
    print(message)

# Comment out the link
if not DEBUG_DO_NOT_COMMENT:
  timestamp = dt.now().strftime("%Y-%m-%d (week %W)")
  lines.insert( lotw['line'], "; Link of the week {}\n".format(timestamp) )
  lines[ lotw['line']+1 ] = "; " + lines[ lotw['line']+1 ]

  # Write the file back
  catalog = open(SITECAT, "w")

  for line in lines:
    catalog.write(line)

  catalog.close()
