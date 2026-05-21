#!/usr/bin/env python3
"""Suite 3 — HTML Structure & Content Correctness"""

import sys, re
from pathlib import Path

REPO = Path("/code/MetariumProject/yettagam-net-website")
PASS = 0; FAIL = 0

def ok(tid, desc):
    global PASS; print(f"  PASS [{tid}] {desc}"); PASS += 1

def fail(tid, desc, detail=""):
    global FAIL
    print(f"  FAIL [{tid}] {desc}{' — '+detail if detail else ''}"); FAIL += 1

def has(content, pattern, flags=re.IGNORECASE):
    return bool(re.search(pattern, content, flags))

def assert_has(tid, desc, content, pattern, flags=re.IGNORECASE):
    if has(content, pattern, flags): ok(tid, desc)
    else: fail(tid, desc, f"pattern not found: {pattern!r}")

def assert_count(tid, desc, content, pattern, expected, flags=re.IGNORECASE):
    n = len(re.findall(pattern, content, flags))
    if n == expected: ok(tid, desc)
    else: fail(tid, desc, f"expected {expected}, found {n} for {pattern!r}")

print("=== Suite 3: HTML Structure & Content Correctness ===\n")

# ─── 3A: Landing page ────────────────────────────────────────────────────────
print("--- 3A: Landing page (index.html) ---")
idx = (REPO / "index.html").read_text()

assert_has("3A.1",  "title 'yettagam — digital safe storage'",    idx, r'<title>yettagam')
assert_has("3A.2a", "Nav link /schemas/",                         idx, r'href="/schemas/"')
assert_has("3A.2b", "Nav link /integration/",                     idx, r'href="/integration/"')
assert_has("3A.2c", "Nav link GitHub",                            idx, r'href="https://github\.com/MetariumProject')
assert_has("3A.2d", "Nav brand link",                             idx, r'class="nav-brand"')
assert_has("3A.3a", "Hero h1 contains 'yettagam'",                idx, r'<h1[^>]*>.*yettagam.*</h1>', re.IGNORECASE|re.DOTALL)
assert_has("3A.3b", "CTA 'browse schemas'",                       idx, r'browse schemas')
assert_has("3A.3c", "CTA 'integration guide'",                    idx, r'integration guide')
assert_has("3A.4a", "for-ai-agents section id",                   idx, r'id="for-ai-agents"')
assert_has("3A.4b", "Link to /agent-context/",                    idx, r'href="/agent-context/"')
assert_has("3A.5",  "'what is yettagam?' section",                idx, r'what is yettagam')
assert_has("3A.6a", "schema architecture section",                idx, r'schema architecture')
assert_has("3A.6b", "diagram div present",                        idx, r'class="diagram"')
assert_has("3A.6c", "layer 1 in diagram",                         idx, r'layer 1')
assert_has("3A.6d", "layer 2 in diagram",                         idx, r'layer 2')
assert_has("3A.6e", "layer 3 in diagram",                         idx, r'layer 3')
assert_has("3A.7a", "type hierarchy section",                     idx, r'type hierarchy')
assert_has("3A.7b", "base types card",                            idx, r'base types')
assert_has("3A.7c", "media types card",                           idx, r'media types')
assert_has("3A.7d", "platform types card",                        idx, r'platform types')
assert_has("3A.7e", "data types card",                            idx, r'data types')

# Quick start steps — count <li> inside the .steps ol
steps_m = re.search(r'<ol class="steps">(.*?)</ol>', idx, re.DOTALL)
if steps_m:
    n = len(re.findall(r'<li>', steps_m.group(1)))
    if n == 3: ok("3A.8", "Quick start has 3 steps")
    else: fail("3A.8", "Quick start step count", f"got {n}, expected 3")
else:
    fail("3A.8", "Could not find <ol class='steps'> on landing page")

assert_has("3A.9a", "Footer metarium.net",                        idx, r'href="https://metarium\.net"')
assert_has("3A.9b", "Footer onemai.net",                          idx, r'href="https://onemai\.net"')
assert_has("3A.9c", "Footer metakovan.net",                       idx, r'href="https://metakovan\.net"')
assert_has("3A.9d", "Footer copyright 2025",                      idx, r'2025')
assert_has("3A.10a","meta viewport",                              idx, r'name="viewport"')
assert_has("3A.10b","meta description",                           idx, r'name="description"')
assert_has("3A.11", "Favicon link",                               idx, r'href="/static/logos/favicon\.svg"')
assert_has("3A.12", "Nav toggle button",                          idx, r'class="nav-toggle"')

# ─── 3B: Schema browser ──────────────────────────────────────────────────────
print("\n--- 3B: Schema browser (schemas/index.html) ---")
sch = (REPO / "schemas/index.html").read_text()

