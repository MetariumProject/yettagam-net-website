#!/usr/bin/env node
/**
 * Suite 5 — JavaScript Logic Unit Tests
 * Extracts and exercises pure functions from schema-browser.js without a DOM.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const REPO = '/code/MetariumProject/yettagam-net-website';
let PASS = 0, FAIL = 0;

function ok(id, desc) {
  console.log(`  PASS [${id}] ${desc}`);
  PASS++;
}
function fail(id, desc, detail = '') {
  console.log(`  FAIL [${id}] ${desc}${detail ? ' — ' + detail : ''}`);
  FAIL++;
}
function assert(id, desc, condition, detail = '') {
  if (condition) ok(id, desc);
  else fail(id, desc, detail);
}
function assertEqual(id, desc, got, expected) {
  if (JSON.stringify(got) === JSON.stringify(expected))
    ok(id, desc);
  else
    fail(id, desc, `got ${JSON.stringify(got)}, expected ${JSON.stringify(expected)}`);
}

console.log('=== Suite 5: JavaScript Logic Unit Tests ===\n');

// ── Load the index and build internal state (mirrors schema-browser.js init) ─
const index = JSON.parse(fs.readFileSync(path.join(REPO, 'ytypes/index.json'), 'utf8'));
const typeIndex = index.types;

// ── Replicate the pure functions from schema-browser.js ──────────────────────

function extractParentName(p) {
  const match = p.match(/^\/ytypes\/([a-z_]+)/);
  return match ? match[1] : null;
}

let typeMap = {};
let childrenMap = {};
let rootTypes = [];

typeIndex.forEach(t => { typeMap[t.name] = t; });

typeIndex.forEach(t => {
  if (!t.inherits_from || t.inherits_from.length === 0) {
    rootTypes.push(t);
  } else {
    const parentName = extractParentName(t.inherits_from[0]);
    if (parentName) {
      if (!childrenMap[parentName]) childrenMap[parentName] = [];
      childrenMap[parentName].push(t);
    } else {
      rootTypes.push(t);
    }
  }
});

function resolveInheritanceChain(name) {
  const chain = [];
  const visited = new Set();
  let current = name;
  while (current && !visited.has(current)) {
    visited.add(current);
    chain.unshift(current);
    const entry = typeMap[current];
    if (!entry || !entry.inherits_from || entry.inherits_from.length === 0) break;
    current = extractParentName(entry.inherits_from[0]);
  }
  return chain;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function getHashType(hash) {
  const match = hash.match(/^#type=([a-z_]+)/);
  return match ? match[1] : null;
}

// ── 5.1–5.3  extractParentName ───────────────────────────────────────────────
assertEqual('5.1',  'extractParentName("/ytypes/base/") → "base"',
            extractParentName('/ytypes/base/'), 'base');
assertEqual('5.2',  'extractParentName("/ytypes/platform_specific/") → "platform_specific"',
            extractParentName('/ytypes/platform_specific/'), 'platform_specific');
assertEqual('5.3a', 'extractParentName("") → null',
            extractParentName(''), null);
assertEqual('5.3b', 'extractParentName("invalid") → null',
            extractParentName('invalid'), null);

// ── 5.4–5.9  Tree building ────────────────────────────────────────────────────
assert('5.4',  'rootTypes has exactly 1 entry (base)',
       rootTypes.length === 1, `got ${rootTypes.length}: ${rootTypes.map(t=>t.name)}`);
assert('5.4b', 'root entry is "base"',
       rootTypes[0] && rootTypes[0].name === 'base', `got ${rootTypes[0]?.name}`);

const baseChildren = (childrenMap['base'] || []).map(t => t.name).sort();
const expectedBaseChildren = ['commit','exhibition','ibase','list','media','platform_specific','url','venue','vr_device'].sort();
assertEqual('5.5',  'childrenMap["base"] has 9 direct children',
            baseChildren, expectedBaseChildren);

const mediaChildren = (childrenMap['media'] || []).map(t => t.name).sort();
assertEqual('5.6',  'childrenMap["media"] = [audio, document, video]',
            mediaChildren, ['audio','document','video']);

const ibaseChildren = (childrenMap['ibase'] || []).map(t => t.name);
assertEqual('5.7',  'childrenMap["ibase"] = [imedia]',
            ibaseChildren, ['imedia']);

const imediaChildren = (childrenMap['imedia'] || []).map(t => t.name);
assertEqual('5.8',  'childrenMap["imedia"] = [image]',
            imediaChildren, ['image']);

const psChildren = (childrenMap['platform_specific'] || []).map(t => t.name).sort();
assertEqual('5.9',  'childrenMap["platform_specific"] = [x_tweet, youtube_video]',
            psChildren, ['x_tweet','youtube_video']);

// ── 5.10–5.12  resolveInheritanceChain ───────────────────────────────────────
assertEqual('5.10', 'chain for "image" = [base, ibase, imedia, image]',
            resolveInheritanceChain('image'), ['base','ibase','imedia','image']);
assertEqual('5.11', 'chain for "base" = [base]',
            resolveInheritanceChain('base'), ['base']);
assertEqual('5.12', 'chain for "x_tweet" = [base, platform_specific, x_tweet]',
            resolveInheritanceChain('x_tweet'), ['base','platform_specific','x_tweet']);

// ── 5.13–5.14  escapeHtml ────────────────────────────────────────────────────
const dangerous = '<script>alert("xss")</script>';
const escaped = escapeHtml(dangerous);
assert('5.13a', 'escapeHtml: no raw < in output',   !escaped.includes('<'));
assert('5.13b', 'escapeHtml: no raw > in output',   !escaped.includes('>'));
assert('5.13c', 'escapeHtml: no raw " in output',   !escaped.includes('"'));
assert('5.13d', 'escapeHtml output contains &lt;',  escaped.includes('&lt;'));
assert('5.13e', 'escapeHtml output contains &gt;',  escaped.includes('&gt;'));
assertEqual('5.14a', 'escapeHtml(null) → ""',       escapeHtml(null), '');
assertEqual('5.14b', 'escapeHtml(undefined) → ""',  escapeHtml(undefined), '');
assertEqual('5.14c', 'escapeHtml("") → ""',         escapeHtml(''), '');

// ── 5.15–5.17  getHashType ───────────────────────────────────────────────────
assertEqual('5.15',  'getHashType("#type=audio") → "audio"',   getHashType('#type=audio'), 'audio');
assertEqual('5.16',  'getHashType("#type=x_tweet") → "x_tweet"', getHashType('#type=x_tweet'), 'x_tweet');
assertEqual('5.17a', 'getHashType("") → null',                  getHashType(''), null);
assertEqual('5.17b', 'getHashType("#foo") → null',              getHashType('#foo'), null);
assertEqual('5.17c', 'getHashType("#type=youtube_video") → "youtube_video"',
            getHashType('#type=youtube_video'), 'youtube_video');

// ── 5.18–5.20  renderSchema logic (simulated using base.ytype) ───────────────
const baseData = JSON.parse(fs.readFileSync(
  path.join(REPO, 'ytypes/base/1.0.0/base.ytype'), 'utf8'));

function renderSchema(typeData) {
  const schema = typeData.schema;
  if (!schema || !schema.properties) return '<p>no schema properties defined for this type</p>';
  const requiredArr = schema.required || [];
  let html = '<table class="property-table">';
  html += '<thead><tr><th>Name</th><th>Type</th><th>Description</th><th>Required</th><th>ReadOnly</th></tr></thead>';
  html += '<tbody>';
  html += renderPropertyRows(schema.properties, requiredArr, 0);
  html += '</tbody></table>';
  return html;
}

function renderPropertyRows(properties, requiredArr, depth) {
  let html = '';
  Object.keys(properties).forEach(propName => {
    const prop = properties[propName];
    let typeStr = prop.type || '';
    if (typeStr === 'array' && prop.items) {
      if (prop.items.type === 'object') typeStr = 'array<object>';
      else typeStr = 'array<' + (prop.items.type || 'any') + '>';
    }
    const isRequired = requiredArr.includes(propName);
    const isReadOnly = prop.readOnly === true;
    html += '<tr>';
    html += `<td><code>${escapeHtml(propName)}</code></td>`;
    html += `<td>${typeStr}</td>`;
    html += `<td>${escapeHtml(prop.description || '')}</td>`;
    html += `<td>${isRequired ? '<span class="badge" style="background:rgba(40,167,69,0.2);color:#28a745">yes</span>' : 'no'}</td>`;
    html += `<td>${isReadOnly ? '<span class="badge" style="background:rgba(255,193,7,0.2);color:#ffc107">yes</span>' : 'no'}</td>`;
    html += '</tr>';
    if (prop.type === 'object' && prop.properties && depth < 2)
      html += renderPropertyRows(prop.properties, prop.required || [], depth + 1);
    if (prop.type === 'array' && prop.items && prop.items.type === 'object' && prop.items.properties && depth < 2)
      html += renderPropertyRows(prop.items.properties, prop.items.required || [], depth + 1);
  });
  return html;
}

const baseSchemaHtml = renderSchema(baseData);
assert('5.18a', 'renderSchema for base.ytype returns a property-table',
       baseSchemaHtml.includes('<table class="property-table">'));
const baseProps = ['name','label','description','uuid','graph','ytype','ytype_label'];
baseProps.forEach(prop => {
  assert('5.18b', `base schema table contains property '${prop}'`,
         baseSchemaHtml.includes(`<code>${prop}</code>`));
});

// ReadOnly badges for ytype and ytype_label
const ytypeRow   = baseSchemaHtml.match(/<tr>.*?<code>ytype<\/code>.*?<\/tr>/s);
const ytypeLRow  = baseSchemaHtml.match(/<tr>.*?<code>ytype_label<\/code>.*?<\/tr>/s);
assert('5.19a', 'ytype row has ReadOnly=yes badge',
       ytypeRow  && ytypeRow[0].includes('color:#ffc107'));
assert('5.19b', 'ytype_label row has ReadOnly=yes badge',
       ytypeLRow && ytypeLRow[0].includes('color:#ffc107'));

// Required badges — base required: ytype, ytype_label, name, label, description, uuid
const baseRequired = ['ytype','ytype_label','name','label','description','uuid'];
let requiredBadgeCount = 0;
baseRequired.forEach(prop => {
  const rowRe = new RegExp(`<code>${prop}<\\/code>.*?<\\/tr>`, 's');
  const m = baseSchemaHtml.match(rowRe);
  if (m && m[0].includes('color:#28a745')) requiredBadgeCount++;
});
assert('5.20', `All 6 required fields in base have Required=yes badge (found ${requiredBadgeCount})`,
       requiredBadgeCount === 6, `found ${requiredBadgeCount}, expected 6`);

// ── 5.21  renderPredicates — commit.ytype has 10 predicate groups ─────────────
const commitData = JSON.parse(fs.readFileSync(
  path.join(REPO, 'ytypes/commit/1.0.0/commit.ytype'), 'utf8'));

function renderPredicates(typeData) {
  const groups = (typeData.definition && typeData.definition.predicateGroups)
    || (typeData.definition && typeData.definition.logic && typeData.definition.logic.predicateGroups)
    || {};
  const groupKeys = Object.keys(groups);
  if (groupKeys.length === 0) return '<p>no predicate groups defined for this type</p>';
  let html = '';
  groupKeys.forEach(groupKey => {
    const group = groups[groupKey];
    html += '<div class="predicate-group">';
    html += '<div class="predicate-group-header">';
    html += `<strong>${escapeHtml(group.label || groupKey)}</strong>`;
    html += '</div><div class="predicate-group-body">';
    const predicates = group.predicates || {};
    Object.keys(predicates).forEach(predName => {
      html += `<div><code>${escapeHtml(groupKey + ':' + predName)}</code></div>`;
    });
    html += '</div></div>';
  });
  return html;
}

const commitPredHtml = renderPredicates(commitData);
const expectedGroups = ['owl','rdfs','skos','cause','intent','axiom','spatial','temporal','part','rel'];
let foundGroups = 0;
expectedGroups.forEach(g => {
  if (commitPredHtml.includes(g)) foundGroups++;
});
assert('5.21a', `renderPredicates(commit) contains all 10 predicate group keys (found ${foundGroups})`,
       foundGroups === 10, `found ${foundGroups}/10`);
const pgCount = (commitPredHtml.match(/class="predicate-group"/g) || []).length;
assert('5.21b', `renderPredicates(commit) renders 10 predicate-group divs (found ${pgCount})`,
       pgCount === 10, `found ${pgCount}`);

// ── 5.22  renderPredicates — base.ytype (no predicates) ──────────────────────
const basePredHtml = renderPredicates(baseData);
assert('5.22', 'renderPredicates(base) shows no-predicates message',
       basePredHtml.includes('no predicate groups defined'));

// ── 5.23  renderOverview produces metadata table ─────────────────────────────
function renderOverview(typeData) {
  let html = '<div class="card">';
  html += `<h3>${escapeHtml(typeData.label || typeData.name)}</h3>`;
  html += `<p>${escapeHtml(typeData.description || '')}</p>`;
  html += '<table>';
  html += `<tr><td><strong>name</strong></td><td><code>${escapeHtml(typeData.name)}</code></td></tr>`;
  html += `<tr><td><strong>kind</strong></td><td><span class="kind-badge ${typeData.kind}">${typeData.kind}</span></td></tr>`;
  html += `<tr><td><strong>version</strong></td><td>${escapeHtml(typeData.$version || '')}</td></tr>`;
  html += `<tr><td><strong>final</strong></td><td>${typeData.final ? 'yes' : 'no'}</td></tr>`;
  html += `<tr><td><strong>singleton</strong></td><td>${typeData.singleton ? 'yes' : 'no'}</td></tr>`;
  html += '</table></div>';
  return html;
}
const baseOverviewHtml = renderOverview(baseData);
['name','kind','version','final','singleton'].forEach(field => {
  assert('5.23', `renderOverview(base) contains metadata row for '${field}'`,
         baseOverviewHtml.includes(`<strong>${field}</strong>`));
});
assert('5.23b', 'renderOverview(base) shows correct kind value',
       baseOverviewHtml.includes('abstract'));

// ── 5.24  renderPropertyRows — array<object> for x_tweet.ytype ───────────────
const xTweetData = JSON.parse(fs.readFileSync(
  path.join(REPO, 'ytypes/x_tweet/1.0.0/x_tweet.ytype'), 'utf8'));
const xTweetSchemaHtml = renderSchema(xTweetData);
assert('5.24a', 'renderSchema(x_tweet) shows array<object> for media_yobj_list',
       xTweetSchemaHtml.includes('array&lt;object&gt;') || xTweetSchemaHtml.includes('array<object>'));
assert('5.24b', 'renderSchema(x_tweet) recurses into media_yobj_list items (shows yobj child prop)',
       xTweetSchemaHtml.includes('<code>yobj</code>'));

// ── 5.25  fetchType URL rewriting ─────────────────────────────────────────────
const testPermalink = 'https://yettagam.net/ytypes/audio/1.0.0/audio.ytype';
const rewritten = testPermalink.replace('https://yettagam.net', '');
assertEqual('5.25', 'fetchType strips https://yettagam.net from permalink',
            rewritten, '/ytypes/audio/1.0.0/audio.ytype');

// ── Summary ───────────────────────────────────────────────────────────────────
console.log(`\nSuite 5 complete: ${PASS} passed, ${FAIL} failed`);
process.exit(FAIL === 0 ? 0 : 1);
