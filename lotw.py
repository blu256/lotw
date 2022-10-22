#!/bin/env python3
# ------------------------------------
# Link of the Week Bot 2.1
# by @blu256@koyu.space
#
# Released to the Public Domain.
# ------------------------------------

from os       import environ
from sys      import argv
from random   import choice
from datetime import datetime as dt
import re

try:
  from mastodon import Mastodon

except ImportError:
  print("Error: please install the Mastodon.py module:")
  print("\t$ pip3 install Mastodon.py")
  exit(2)

#################################
# Change debugging mode here
DEBUG_CHECK_LINKS    = False
DEBUG_SKIP_MASTODON  = False
DEBUG_DO_NOT_COMMENT = False
#
#################################

SITECAT = "sitecat.txt"

lotd_entries      = []
throwback_entries = []

MODE = "lotd"
if len(argv) > 1 and argv[1] == "throwback":
  MODE = "throwback"

if DEBUG_CHECK_LINKS:
  DEBUG_SKIP_MASTODON  = True
  DEBUG_DO_NOT_COMMENT = True

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

# Used by throwback mode
type     = None
date     = None

category = None
for line in enumerate(lines):
  i = line[0]
  l = line[1].replace("\n", "")

  # Skip empty lines
  if not len(l):
    continue

  # Skip comments except if it is a LOTW/LOTD identifier
  if l[0] == ";":
    if date is None:
      result = re.search("; Link of the (day|week) ([\d]{4,4}-[\d]{2,2}-[\d]{2,2})", l)
      if result:
        type = result.group(1)
        date = result.group(2)
      continue
    else:
      l = l[2:]

  # Store current category
  if l[0] == "%":
    category = l[1:].split("/")
    continue

  # Parse entries
  ls = l.split(" ")
  try:
    entry = {
      'line': i,
      'link': ls[0],
      'desc': " ".join(ls[1:]),
      'cat' : category,
      'cats': "no category" if category is None else " » ".join(category),
    }

    if date is None and MODE == "lotd":
      lotd_entries.append(entry)

    elif date:
      entry['date'] = date
      entry['type'] = type or "day"
      throwback_entries.append(entry)
      date = None
      type = None

  except:
    print("Warning: line {} is probably faulty".format(i))
    date = None
    pass # skip faulty lines

def prepareMessage(link):
  global MODE

  # Pick tags based on category
  tags = ["lotd"]
  for c in reversed(link['cat']):
    tags.append(c.strip().lower().replace('-','').replace(' ',''))

  # Pick appropriate tags based on protocol
  if link['link'].startswith("http"):
    tags += ["web"]

  elif link['link'].startswith("gemini"):
    tags += ["gemini"]

  # Add hashes to tags
  for t in enumerate(tags):
    tags[t[0]] = "#" + t[1]

  # Pick out hashtags from description
  tags += re.findall(r"#[A-Za-z0-9_]*", link['desc'])

  # Compose the toot
  message = ""
  if MODE == "lotd":
    message += f"📎 Link of the day: {link['link']}\n"
  else:
    message +=  "🕖 Link of the day THROWBACK\n"
    message += f"This day, one year ago...\n\n"
    message += f"📎 Link of the {link['type']}: {link['link']}\n"
  message += f"📂 Category: {link['cats']}\n"
  message += f"\n{link['desc']}\n\n"
  message += " ".join(tags)
  return message

# Pick a random link
if DEBUG_CHECK_LINKS:
  for l in lotd_entries:
    message = prepareMessage(l)
    if len(message) > 500:
      print(f"{l['link']}: Message length exceeds 500 characters! Make the description shorter!")
  print("Check completed")
  exit(0)
else:
  l = None
  message = None
  if MODE == "lotd":
    l = choice(lotd_entries)
  else:
    for entry in throwback_entries:
      link_date = dt.strptime(entry['date'], "%Y-%m-%d")
      today     = dt.now()
      delta = today - link_date
      if delta.days == 365:
        l = entry

  if l is not None:
    message = prepareMessage(l)

# Post it!
if message:
  if not DEBUG_SKIP_MASTODON:
    client.toot(message)
  else:
    print(message)
else:
  print("Nothing to post")

# Comment out the link
if not DEBUG_DO_NOT_COMMENT and not MODE == "throwback":
  timestamp = dt.now().strftime("%Y-%m-%d")
  lines.insert( lotd['line'], "; Link of the day {}\n".format(timestamp) )
  lines[ lotd['line']+1 ] = "; " + lines[ lotd['line']+1 ]

  # Write the file back
  catalog = open(SITECAT, "w")

  for line in lines:
    catalog.write(line)

  catalog.close()