assert_has("3B.1",  "title 'schema browser — yettagam'",          sch, r'<title>schema browser')
assert_has("3B.2a", ".schema-layout present",                     sch, r'class="schema-layout"')
assert_has("3B.2b", ".type-tree present",                         sch, r'class="type-tree"')
assert_has("3B.2c", ".schema-detail present",                     sch, r'class="schema-detail"')
assert_has("3B.3",  "Default placeholder text",                   sch, r'select a type from the tree')
assert_has("3B.4a", "schema-browser.js script tag",               sch, r'src="/static/js/schema-browser\.js"')
nav_pos = sch.find('nav-toggle'); js_pos = sch.find('schema-browser.js')
if nav_pos != -1 and js_pos != -1 and js_pos > nav_pos:
    ok("3B.4b", "schema-browser.js appears after nav-toggle script")
else:
    fail("3B.4b", "schema-browser.js order wrong", f"nav_pos={nav_pos}, js_pos={js_pos}")

# ─── 3C: Integration guide ───────────────────────────────────────────────────
print("\n--- 3C: Integration guide (integration/index.html) ---")
intg = (REPO / "integration/index.html").read_text()

assert_has("3C.1",  "title 'integration guide — yettagam'",       intg, r'<title>integration guide')
assert_has("3C.2",  "Hero h1 'integration guide'",                intg, r'<h1[^>]*>.*integration guide.*</h1>', re.IGNORECASE|re.DOTALL)

for tid, pat in [
    ("3C.3a", r'schema reference urls'),
    ("3C.3b", r'schema linkage'),
    ("3C.3c", r'using \$schema references'),
    ("3C.3d", r'validating against ytype'),
    ("3C.3e", r'type inheritance'),
    ("3C.3f", r'MCP integration'),
    ("3C.3g", r'contributing new types'),
]:
    assert_has(tid, f"Section '{pat}' present", intg, pat)

# Table condensed to 3 rows: meta-schema, yObj template, types index
tbody_m = re.search(r'<tbody>(.*?)</tbody>', intg, re.DOTALL)
if tbody_m:
    n = len(re.findall(r'<tr>', tbody_m.group(1)))
    if n == 3: ok("3C.4", "Integration table has 3 rows (condensed key endpoints)")
    else: fail("3C.4", "Integration table row count", f"got {n}, expected 3")
else:
    fail("3C.4", "Could not find <tbody>")

assert_has("3C.5a", "Python code example",                        intg, r'import json')
assert_has("3C.5b", "JavaScript code example",                    intg, r'await fetch')
assert_has("3C.6a", "MCP tool yettagam_list_types",               intg, r'yettagam_list_types')
assert_has("3C.6b", "MCP tool yettagam_get_type",                 intg, r'yettagam_get_type')
assert_has("3C.7a", "Inheritance diagram base(abstract)",         intg, r'base \(abstract\)')
assert_has("3C.7b", "Inheritance diagram image",                  intg, r'\+-- image')
assert_has("3C.7c", "Inheritance diagram x_tweet",                intg, r'\+-- x_tweet')

steps_m = re.search(r'<ol class="steps">(.*?)</ol>', intg, re.DOTALL)
if steps_m:
    n = len(re.findall(r'<li>', steps_m.group(1)))
    if n == 3: ok("3C.8", "Contributing steps has 3 steps")
    else: fail("3C.8", "Contributing steps count", f"got {n}, expected 3")
else:
    fail("3C.8", "Could not find <ol class='steps'>")

# GitHub external links use target=_blank rel=noopener
github_links = re.findall(r'<a[^>]+href="https?://[^"]*github[^>]*>', intg)
for link in github_links:
    if 'target="_blank"' in link and 'rel="noopener"' in link:
        ok("3C.9", f"GitHub link has target=_blank rel=noopener")
    else:
        fail("3C.9", "GitHub link missing security attrs", link[:120])

# ─── 3D: 404 page ────────────────────────────────────────────────────────────
print("\n--- 3D: 404 page (404.html) ---")
e404 = (REPO / "404.html").read_text()

assert_has("3D.1",  "Title contains 404",                         e404, r'<title>.*404')
assert_has("3D.2",  ".error-code contains 404",                   e404, r'class="error-code"[^>]*>.*404', re.DOTALL)
assert_has("3D.3",  ".error-message present",                     e404, r'class="error-message"')
assert_has("3D.4",  "'go back home' link → /",                   e404, r'href="/"[^>]*>.*go back home', re.DOTALL|re.IGNORECASE)
assert_has("3D.5a", "Nav present in 404",                         e404, r'class="nav"')
assert_has("3D.5b", "Footer present in 404",                      e404, r'class="footer"')

# ─── 3E: main.py WSGI 404 handler ────────────────────────────────────────────
print("\n--- 3E: main.py WSGI 404 handler ---")
main_py = (REPO / "main.py").read_text()

assert_has("3E.1",  "main.py defines app() WSGI callable",        main_py, r'def app\(environ')
assert_has("3E.2",  "main.py returns 404 Not Found status",       main_py, r'404 Not Found')
assert_has("3E.3",  "main.py reads 404.html file",                main_py, r'404\.html')
assert_has("3E.4",  "main.py sets Content-Type text/html",        main_py, r'text/html')

print(f"\nSuite 3 complete: {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
