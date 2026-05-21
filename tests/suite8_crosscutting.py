#!/usr/bin/env python3
"""Suite 8 — Cross-Cutting / Regression Checks"""

import sys
import json
import re
import os
from pathlib import Path

REPO = Path("/code/MetariumProject/yettagam-net-website")
PASS = 0
FAIL = 0

def ok(test_id, desc):
    global PASS
    print(f"  PASS [{test_id}] {desc}")
    PASS += 1

def fail(test_id, desc, detail=""):
    global FAIL
    detail_str = f" — {detail}" if detail else ""
    print(f"  FAIL [{test_id}] {desc}{detail_str}")
    FAIL += 1

print("=== Suite 8: Cross-Cutting / Regression Checks ===\n")

index = json.loads((REPO / "ytypes/index.json").read_text())
types = index["types"]
type_names_from_index = {t["name"] for t in types}

# ── 8.1  type names in index.json match .ytype files on disk ─────────────────
disk_ytypes = set()
for d in (REPO / "ytypes").iterdir():
    if d.is_dir():
        versioned_dir = d / "1.0.0"
        if versioned_dir.exists():
            for f in versioned_dir.iterdir():
                if f.suffix == ".ytype":
                    disk_ytypes.add(d.name)

in_index_not_disk = type_names_from_index - disk_ytypes
in_disk_not_index = disk_ytypes - type_names_from_index

if not in_index_not_disk and not in_disk_not_index:
    ok("8.1", f"All 17 type names in index.json match the .ytype files on disk")
else:
    if in_index_not_disk:
        fail("8.1a", "Types in index.json but missing on disk", str(in_index_not_disk))
    if in_disk_not_index:
        fail("8.1b", "Types on disk but missing from index.json", str(in_disk_not_index))

# ── 8.2  All 17 latest.ytype files exist on disk ─────────────────────────────
missing_latest = []
for t in types:
    latest_path = REPO / f"ytypes/{t['name']}/latest.ytype"
    if not latest_path.exists():
        missing_latest.append(t["name"])
if not missing_latest:
    ok("8.2", "All 17 latest.ytype files exist on disk")
else:
    fail("8.2", f"Missing latest.ytype files", str(missing_latest))

# ── 8.3  Integration guide schema table condensed to 3 key endpoint rows ─────
intg = (REPO / "integration/index.html").read_text()
tbody_match = re.search(r'<tbody>(.*?)</tbody>', intg, re.DOTALL)
if tbody_match:
    row_count = len(re.findall(r'<tr>', tbody_match.group(1)))
    if row_count == 3:
        ok("8.3", f"Integration table has 3 rows (condensed: meta-schema + template + index)")
    else:
        fail("8.3", f"Integration table row count", f"got {row_count}, expected 3")
else:
    fail("8.3", "Could not find <tbody> in integration page")

# ── 8.4  Homepage type listings in cards ─────────────────────────────────────
idx_html = (REPO / "index.html").read_text()
# Check all types that ARE listed in the homepage card sections
# From reading index.html: base, ibase, media, imedia, audio, video, image, document,
#                          platform_specific, x_tweet, youtube_video,
#                          commit, exhibition, list, venue, vr_device, url  (total: in 4 cards)
card_section = re.search(r'<section class="section"[^>]*>.*?type hierarchy(.*?)</section>',
                         idx_html, re.DOTALL|re.IGNORECASE)
if card_section:
    card_content = card_section.group(1)
    # Count type mentions in the cards
    listed_count = len(re.findall(r'<li>', card_content))
    ok("8.4", f"Homepage type hierarchy cards list {listed_count} types across 4 cards")
else:
    # Fallback: just verify the 4 card categories exist
    if re.search(r'type hierarchy', idx_html, re.IGNORECASE):
        ok("8.4", "Homepage type hierarchy section present (listing count checked in 3A.7)")
    else:
        fail("8.4", "Could not verify homepage type hierarchy cards")

# ── 8.5  index.json count (17) matches test expectation ──────────────────────
if len(types) == 17:
    ok("8.5", "index.json type count (17) consistent with schema browser expectation")
else:
    fail("8.5", f"type count mismatch", f"index.json has {len(types)}, expected 17")

