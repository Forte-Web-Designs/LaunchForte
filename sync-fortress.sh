#!/bin/bash
# sync-fortress.sh — pull every Fortress zip out of Downloads into the repo.
#
# Run it any time. It is safe to run twice.
#
#   bash ~/repos/launchforte/sync-fortress.sh
#
# What it does, and why:
#   Zips are unpacked OLDEST FIRST, so a newer file always overwrites an older
#   one with the same name. That is what makes "I think I missed one" harmless —
#   throw every zip you ever downloaded at it and the newest version of each
#   file wins. Nothing is ever deleted; the previous fortress folder is moved to
#   docs/_to_delete/ with a timestamp so you can always go back.

set -euo pipefail

DL="$HOME/Downloads"
REPO="$HOME/repos/launchforte"
DOCS="$REPO/docs"
DEST="$DOCS/fortress"
TRASH="$DOCS/_to_delete"
STAMP="$(date +%Y%m%d-%H%M%S)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# Every zip family this project has ever shipped under.
PATTERNS=(
  'fortress-complete*.zip'
  'fortress-docs*.zip'
  'fortress-build-system*.zip'
  'fdocs*.zip'
  'fev-*.zip'
  'ev-a*.zip'
  'ev-b*.zip'
  'evidence-library*.zip'
  'evidence-pdfs*.zip'
)

echo "==> Looking for Fortress zips in $DL"
ZIPS=()
while IFS= read -r f; do [ -n "$f" ] && ZIPS+=("$f"); done < <(
  for p in "${PATTERNS[@]}"; do
    find "$DL" -maxdepth 1 -name "$p" -type f 2>/dev/null
  done | sort -u | while read -r f; do
    printf '%s\t%s\n' "$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f")" "$f"
  done | sort -n | cut -f2-
)

if [ ${#ZIPS[@]} -eq 0 ]; then
  echo "    No Fortress zips found. Nothing to do."
  exit 0
fi

echo "    Found ${#ZIPS[@]}, unpacking oldest first so the newest copy of each file wins:"
for z in "${ZIPS[@]}"; do
  printf '      %-34s %s\n' "$(basename "$z")" "$(date -r "$z" '+%b %d %H:%M' 2>/dev/null || true)"
  unzip -qo "$z" -d "$STAGE" 2>/dev/null || echo "        (skipped — not a readable zip)"
done

# Some zips contain a top-level fortress/ or ship/ wrapper; flatten it.
for w in fortress ship; do
  if [ -d "$STAGE/$w" ]; then
    cp -R "$STAGE/$w/." "$STAGE/" 2>/dev/null || true
    rm -rf "$STAGE/$w"
  fi
done

# macOS zip noise.
find "$STAGE" -name '__MACOSX' -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name '.DS_Store' -delete 2>/dev/null || true

echo "==> Setting the previous fortress folder aside (never deleted)"
mkdir -p "$TRASH"
if [ -d "$DEST" ]; then
  mv "$DEST" "$TRASH/fortress-$STAMP"
  echo "    $TRASH/fortress-$STAMP"
else
  echo "    (none existed)"
fi

mkdir -p "$DEST"
cp -R "$STAGE/." "$DEST/"

# Rebuild the manifest from what is ACTUALLY on disk, not from what a zip
# claimed. A manifest that disagrees with the folder is how the count drifted
# to 445 files against a 412 manifest last time.
LIB="$DEST/evidence-library"
if [ -d "$LIB" ]; then
  echo "==> Rebuilding the manifest from the files on disk"
  /usr/bin/python3 - "$LIB" <<'PY'
import os, sys, json
from collections import Counter
lib = sys.argv[1]
imgs, shapes = [], {}
for shape in sorted(os.listdir(lib)):
    d = os.path.join(lib, shape)
    if not os.path.isdir(d):
        continue
    files = sorted(f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.png')))
    if not files:
        continue
    tools = set()
    for f in files:
        p = os.path.splitext(f)[0].split('--')
        tool = p[1] if len(p) >= 3 else 'unknown'
        view = '--'.join(p[2:]) if len(p) >= 3 else os.path.splitext(f)[0]
        tools.add(tool)
        imgs.append({"shape": shape, "tool": tool, "view": view, "file": f"{shape}/{f}"})
    shapes[shape] = {"count": len(files), "tools": sorted(tools)}
json.dump({"count": len(imgs), "shapes": shapes, "images": imgs},
          open(os.path.join(lib, "manifest.json"), "w"), indent=1)
ship = [i for i in imgs if i["shape"] != "_rejects"]
print(f"    {len(ship)} shippable shots  ·  "
      f"{len([s for s in shapes if not s.startswith('_')])} patterns  ·  "
      f"{len(set(i['tool'] for i in ship))} tools")
print("    " + ", ".join(f"{t} {n}" for t, n in Counter(i['tool'] for i in ship).most_common()))
held = len(imgs) - len(ship)
if held:
    print(f"    {held} rejects held back, never shipped")
PY
fi

# The evidence PDFs are what the Cockpit actually attaches: one PDF per
# pattern x tool, replacing four separate image fetches. A PDF attaches, so
# nothing has to be linked — which is the rule the Audit node enforces.
if [ -d "$DEST/evidence-pdfs" ]; then
  SITE="$REPO/site/built-with/packs"
  mkdir -p "$SITE"
  cp "$DEST/evidence-pdfs/"*.pdf "$SITE/" 2>/dev/null || true
  cp "$DEST/evidence-pdfs/packs-index.json" "$SITE/" 2>/dev/null || true
  echo "==> Staged $(ls -1 "$SITE"/*.pdf 2>/dev/null | wc -l | tr -d ' ') packs into site/built-with/packs/"
  echo "    Deploy the site and they are live at /built-with/packs/<pattern>--<tool>.pdf"
fi

echo "==> Done"
echo "    Repo:  $DEST"
echo
echo "    Top level:"
ls -1 "$DEST" | sed 's/^/      /'
echo
echo "    Old copies are in $TRASH — delete that folder yourself when you are happy."
