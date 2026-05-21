#!/usr/bin/env python3
"""Suite 7 — App Engine Configuration Correctness"""

import sys
import re
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

def assert_contains(test_id, desc, content, pattern, flags=0):
    if re.search(pattern, content, flags):
        ok(test_id, desc)
    else:
        fail(test_id, desc, f"pattern not found: {pattern!r}")

print("=== Suite 7: App Engine Configuration Correctness ===\n")

app_yaml = (REPO / "app.yaml").read_text()

# ── 7.1  Runtime ─────────────────────────────────────────────────────────────
assert_contains("7.1", "runtime: python312",
                app_yaml, r'^runtime:\s*python312', re.MULTILINE)

# ── 7.2  ytype meta-schema handler has correct mime and expiration ────────────
# Find the /ytype/(.*) handler block
ytype_block = re.search(
    r'url:\s*/ytype/\(\.\*\)(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
if ytype_block:
    block = ytype_block.group(1)
    if 'application/json' in block:
        ok("7.2a", "/ytype/(.*) handler sets mime_type: application/json")
    else:
        fail("7.2a", "/ytype/(.*) handler missing mime_type: application/json")
    if '365d' in block:
        ok("7.2b", "/ytype/(.*) handler sets expiration: 365d (immutable)")
    else:
        fail("7.2b", "/ytype/(.*) handler should have expiration: 365d")
else:
    fail("7.2", "Could not find /ytype/(.*) handler in app.yaml")

# ── 7.3  ytypes/index.json handler has CORS header ───────────────────────────
index_block = re.search(
    r'url:\s*/ytypes/index\\\.json(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
if index_block:
    block = index_block.group(1)
    if 'Access-Control-Allow-Origin' in block and '"*"' in block:
        ok("7.3", "/ytypes/index.json handler has CORS Access-Control-Allow-Origin: *")
    else:
        fail("7.3", "/ytypes/index.json handler missing CORS header")
else:
    fail("7.3", "Could not find /ytypes/index.json handler in app.yaml")

# ── 7.4  Versioned .ytype handler regex is correct ───────────────────────────
assert_contains("7.4", "Versioned .ytype handler has correct regex pattern",
                app_yaml, r'\(\[a-z_\]\+\)/\(\[0-9\.\]\+\)/\(\.\+\)\\\.ytype')

# ── 7.5  latest.ytype expiration is 10m (mutable) vs versioned 365d ──────────
latest_block = re.search(
    r'url:\s*/ytypes/\(\[a-z_\]\+\)/latest\\\.ytype(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
versioned_block = re.search(
    r'url:\s*/ytypes/\(\[a-z_\]\+\)/\(\[0-9\.\]\+\)/\(\.\+\)\\\.ytype(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
if latest_block:
    if '10m' in latest_block.group(1):
        ok("7.5a", "latest.ytype handler has expiration: 10m (mutable)")
    else:
        fail("7.5a", "latest.ytype handler should have expiration: 10m")
else:
    fail("7.5a", "Could not find latest.ytype handler")

if versioned_block:
    if '365d' in versioned_block.group(1):
        ok("7.5b", "Versioned .ytype handler has expiration: 365d (immutable)")
    else:
        fail("7.5b", "Versioned .ytype handler should have expiration: 365d")
else:
    fail("7.5b", "Could not find versioned .ytype handler")

# ── 7.6  Directory alias serves latest.ytype ─────────────────────────────────
dir_alias_block = re.search(
    r'url:\s*/ytypes/\(\[a-z_\]\+\)/\?\$(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
if dir_alias_block:
    block = dir_alias_block.group(1)
    if 'latest.ytype' in block:
        ok("7.6", "Directory alias /ytypes/{name}/ serves latest.ytype")
    else:
        fail("7.6", "Directory alias handler should reference latest.ytype")
else:
    fail("7.6", "Could not find directory alias handler")

# ── 7.7  Catch-all handler uses script:auto + error_handlers for proper 404 ──
# New architecture: catch-all script: auto delegates to main.py WSGI handler,
# which returns 404.html with a real HTTP 404 status code.
assert_contains("7.7a", "Catch-all handler url: /.*",
                app_yaml, r'url:\s*/\.\*')
assert_contains("7.7b", "Catch-all handler uses script: auto (WSGI handler)",
                app_yaml, r'script:\s*auto')
assert_contains("7.7c", "error_handlers section present with 404.html",
                app_yaml, r'error_handlers')
assert_contains("7.7d", "error_handlers references 404.html",
                app_yaml, r'file:\s*404\.html')

# Verify 404 handler is LAST — after all other url patterns
all_urls = [(m.start(), m.group(1)) for m in re.finditer(r'url:\s*(/[^\n]+)', app_yaml)]
catchall_positions = [pos for pos, url in all_urls if url.strip() == '/.*']
if catchall_positions:
    last_pos = max(pos for pos, _ in all_urls)
    if catchall_positions[0] == last_pos:
        ok("7.7e", "Catch-all /.* is the last url handler (correct order)")
    else:
        fail("7.7e", "Catch-all /.* is not the last handler — routes may be wrong")
else:
    fail("7.7e", "Could not verify catch-all handler order")

# ── 7.8  /schemas/ and /integration/ handlers exist before catch-all ─────────
assert_contains("7.8a", "/schemas/? handler present",
                app_yaml, r'url:\s*/schemas/\?')
assert_contains("7.8b", "/integration/? handler present",
                app_yaml, r'url:\s*/integration/\?')

# ── 7.9  Static asset handlers are ordered before HTML page handlers ──────────
css_pos    = app_yaml.find('/static/css')
schemas_pos = app_yaml.find('/schemas')
if css_pos != -1 and schemas_pos != -1:
    if css_pos < schemas_pos:
        ok("7.9", "Static asset handlers (/static/css) appear before HTML page handlers (/schemas)")
    else:
        fail("7.9", "Static asset handlers should appear before page handlers in app.yaml")
else:
    fail("7.9", "Could not find static or page handler positions")

# ── 7.10  CORS headers on all JSON endpoints ─────────────────────────────────
json_handler_patterns = [
    r'url:\s*/ytype/\(\.\*\)',
    r'url:\s*/ytype_template/\(\.\*\)',
    r'url:\s*/ytypes/index\\\.json',
    r'url:\s*/ytypes/\(\[a-z_\]\+\)/\(\[0-9\.\]\+\)/\(\.\+\)\\\.ytype',
    r'url:\s*/ytypes/\(\[a-z_\]\+\)/latest\\\.ytype',
    r'url:\s*/ytypes/\(\[a-z_\]\+\)/\?\$',
    r'url:\s*/agent-context/\?',
]
for i, pat in enumerate(json_handler_patterns):
    m = re.search(pat + r'(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
    if m:
        block = m.group(1) if m.lastindex else ''
        # Look for either the block following the url: line
        if 'Access-Control-Allow-Origin' in block:
            ok(f"7.10", f"JSON handler {i+1} has CORS header")
        else:
            fail(f"7.10", f"JSON handler {i+1} missing CORS header", f"pattern: {pat}")
    else:
        fail(f"7.10", f"Could not find JSON handler {i+1}", f"pattern: {pat}")

# ── 7.11  /agent-context/ handler points to agent-context/index.json ─────────
agent_block = re.search(
    r'url:\s*/agent-context/\?(.*?)(?=\n\s*-\s*url:|\Z)', app_yaml, re.DOTALL)
if agent_block:
    block = agent_block.group(1)
    if 'agent-context/index.json' in block:
        ok("7.11", "/agent-context/? handler serves agent-context/index.json")
    else:
        fail("7.11", "/agent-context/? handler should reference agent-context/index.json")
else:
    fail("7.11", "Could not find /agent-context/? handler")

print(f"\nSuite 7 complete: {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
