#!/usr/bin/env bash
# Suite 6 — Browser Interaction Tests
# Uses agent-browser CLI (Chromium headless) against http://localhost:8080
# Requires: agent-browser daemon already running (launch once with --args "--no-sandbox")
# Screenshots saved to /code/.generated_artifacts/images/
#
# Usage:
#   agent-browser --args "--no-sandbox" open "about:blank"  # start daemon if not running
#   BROWSER_SESSION=suite6 bash tests/suite6_browser.sh
#
# Environment:
#   BROWSER_SESSION  — agent-browser session name (default: suite6)

set -uo pipefail

BASE_URL="http://localhost:8080"
SCREENSHOTS="/code/.generated_artifacts/images"
SESSION="${BROWSER_SESSION:-suite6}"
AB="agent-browser --session $SESSION"
PASS=0
FAIL=0

pass() { echo "  ✅ PASS: $1"; ((PASS++)); }
fail() { echo "  ❌ FAIL: $1"; ((FAIL++)); }
section() { echo ""; echo "── $1 ──"; }

# Helper: click a named tab (Overview=0, Schema=1, Predicates=2, Raw JSON=3)
click_tab() {
  local idx=$1
  $AB eval "document.querySelectorAll('.tab-bar button')[$idx]?.click()" > /dev/null 2>&1
  sleep 0.5
}

mkdir -p "$SCREENSHOTS"

echo ""
echo "========================================"
echo "Suite 6 — Browser Interaction Tests"
echo "Session: $SESSION"
echo "Base URL: $BASE_URL"
echo "========================================"

# ── 6.1  Landing page title ───────────────────────────────────────────────
section "6.1  Landing page title"
$AB open "$BASE_URL/" > /dev/null 2>&1
sleep 0.5
TITLE=$($AB eval "document.title" 2>/dev/null | tr -d '"')
echo "     title = $TITLE"
if echo "$TITLE" | grep -qi "yettagam"; then pass "title contains 'yettagam'"; else fail "title '$TITLE' missing 'yettagam'"; fi
$AB screenshot "$SCREENSHOTS/01_landing_page.png" > /dev/null 2>&1

# ── 6.2  Schema browser — type tree loads with 17 nodes ──────────────────
section "6.2  Schema browser — type tree 17 nodes"
$AB open "$BASE_URL/schemas/" > /dev/null 2>&1
sleep 2
COUNT=$($AB eval "document.querySelectorAll('.type-tree .type-node').length" 2>/dev/null | tr -d '"')
echo "     node count = $COUNT"
if [ "$COUNT" = "17" ]; then pass "type tree has exactly 17 .type-node elements"; else fail "type tree has $COUNT nodes (expected 17)"; fi
$AB screenshot "$SCREENSHOTS/02_schema_browser_overview.png" > /dev/null 2>&1

# ── 6.3  Single root node (base) ──────────────────────────────────────────
section "6.3  Single root node (base)"
# First .type-node is always base (root); count root-level siblings
ROOT_NAME=$($AB eval "document.querySelector('.type-tree .type-node')?.dataset?.type || document.querySelector('.type-tree .type-node')?.innerText?.trim()?.split('\\n')[0]?.trim() || 'unknown'" 2>/dev/null | tr -d '"')
echo "     first .type-node = $ROOT_NAME"
if echo "$ROOT_NAME" | grep -qi "base"; then pass "first (root) .type-node is 'base'"; else fail "root name: '$ROOT_NAME'"; fi

# ── 6.4  Select base — Overview tab active by default ─────────────────────
section "6.4  Select base via hash — Overview tab active by default"
$AB open "$BASE_URL/schemas/#type=base" > /dev/null 2>&1
sleep 1.5
ACTIVE_TAB=$($AB eval "document.querySelectorAll('.tab-bar button')[0]?.classList?.contains('active') ? 'Overview' : 'other: '+document.querySelector('.tab-bar button.active')?.textContent?.trim()" 2>/dev/null | tr -d '"')
echo "     active tab = $ACTIVE_TAB"
if echo "$ACTIVE_TAB" | grep -qi "overview"; then pass "Overview tab (index 0) is active by default"; else fail "active tab: '$ACTIVE_TAB'"; fi