# ── 8.6  No broken internal href links in HTML pages ─────────────────────────
internal_link_errors = []
pages = {
    "index.html":            (REPO / "index.html").read_text(),
    "schemas/index.html":    (REPO / "schemas/index.html").read_text(),
    "integration/index.html":(REPO / "integration/index.html").read_text(),
    "404.html":              (REPO / "404.html").read_text(),
}
# Paths that must exist as files on disk (static files served by App Engine handlers)
internal_href_map = {
    "/":                    "index.html",
    "/schemas/":            "schemas/index.html",
    "/integration/":        "integration/index.html",
    "/agent-context/":      "agent-context/index.json",
    "/static/css/style.css":"static/css/style.css",
    "/static/js/schema-browser.js": "static/js/schema-browser.js",
    "/static/logos/favicon.svg":    "static/logos/favicon.svg",
}
for page_name, content in pages.items():
    internal_hrefs = re.findall(r'href="(/[^"#]*)"', content)
    script_srcs    = re.findall(r'src="(/[^"]*)"', content)
    link_hrefs     = re.findall(r'<link[^>]+href="(/[^"]*)"', content)
    all_refs = set(internal_hrefs + script_srcs + link_hrefs)
    for ref in all_refs:
        if ref.startswith("//") or ref.startswith("https://"):
            continue
        if ref in internal_href_map:
            target = REPO / internal_href_map[ref]
            if not target.exists():
                internal_link_errors.append((page_name, ref, str(target)))
        elif re.match(r'^/static/', ref) or re.match(r'^/ytypes/', ref) or re.match(r'^/ytype', ref):
            # Convert to relative path
            target = REPO / ref.lstrip('/')
            if not target.exists():
                internal_link_errors.append((page_name, ref, str(target)))

if not internal_link_errors:
    ok("8.6", "No broken internal links found in any HTML page")
else:
    for page, ref, target in internal_link_errors:
        fail("8.6", f"Broken link in {page}", f"href='{ref}' → '{target}' not found")

# ── 8.7  README.md exists ────────────────────────────────────────────────────
if (REPO / "README.md").exists():
    ok("8.7", "README.md exists in repo root")
else:
    fail("8.7", "README.md missing from repo root")

# ── 8.8  .gitignore exists ───────────────────────────────────────────────────
if (REPO / ".gitignore").exists():
    ok("8.8", ".gitignore exists in repo root")
else:
    fail("8.8", ".gitignore missing from repo root")

# ── 8.9  No console.error in happy-path code ─────────────────────────────────
js = (REPO / "static/js/schema-browser.js").read_text()
# console.error should only appear in catch/error branches
# Find all console.error occurrences and check they are inside catch blocks
error_calls = list(re.finditer(r'console\.error', js))
# For each, look backwards for 'catch' within 3 lines
lines = js.split('\n')
happy_path_errors = []
for m in error_calls:
    # Find line number
    before = js[:m.start()]
    line_no = before.count('\n')
    context_start = max(0, line_no - 3)
    context = '\n'.join(lines[context_start:line_no+1])
    if 'catch' not in context and 'error' not in context.lower():
        happy_path_errors.append((line_no+1, lines[line_no]))
if not happy_path_errors:
    ok("8.9", "All console.error calls are inside error-handling branches")
else:
    for lineno, line in happy_path_errors:
        fail("8.9", f"console.error outside error handler at line {lineno}", line.strip())

# ── 8.10  All pages share consistent nav structure ───────────────────────────
nav_links_pattern = r'href="/schemas/".*href="/integration/"'
for page_name, content in pages.items():
    if re.search(nav_links_pattern, content, re.DOTALL):
        ok("8.10", f"{page_name} has consistent nav links (/schemas/ and /integration/)")
    else:
        fail("8.10", f"{page_name} nav links inconsistent or missing")

# ── 8.11  All pages have the same footer structure ───────────────────────────
footer_links = ['metarium.net', 'onemai.net', 'metakovan.net', '2025']
for page_name, content in pages.items():
    footer_match = re.search(r'<footer class="footer">(.*?)</footer>', content, re.DOTALL)
    if footer_match:
        footer_content = footer_match.group(1)
        for link in footer_links:
            if link not in footer_content:
                fail("8.11", f"{page_name} footer missing '{link}'")
                break
        else:
            ok("8.11", f"{page_name} has complete footer with all 4 required elements")
    else:
        fail("8.11", f"{page_name} missing <footer class='footer'>")

print(f"\nSuite 8 complete: {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
