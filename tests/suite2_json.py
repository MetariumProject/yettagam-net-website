#!/usr/bin/env python3
"""Suite 2 — JSON Data Validity & Schema Correctness"""

import json, os, sys, re
from pathlib import Path

REPO = Path("/code/MetariumProject/yettagam-net-website")
PASS = 0; FAIL = 0

def ok(tid, desc):
    global PASS; print(f"  PASS [{tid}] {desc}"); PASS += 1

def fail(tid, desc, detail=""):
    global FAIL
    print(f"  FAIL [{tid}] {desc}{' — ' + detail if detail else ''}"); FAIL += 1

def load_json(p):
    with open(p) as f: return json.load(f)

print("=== Suite 2: JSON Data Validity & Schema Correctness ===\n")

# ── 2.1  All versioned .ytype files are valid JSON ────────────────────────────
ytype_files = sorted(REPO.glob("ytypes/*/1.0.0/*.ytype"))
ytype_data = {}
parse_errors = []
for f in ytype_files:
    try:
        data = load_json(f); ytype_data[f.stem] = data
    except json.JSONDecodeError as e:
        parse_errors.append((str(f), str(e)))
if not parse_errors:
    ok("2.1", f"All {len(ytype_files)} versioned .ytype files are valid JSON")
else:
    for f, e in parse_errors: fail("2.1", f"Invalid JSON: {f}", e)

# ── 2.2  All latest.ytype files are valid JSON ────────────────────────────────
latest_files = sorted(REPO.glob("ytypes/*/latest.ytype"))
latest_errors = []
for f in latest_files:
    try: load_json(f)
    except Exception as e: latest_errors.append((str(f), str(e)))
if not latest_errors:
    ok("2.2", f"All {len(latest_files)} latest.ytype files are valid JSON")
else:
    for f, e in latest_errors: fail("2.2", f"Invalid JSON: {f}", e)

# ── 2.3  index.json has exactly 17 types ─────────────────────────────────────
index = load_json(REPO / "ytypes/index.json")
types = index.get("types", [])
if len(types) == 17: ok("2.3", "ytypes/index.json has exactly 17 types")
else: fail("2.3", "type count wrong", f"got {len(types)}, expected 17")

# ── 2.4  Every index entry has required fields ───────────────────────────────
REQ = {"name","label","description","kind","version","final","singleton","inherits_from","permalink","latest"}
for t in types:
    missing = REQ - set(t.keys())
    if missing: fail("2.4", f"index entry '{t.get('name','?')}' missing fields", str(missing))
    else: ok("2.4", f"index entry '{t['name']}' has all required fields")

# ── 2.5  Every permalink matches pattern ─────────────────────────────────────
for t in types:
    n = t["name"]; exp = f"https://yettagam.net/ytypes/{n}/1.0.0/{n}.ytype"
    if t.get("permalink") == exp: ok("2.5", f"permalink correct for '{n}'")
    else: fail("2.5", f"permalink mismatch '{n}'", f"got '{t.get('permalink')}', expected '{exp}'")

# ── 2.6  Every latest URL matches pattern ────────────────────────────────────
for t in types:
    n = t["name"]; exp = f"https://yettagam.net/ytypes/{n}/latest.ytype"
    if t.get("latest") == exp: ok("2.6", f"latest URL correct for '{n}'")
    else: fail("2.6", f"latest URL mismatch '{n}'", f"got '{t.get('latest')}'")

# ── 2.7  Every .ytype has all required top-level fields ──────────────────────
REQ_YTYPE = {"$schema","$version","$role","name","label","description","kind",
             "final","singleton","inherits_from","definition","schema"}
for name, data in ytype_data.items():
    missing = REQ_YTYPE - set(data.keys())
    if missing: fail("2.7", f"'{name}.ytype' missing fields", str(missing))
    else: ok("2.7", f"'{name}.ytype' has all required top-level fields")

# ── 2.8  Every .ytype $schema equals meta-schema URL ─────────────────────────
EXPECTED_SCHEMA = "https://yettagam.net/ytype/1.0.0/schema.json"
for name, data in ytype_data.items():
    if data.get("$schema") == EXPECTED_SCHEMA: ok("2.8", f"'{name}.ytype' $schema correct")
    else: fail("2.8", f"'{name}.ytype' wrong $schema", str(data.get("$schema")))