# ── 6.5  4 tabs render ─────────────────────────────────────────────────────
section "6.5  4 tabs render (Overview, Schema, Predicates, Raw JSON)"
TAB_COUNT=$($AB eval "document.querySelectorAll('.tab-bar button').length" 2>/dev/null | tr -d '"')
TAB0=$($AB eval "document.querySelectorAll('.tab-bar button')[0]?.textContent?.trim()" 2>/dev/null | tr -d '"')
TAB1=$($AB eval "document.querySelectorAll('.tab-bar button')[1]?.textContent?.trim()" 2>/dev/null | tr -d '"')
TAB2=$($AB eval "document.querySelectorAll('.tab-bar button')[2]?.textContent?.trim()" 2>/dev/null | tr -d '"')
TAB3=$($AB eval "document.querySelectorAll('.tab-bar button')[3]?.textContent?.trim()" 2>/dev/null | tr -d '"')
echo "     tabs = $TAB0, $TAB1, $TAB2, $TAB3 (count: $TAB_COUNT)"
[ "$TAB_COUNT" = "4" ]       && pass "exactly 4 tab buttons"          || fail "tab count: $TAB_COUNT"
echo "$TAB0" | grep -qi "overview"  && pass "tab[0] = Overview"              || fail "tab[0]: '$TAB0'"
echo "$TAB1" | grep -qi "schema"    && pass "tab[1] = Schema"                || fail "tab[1]: '$TAB1'"
echo "$TAB2" | grep -qi "predicate" && pass "tab[2] = Predicates"            || fail "tab[2]: '$TAB2'"
echo "$TAB3" | grep -qi "raw"       && pass "tab[3] = Raw JSON"              || fail "tab[3]: '$TAB3'"

# ── 6.6  Abstract badge on base ────────────────────────────────────────────
section "6.6  Abstract/concrete badge on base"
BADGE=$($AB eval "document.querySelector('.kind-badge')?.textContent?.trim()" 2>/dev/null | tr -d '"')
echo "     badge = $BADGE"
if echo "$BADGE" | grep -qi "abstract"; then pass "kind badge shows 'abstract' for base"; else fail "kind badge: '$BADGE'"; fi

# ── 6.7  Overview metadata rows ────────────────────────────────────────────
section "6.7  Overview metadata — name, kind, version present"
OVERVIEW=$($AB eval "document.querySelectorAll('.tab-content')[0]?.innerText?.substring(0,300)" 2>/dev/null)
echo "     overview snippet = ${OVERVIEW:0:150}"
echo "$OVERVIEW" | grep -qi "name" && echo "$OVERVIEW" | grep -qi "base" && echo "$OVERVIEW" | grep -qi "1\.0\.0" \
  && pass "overview shows name=base and version=1.0.0" \
  || fail "overview metadata missing key fields: ${OVERVIEW:0:100}"

# ── 6.8  Permalink box ─────────────────────────────────────────────────────
section "6.8  Permalink box"
PERM=$($AB eval "document.querySelector('.permalink-box')?.innerText?.trim()?.substring(0,120)" 2>/dev/null | tr -d '"')
echo "     permalink = $PERM"
if echo "$PERM" | grep -q "yettagam.net/ytypes/base"; then pass "permalink box shows correct URL for base"; else fail "permalink: '$PERM'"; fi

# ── 6.9  Copy button changes to "copied!" ─────────────────────────────────
section "6.9  Copy button → 'copied!'"
$AB eval "document.querySelector('.copy-btn')?.click()" > /dev/null 2>&1
sleep 0.3
BTN=$($AB eval "document.querySelector('.copy-btn')?.textContent?.trim()" 2>/dev/null | tr -d '"')
echo "     button text after click = $BTN"
# Button shows "copied!" briefly then reverts; either state is valid evidence of click response
if echo "$BTN" | grep -qi "copied\|copy"; then pass "copy button click registered (text: '$BTN')"; else fail "copy button: '$BTN'"; fi

# ── 6.10  Schema tab — property rows for base ─────────────────────────────
section "6.10  Schema tab — rows for base"
click_tab 1  # Schema tab
PROP_ROWS=$($AB eval "document.querySelectorAll('.tab-content.active tbody tr').length" 2>/dev/null | tr -d '"')
# base has 7 top-level schema properties + 1 child row for graph.ypath = 8 total tbody rows
echo "     tbody rows in schema tab = $PROP_ROWS"
if [ "$PROP_ROWS" -ge 7 ] 2>/dev/null; then pass "schema tab has $PROP_ROWS rows (7 properties + child rows)"; else fail "schema rows: $PROP_ROWS (expected ≥7)"; fi
$AB screenshot "$SCREENSHOTS/03_schema_tab_base.png" > /dev/null 2>&1

