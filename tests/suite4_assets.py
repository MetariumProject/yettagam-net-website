#!/usr/bin/env python3
"""Suite 4 — CSS / Asset Integrity"""

import sys, re
from pathlib import Path

REPO = Path("/code/MetariumProject/yettagam-net-website")
PASS = 0; FAIL = 0

def ok(tid, desc):
    global PASS; print(f"  PASS [{tid}] {desc}"); PASS += 1

def fail(tid, desc, detail=""):
    global FAIL
    print(f"  FAIL [{tid}] {desc}{' — '+detail if detail else ''}"); FAIL += 1

def assert_has(tid, desc, content, pattern, flags=0):
    if re.search(pattern, content, flags): ok(tid, desc)
    else: fail(tid, desc, f"pattern not found: {pattern!r}")

print("=== Suite 4: CSS / Asset Integrity ===\n")

css = (REPO / "static/css/style.css").read_text()
js  = (REPO / "static/js/schema-browser.js").read_text()
svg = (REPO / "static/logos/favicon.svg").read_bytes()

# ── 4.1  Required CSS classes ────────────────────────────────────────────────
for tid, pat in [
    ("4.1a",  r'\.nav\s*\{'),
    ("4.1b",  r'\.hero\s*\{'),
    ("4.1c",  r'\.schema-layout\s*\{'),
    ("4.1d",  r'\.type-tree\s*\{'),
    ("4.1e",  r'\.schema-detail\s*\{'),
    ("4.1f",  r'\.tab-bar\s*\{'),
    ("4.1g",  r'\.tab-content\s*\{'),
    ("4.1h",  r'\.predicate-group\s*\{'),
    ("4.1i",  r'\.permalink-box\s*\{'),
    ("4.1j",  r'\.copy-btn\s*\{'),
    ("4.1k",  r'\.inheritance-chain\s*\{'),
    ("4.1l",  r'\.tree-toggle\s*\{'),
    ("4.1m",  r'\.error-page\s*\{'),
    ("4.1n",  r'\.error-code\s*\{'),
]:
    class_name = re.search(r'\\\.([a-z_-]+)', pat)
    label = class_name.group(0).replace('\\', '') if class_name else pat
    assert_has(tid, f"CSS class {label} defined", css, pat)

# ── 4.2  Mobile breakpoint ───────────────────────────────────────────────────
mob_m = re.search(r'@media\s*\(max-width:\s*768px\)(.*?)(?=@media|\Z)', css, re.DOTALL)
if mob_m:
    mob = mob_m.group(1)
    if re.search(r'\.nav-links\s*\{[^}]*display\s*:\s*none', mob):
        ok("4.2a", "Mobile @media hides .nav-links")
    else:
        fail("4.2a", "Mobile @media should hide .nav-links with display:none")
    if re.search(r'\.nav-toggle\s*\{[^}]*display\s*:\s*block', mob):
        ok("4.2b", "Mobile @media shows .nav-toggle")
    else:
        fail("4.2b", "Mobile @media should show .nav-toggle with display:block")
else:
    fail("4.2", "No @media (max-width: 768px) block found")

# ── 4.3  .tree-toggle hidden at baseline ─────────────────────────────────────
bt_m = re.search(r'\.tree-toggle\s*\{([^}]*)\}', css)
if bt_m:
    rule = bt_m.group(1)
    if 'none' in rule: ok("4.3", ".tree-toggle has display:none at baseline")
    else: fail("4.3", ".tree-toggle baseline should have display:none", rule.strip())
else:
    fail("4.3", "Could not find .tree-toggle baseline rule")

# ── 4.4  favicon.svg ─────────────────────────────────────────────────────────
if len(svg) > 0: ok("4.4a", "favicon.svg non-empty")
else: fail("4.4a", "favicon.svg is empty")
if b"<svg" in svg: ok("4.4b", "favicon.svg contains <svg element")
else: fail("4.4b", "favicon.svg does not look like SVG")

# ── 4.5  Tab content visibility toggled via CSS ───────────────────────────────
assert_has("4.5a", ".tab-content default display:none",
           css, r'\.tab-content\s*\{[^}]*display\s*:\s*none')
assert_has("4.5b", ".tab-content.active display:block",
           css, r'\.tab-content\.active\s*\{[^}]*display\s*:\s*block')

# ── 4.6  Predicate group toggle ──────────────────────────────────────────────
assert_has("4.6a", ".predicate-group-body default display:none",
           css, r'\.predicate-group-body\s*\{[^}]*display\s*:\s*none')
assert_has("4.6b", ".predicate-group.open body display:block",
           css, r'\.predicate-group\.open\s+\.predicate-group-body\s*\{[^}]*display\s*:\s*block')

# ── 4.7  CSS design tokens ────────────────────────────────────────────────────
for token in ["--bg","--bg-card","--bg-code","--border","--accent","--text","--text-muted"]:
    assert_has("4.7", f"CSS token {token} defined", css, re.escape(token) + r'\s*:')

# ── 4.8  .property-table block removed — CSS simplified to use global table styles ──
# After CSS simplification, .property-table was removed and the schema browser's
# property table now inherits from the global `table` selector. Verify:
# (a) .property-table has NO separate block (deduplication confirmed)
# (b) global `table` selector IS defined (tables still styled)
prop_table_defs = len(re.findall(r'\.property-table\s*\{', css))
if prop_table_defs == 0:
    ok("4.8a", ".property-table separate block absent (CSS simplified — uses global table styles)")
else:
    fail("4.8a", f".property-table still has {prop_table_defs} separate block(s), expected 0 after simplification")

if re.search(r'^table\s*\{', css, re.MULTILINE):
    ok("4.8b", "Global `table` selector defined (property table inherits from it)")
else:
    fail("4.8b", "Global `table` selector missing — property table has no styles")

# ── 4.9  JS file contains all key functions ──────────────────────────────────
if len(js) > 100: ok("4.9a", "schema-browser.js is non-trivially sized")
else: fail("4.9a", "schema-browser.js suspiciously small")

for fn in ["selectType","fetchType","renderDetail","renderOverview",
           "renderSchema","renderPredicates","escapeHtml","getHashType",
           "resolveInheritanceChain"]:
    if fn in js: ok("4.9b", f"JS function '{fn}' present")
    else: fail("4.9b", f"JS function '{fn}' missing")

print(f"\nSuite 4 complete: {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