# ── 2.9  Every .ytype schema.type=="object" and schema.properties exists ──────
for name, data in ytype_data.items():
    s = data.get("schema", {})
    errors = []
    if s.get("type") != "object": errors.append(f"schema.type='{s.get('type')}'")
    if not isinstance(s.get("properties"), dict): errors.append("schema.properties missing/not-dict")
    if not errors: ok("2.9", f"'{name}.ytype' schema structure valid")
    else: fail("2.9", f"'{name}.ytype' schema structure", "; ".join(errors))

# ── 2.10  latest.ytype identical to versioned file ───────────────────────────
for t in types:
    n = t["name"]
    v_path = REPO / f"ytypes/{n}/1.0.0/{n}.ytype"
    l_path = REPO / f"ytypes/{n}/latest.ytype"
    if not v_path.exists(): fail("2.10", f"'{n}' versioned file missing"); continue
    if not l_path.exists(): fail("2.10", f"'{n}' latest.ytype missing"); continue
    if v_path.read_text() == l_path.read_text(): ok("2.10", f"'{n}' latest.ytype identical to versioned")
    else: fail("2.10", f"'{n}' latest.ytype differs from versioned")

# ── 2.11  Every inherits_from reference resolves to a known type ─────────────
type_names = {t["name"] for t in types}
PARENT_RE = re.compile(r"^/ytypes/([a-z_]+)/")
for name, data in ytype_data.items():
    for ref in data.get("inherits_from", []):
        m = PARENT_RE.match(ref)
        if m:
            parent = m.group(1)
            if parent in type_names: ok("2.11", f"'{name}' inherits_from '{parent}' resolves")
            else: fail("2.11", f"'{name}' inherits_from dangling ref", f"'{parent}' not in index")
        else:
            fail("2.11", f"'{name}' inherits_from unparseable ref", ref)

# ── 2.12  agent-context/index.json validity ──────────────────────────────────
try:
    ctx = load_json(REPO / "agent-context/index.json")
    missing = {"name","url","schemas"} - set(ctx.keys())
    if not missing: ok("2.12", "agent-context/index.json valid with required fields")
    else: fail("2.12", "agent-context/index.json missing fields", str(missing))
except Exception as e:
    fail("2.12", "agent-context/index.json failed", str(e))

# ── 2.13  meta-schema and template schema parse as valid JSON ─────────────────
for path, label in [("ytype/1.0.0/schema.json","meta-schema"),
                    ("ytype_template/1.0.0/schema.json","template schema")]:
    try:
        data = load_json(REPO / path)
        ok("2.13", f"{label} is valid JSON")
        # Extra: meta-schema now has type:object
        if path.endswith("schema.json") and "ytype_template" not in path:
            if data.get("type") == "object":
                ok("2.13b", "meta-schema has type:object")
            else:
                fail("2.13b", "meta-schema missing type:object", str(data.get("type")))
            # $schema/$version/$role in required
            req = data.get("required", [])
            for field in ["$schema","$version","$role"]:
                if field in req: ok("2.13c", f"meta-schema required includes '{field}'")
                else: fail("2.13c", f"meta-schema required missing '{field}'")
    except Exception as e:
        fail("2.13", f"{label} parse failed", str(e))

# ── 2.14  ytype_template restructured as valid JSON Schema ───────────────────
try:
    tmpl = load_json(REPO / "ytype_template/1.0.0/schema.json")
    if tmpl.get("type") == "object":
        ok("2.14a", "ytype_template has type:object at top level")
    else:
        fail("2.14a", "ytype_template missing type:object", str(tmpl.get("type")))
    if isinstance(tmpl.get("properties"), dict):
        ok("2.14b", "ytype_template has properties object")
    else:
        fail("2.14b", "ytype_template missing properties dict")
    if isinstance(tmpl.get("description"), str):
        ok("2.14c", "ytype_template description is a string (not object)")
    else:
        fail("2.14c", "ytype_template description should be string", str(type(tmpl.get("description"))))
except Exception as e:
    fail("2.14", "ytype_template failed", str(e))

print(f"\nSuite 2 complete: {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