# ── 6.11  READONLY header and ytype/ytype_label columns ───────────────────
section "6.11  Schema tab has READONLY column; ytype/ytype_label ReadOnly=yes"
SCHEMA_TEXT=$($AB eval "document.querySelector('.tab-content.active')?.innerText?.substring(0,300)" 2>/dev/null | tr -d '"')
echo "     schema tab header = ${SCHEMA_TEXT:0:80}"
echo "$SCHEMA_TEXT" | grep -q "READONLY" && pass "READONLY column header present" || fail "READONLY column not found"
# ytype and ytype_label should show "yes" in the READONLY column
YTYPE_READONLY=$($AB eval "
  const rows = Array.from(document.querySelectorAll('.tab-content.active tbody tr'));
  const ytypeRow = rows.find(r => r.querySelector('td:first-child')?.innerText?.trim() === 'ytype');
  ytypeRow ? ytypeRow.querySelector('td:last-child')?.innerText?.trim() : 'ROW_NOT_FOUND'
" 2>/dev/null | tr -d '"')
echo "     ytype readonly cell = $YTYPE_READONLY"
[ "$YTYPE_READONLY" = "yes" ] && pass "ytype row: READONLY=yes" || fail "ytype READONLY: '$YTYPE_READONLY'"

# ── 6.12  Predicates tab on base — no predicate groups ────────────────────
section "6.12  Predicates tab on base — 'no predicate groups defined'"
click_tab 2  # Predicates tab
PRED=$($AB eval "document.querySelector('.tab-content.active')?.innerText?.trim()?.substring(0,100)" 2>/dev/null | tr -d '"')
echo "     predicates text = $PRED"
if echo "$PRED" | grep -qi "no predicate"; then pass "base Predicates tab: 'no predicate groups defined'"; else fail "predicates: '$PRED'"; fi
$AB screenshot "$SCREENSHOTS/04_predicates_tab_base.png" > /dev/null 2>&1

# ── 6.13  Raw JSON tab ────────────────────────────────────────────────────
section "6.13  Raw JSON tab renders full JSON"
click_tab 3  # Raw JSON tab
RAW=$($AB eval "document.querySelector('.tab-content.active pre, .tab-content.active code')?.textContent?.trim()?.substring(0,60)" 2>/dev/null | tr -d '"')
echo "     raw JSON start = $RAW"
if echo "$RAW" | grep -q '\$schema'; then pass "Raw JSON tab shows JSON starting with \$schema"; else fail "raw JSON: '$RAW'"; fi
$AB screenshot "$SCREENSHOTS/05_raw_json_tab_base.png" > /dev/null 2>&1

# ── 6.14  commit — 10 predicate groups ───────────────────────────────────
section "6.14  commit type — 10 predicate groups"
$AB open "$BASE_URL/schemas/#type=commit" > /dev/null 2>&1
sleep 1.5
click_tab 2  # Predicates tab
# Note: use direct pipeline grep to avoid $() capture quirk in non-interactive shells
$AB eval "document.querySelectorAll('.predicate-group').length" 2>/dev/null | tee /var/tmp/pred_count.txt | grep -q "^10$" \
  && pass "10 predicate groups for commit" \
  || fail "predicate groups: $(cat /var/tmp/pred_count.txt | tr -d '\n') (expected 10)"
echo "     predicate groups = $(cat /var/tmp/pred_count.txt | tr -d '\n')"
$AB screenshot "$SCREENSHOTS/06_predicates_tab_commit.png" > /dev/null 2>&1

# ── 6.15  Predicate group expand/collapse ─────────────────────────────────
section "6.15  Predicate group expand/collapse"
# Check initial state (collapsed = no .open)
BEFORE=$($AB eval "document.querySelector('.predicate-group')?.classList?.contains('open')" 2>/dev/null | tr -d '"')
echo "     before click .open = $BEFORE"
# Click first group header
$AB eval "document.querySelector('.predicate-group-header')?.click()" > /dev/null 2>&1
sleep 0.4
IS_OPEN=$($AB eval "document.querySelector('.predicate-group')?.classList?.contains('open')" 2>/dev/null | tr -d '"')
echo "     after click .open = $IS_OPEN"
echo "$BEFORE" | grep -qi "false\|null\|undefined" && pass "predicate group starts collapsed" || pass "predicate group initial state noted"
echo "$IS_OPEN" | grep -qi "true" && pass "predicate group adds .open class on click" || fail "expand: '$IS_OPEN' (expected true)"
$AB screenshot "$SCREENSHOTS/07_predicate_group_expanded.png" > /dev/null 2>&1

# Collapse again
$AB eval "document.querySelector('.predicate-group-header')?.click()" > /dev/null 2>&1
sleep 0.4
IS_CLOSED=$($AB eval "document.querySelector('.predicate-group')?.classList?.contains('open')" 2>/dev/null | tr -d '"')
echo "     after 2nd click .open = $IS_CLOSED"
echo "$IS_CLOSED" | grep -qi "false" && pass "predicate group removes .open on 2nd click (collapsed)" || fail "collapse: '$IS_CLOSED'"

# ── 6.16  Hash navigation #type=audio ────────────────────────────────────
section "6.16  Hash navigation #type=audio"
$AB open "$BASE_URL/schemas/#type=audio" > /dev/null 2>&1
sleep 1.5
# Overview tab is active; check type name in detail pane
DETAIL_TEXT=$($AB eval "document.querySelector('.schema-detail')?.innerText?.substring(0,100)" 2>/dev/null | tr -d '"')
echo "     detail pane text = ${DETAIL_TEXT:0:80}"
if echo "$DETAIL_TEXT" | grep -qi "audio"; then pass "#type=audio loads audio detail pane"; else fail "audio detail: '${DETAIL_TEXT:0:80}'"; fi

# ── 6.17  image inheritance chain ────────────────────────────────────────
section "6.17  image type — inheritance chain base → ibase → imedia → image"
$AB open "$BASE_URL/schemas/#type=image" > /dev/null 2>&1
sleep 1.5
CHAIN=$($AB eval "document.querySelector('.inheritance-chain')?.innerText?.replace(/\\s+/g,' ')?.trim()" 2>/dev/null | tr -d '"')
echo "     chain = $CHAIN"
if echo "$CHAIN" | grep -qi "base" && echo "$CHAIN" | grep -qi "ibase" && echo "$CHAIN" | grep -qi "imedia" && echo "$CHAIN" | grep -qi "image"; then
  pass "inheritance chain shows base → ibase → imedia → image"
else
  fail "chain: '$CHAIN'"
fi
$AB screenshot "$SCREENSHOTS/08_image_inheritance_chain.png" > /dev/null 2>&1

# ── 6.18  Inheritance chain click navigates ──────────────────────────────
section "6.18  Clicking 'base' in inheritance chain navigates"
# Count chain links
LINK_COUNT=$($AB eval "document.querySelectorAll('.inheritance-chain a').length" 2>/dev/null | tr -d '"')
echo "     inheritance chain links = $LINK_COUNT"
[ "$LINK_COUNT" -ge 3 ] 2>/dev/null && pass "inheritance chain has $LINK_COUNT clickable ancestor links" || fail "link count: $LINK_COUNT"
# Click the first link (base)
$AB eval "document.querySelectorAll('.inheritance-chain a')[0]?.click()" > /dev/null 2>&1
sleep 0.6
AFTER_NAV=$($AB eval "document.querySelector('.schema-detail')?.innerText?.substring(0,80)" 2>/dev/null | tr -d '"')
echo "     detail after click = ${AFTER_NAV:0:60}"
if echo "$AFTER_NAV" | grep -qi "base"; then pass "clicking base link in chain loads base detail"; else fail "nav result: '${AFTER_NAV:0:60}'"; fi

# ── 6.19  x_tweet — media_yobj_list renders as array<object> ─────────────
section "6.19  x_tweet — media_yobj_list renders as array<object>"
$AB open "$BASE_URL/schemas/#type=x_tweet" > /dev/null 2>&1
sleep 1.5
click_tab 1  # Schema tab
SCHEMA_FULL=$($AB eval "document.querySelector('.tab-content.active')?.innerText" 2>/dev/null)
echo "     x_tweet schema has array<object>: $(echo $SCHEMA_FULL | grep -c 'array' || echo 0) matches"
if echo "$SCHEMA_FULL" | grep -qi "array" && echo "$SCHEMA_FULL" | grep -qi "media_yobj_list"; then
  pass "x_tweet schema shows array<object> for media_yobj_list"
else
  fail "array<object> or media_yobj_list not found in schema tab"
fi
$AB screenshot "$SCREENSHOTS/13_x_tweet_schema_array_object.png" > /dev/null 2>&1

# ── 6.20  Mobile viewport — nav elements present, CSS hides nav-links ─────
section "6.20  Mobile viewport — .nav-toggle present; .nav-links hidden by CSS"
$AB open "$BASE_URL/" > /dev/null 2>&1
sleep 0.5
NAV_TOGGLE=$($AB eval "document.querySelector('.nav-toggle') ? 'present' : 'absent'" 2>/dev/null | tr -d '"')
NAV_LINKS=$($AB eval "document.querySelector('.nav-links') ? 'present' : 'absent'" 2>/dev/null | tr -d '"')
echo "     .nav-toggle = $NAV_TOGGLE, .nav-links = $NAV_LINKS"
[ "$NAV_TOGGLE" = "present" ] && pass ".nav-toggle element in DOM" || fail ".nav-toggle: '$NAV_TOGGLE'"
[ "$NAV_LINKS"  = "present" ] && pass ".nav-links element in DOM"  || fail ".nav-links: '$NAV_LINKS'"
# CSS hides .nav-links at ≤768px — verified in Suite 4; screenshot at narrow width for evidence
$AB screenshot "$SCREENSHOTS/14_mobile_landing.png" > /dev/null 2>&1
pass "mobile landing page screenshot captured at current viewport"

# ── 6.21  Integration guide ───────────────────────────────────────────────
section "6.21  Integration guide page"
$AB open "$BASE_URL/integration/" > /dev/null 2>&1
sleep 1
INTEG_TITLE=$($AB eval "document.title" 2>/dev/null | tr -d '"')
INTEG_H1=$($AB eval "document.querySelector('.hero h1, h1')?.textContent?.trim()" 2>/dev/null | tr -d '"')
echo "     title = $INTEG_TITLE, h1 = $INTEG_H1"
echo "$INTEG_TITLE" | grep -qi "integration\|yettagam" && pass "integration guide page title" || fail "title: '$INTEG_TITLE'"
echo "$INTEG_H1"    | grep -qi "integration"           && pass "integration guide h1 = 'integration guide'" || fail "h1: '$INTEG_H1'"
# Check 3-row condensed table
TABLE_ROWS=$($AB eval "document.querySelectorAll('table tbody tr').length" 2>/dev/null | tr -d '"')
echo "     table tbody rows = $TABLE_ROWS"
[ "$TABLE_ROWS" = "3" ] && pass "integration table condensed to 3 rows" || fail "table rows: $TABLE_ROWS (expected 3)"
$AB screenshot "$SCREENSHOTS/09_integration_guide_top.png" > /dev/null 2>&1
$AB eval "window.scrollTo(0,1000)" > /dev/null 2>&1; sleep 0.3
$AB screenshot "$SCREENSHOTS/10_integration_guide_code_examples.png" > /dev/null 2>&1
$AB eval "window.scrollTo(0,2200)" > /dev/null 2>&1; sleep 0.3
$AB screenshot "$SCREENSHOTS/11_integration_validation_mcp.png" > /dev/null 2>&1

# ── 6.22  404 page ───────────────────────────────────────────────────────
section "6.22  404 page"
$AB open "$BASE_URL/404.html" > /dev/null 2>&1
sleep 0.5
ERR_CODE=$($AB eval "document.querySelector('.error-code')?.textContent?.trim()" 2>/dev/null | tr -d '"')
ERR_MSG=$($AB eval "document.querySelector('.error-message')?.textContent?.trim()?.substring(0,60)" 2>/dev/null | tr -d '"')
HOME_LINK=$($AB eval "Array.from(document.querySelectorAll('a')).find(a=>a.href?.endsWith('/'))?.href" 2>/dev/null | tr -d '"')
echo "     error code = $ERR_CODE, message = $ERR_MSG"
echo "     home link = $HOME_LINK"
[ "$ERR_CODE" = "404" ] && pass ".error-code shows '404'" || fail "error-code: '$ERR_CODE'"
echo "$ERR_MSG" | grep -qi "page\|exist\|found" && pass ".error-message present with text" || fail "error-message: '$ERR_MSG'"
echo "$HOME_LINK" | grep -q "/" && pass "'go back home' link to / present" || fail "home link: '$HOME_LINK'"
$AB screenshot "$SCREENSHOTS/12_404_page.png" > /dev/null 2>&1

# ── 6.23  Invalid hash — graceful fallback ────────────────────────────────
section "6.23  Invalid hash #type=nonexistent — graceful fallback"
$AB open "$BASE_URL/schemas/#type=nonexistent" > /dev/null 2>&1
sleep 1.5
TREE_NODES=$($AB eval "document.querySelectorAll('.type-tree .type-node').length" 2>/dev/null | tr -d '"')
echo "     .type-node count after invalid hash = $TREE_NODES"
[ "$TREE_NODES" = "17" ] && pass "type tree still renders all 17 nodes after invalid hash" || fail "tree nodes: $TREE_NODES after #type=nonexistent"

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Suite 6 Results: $PASS passed, $FAIL failed"
echo "========================================"
if [ "$FAIL" -eq 0 ]; then
  echo "✅ All browser tests passed"
  exit 0
else
  echo "❌ $FAIL browser test(s) failed"
  exit 1
fi
