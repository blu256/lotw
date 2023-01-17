#!/bin/bash
echo "$(grep -E "^[a-z]" sitecat.txt|wc -l) links left"
