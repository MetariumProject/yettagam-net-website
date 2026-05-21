#!/usr/bin/env bash
# Suite 1 — HTTP Endpoint Availability & Status Codes
BASE="http://localhost:8080"
PASS=0; FAIL=0

check() {
  local id="$1" desc="$2" url="$3" expected_code="$4"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$code" = "$expected_code" ]; then
    echo "  PASS [$id] $desc (HTTP $code)"
    PASS=$((PASS+1))
  else
    echo "  FAIL [$id] $desc — expected HTTP $expected_code, got $code"
    FAIL=$((FAIL+1))
  fi
}

check_body_json() {
  local id="$1" desc="$2" url="$3"
  local body
  body=$(curl -s "$url")
  if echo "$body" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo "  PASS [$id] $desc (valid JSON)"
    PASS=$((PASS+1))
  else
    echo "  FAIL [$id] $desc — body is not valid JSON"
    echo "    body preview: $(echo "$body" | head -c 120)"
    FAIL=$((FAIL+1))
  fi
}

check_body_contains() {
  local id="$1" desc="$2" url="$3" needle="$4"
  local body
  body=$(curl -s "$url")
  if echo "$body" | grep -q "$needle"; then
    echo "  PASS [$id] $desc (found '$needle')"
    PASS=$((PASS+1))
  else
    echo "  FAIL [$id] $desc — '$needle' not found in response"
    FAIL=$((FAIL+1))
  fi
}

echo "=== Suite 1: HTTP Endpoint Availability ==="

check "1.1"  "GET / → 200"                                   "$BASE/"                                         200
check "1.2"  "GET /schemas/ → 200"                           "$BASE/schemas/"                                 200
check "1.3"  "GET /integration/ → 200"                       "$BASE/integration/"                             200
check "1.4"  "GET /ytypes/index.json → 200"                  "$BASE/ytypes/index.json"                        200
check "1.5"  "GET /ytypes/base/1.0.0/base.ytype → 200"       "$BASE/ytypes/base/1.0.0/base.ytype"            200
check "1.6"  "GET /ytypes/base/latest.ytype → 200"           "$BASE/ytypes/base/latest.ytype"                 200
check "1.7"  "GET /ytype/1.0.0/schema.json → 200"            "$BASE/ytype/1.0.0/schema.json"                 200
check "1.8"  "GET /ytype_template/1.0.0/schema.json → 200"   "$BASE/ytype_template/1.0.0/schema.json"        200
check "1.9"  "GET /agent-context/index.json → 200"           "$BASE/agent-context/index.json"                 200
check "1.10" "GET /static/css/style.css → 200"               "$BASE/static/css/style.css"                    200
check "1.11" "GET /static/js/schema-browser.js → 200"        "$BASE/static/js/schema-browser.js"             200
check "1.12" "GET /static/logos/favicon.svg → 200"           "$BASE/static/logos/favicon.svg"                200

# Spot-check every type's versioned and latest endpoints
for TYPE in audio base commit document exhibition ibase image imedia list media platform_specific url venue video vr_device x_tweet youtube_video; do
  check "1.5.$TYPE" "GET /ytypes/$TYPE/1.0.0/$TYPE.ytype → 200" \
    "$BASE/ytypes/$TYPE/1.0.0/$TYPE.ytype" 200
  check "1.6.$TYPE" "GET /ytypes/$TYPE/latest.ytype → 200" \
    "$BASE/ytypes/$TYPE/latest.ytype" 200
done

# JSON validity
check_body_json "1.4b"  "/ytypes/index.json is valid JSON"            "$BASE/ytypes/index.json"
check_body_json "1.5b"  "/ytypes/base/1.0.0/base.ytype valid JSON"    "$BASE/ytypes/base/1.0.0/base.ytype"
check_body_json "1.6b"  "/ytypes/base/latest.ytype valid JSON"        "$BASE/ytypes/base/latest.ytype"
check_body_json "1.7b"  "/ytype/1.0.0/schema.json valid JSON"         "$BASE/ytype/1.0.0/schema.json"
check_body_json "1.8b"  "/ytype_template/1.0.0/schema.json valid JSON" "$BASE/ytype_template/1.0.0/schema.json"
check_body_json "1.9b"  "/agent-context/index.json valid JSON"        "$BASE/agent-context/index.json"

# SVG check
check_body_contains "1.12b" "favicon.svg contains <svg" "$BASE/static/logos/favicon.svg" "<svg"

echo "  NOTE [1.13] 404 routing: python http.server returns its own 404 — App Engine 404 behaviour verified via app.yaml/main.py analysis in Suite 7"

echo ""
echo "Suite 1 complete: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
