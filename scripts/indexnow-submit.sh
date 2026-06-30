#!/usr/bin/env bash
# IndexNow submission helper.
#
# What this does: reads every URL from site/sitemap.xml and submits the full
# list to the IndexNow API in one POST. IndexNow is the standard for telling
# Bing (and by extension ChatGPT Search, which runs on Bing's index) that
# content has changed, so pages get crawled and indexed in minutes instead
# of waiting for the next bot pass.
#
# When to run:
# - After deploying a new page or post
# - After updating an existing page's body copy or metadata
# - Routinely (monthly is fine) to re-ping everything
#
# Usage:
#   ./scripts/indexnow-submit.sh
#
# Verify the key file exists at the site root: site/d2fcd25a046091def7f4d784e464b53c.txt
# That file proves we own the key. Without it, submissions are rejected.

set -e

KEY="d2fcd25a046091def7f4d784e464b53c"
HOST="launchforte.com"
KEY_LOCATION="https://${HOST}/${KEY}.txt"
SITEMAP="$(dirname "$0")/../site/sitemap.xml"

if [ ! -f "$SITEMAP" ]; then
  echo "ERROR: sitemap not found at $SITEMAP"
  exit 1
fi

# Extract every <loc> URL from the sitemap, one per line, as a JSON array.
URLS=$(grep -oE '<loc>[^<]+</loc>' "$SITEMAP" | sed -E 's:</?loc>::g')

if [ -z "$URLS" ]; then
  echo "ERROR: no URLs found in sitemap"
  exit 1
fi

URL_COUNT=$(echo "$URLS" | wc -l | tr -d ' ')
echo "Submitting $URL_COUNT URLs to IndexNow..."

# Build the JSON body. IndexNow accepts up to 10,000 URLs per request.
JSON_URLS=$(echo "$URLS" | python3 -c "
import sys, json
urls = [line.strip() for line in sys.stdin if line.strip()]
print(json.dumps(urls))
")

PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({
    'host': '${HOST}',
    'key': '${KEY}',
    'keyLocation': '${KEY_LOCATION}',
    'urlList': json.loads('''${JSON_URLS}''')
}))
")

# Submit to IndexNow. Bing's endpoint accepts submissions on behalf of
# every search engine that participates in the protocol (Yandex, Seznam,
# Naver, etc), so one POST covers all of them.
RESPONSE=$(curl -s -w '\nHTTP_STATUS:%{http_code}' \
    -X POST 'https://api.indexnow.org/IndexNow' \
    -H 'Content-Type: application/json; charset=utf-8' \
    --data "$PAYLOAD")

echo "$RESPONSE"

# Status codes: 200 = OK, 202 = accepted (verify pending), 400 = bad
# request, 403 = forbidden (key mismatch), 422 = invalid URLs, 429 = too
# many requests. 200 and 202 are the success states.
