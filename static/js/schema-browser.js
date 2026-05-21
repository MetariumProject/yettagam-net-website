(async function () {
  'use strict';

  // =========================================================================
  // State
  // =========================================================================
  const typeCache = new Map();
  let typeIndex = [];
  let typeMap = {};        // name → index entry
  let childrenMap = {};    // parentName → [childEntries]
  let rootTypes = [];      // types with no parent

  // =========================================================================
  // DOM references
  // =========================================================================
  const treeEl = document.querySelector('.type-tree');
  const detailEl = document.querySelector('.schema-detail');

  // =========================================================================
  // 1. Fetch type index
  // =========================================================================
  try {
    const response = await fetch('/ytypes/index.json');
    const index = await response.json();
    typeIndex = index.types;
  } catch (err) {
    detailEl.innerHTML = '<p style="color:#e57373">failed to load type index</p>';
    return;
  }

  // =========================================================================
  // 2. Build inheritance tree
  // =========================================================================
  function extractParentName(path) {
    const match = path.match(/^\/ytypes\/([a-z_]+)/);
    return match ? match[1] : null;
  }

  typeIndex.forEach(function (t) { typeMap[t.name] = t; });

  // Build parent → children map
  childrenMap = {};
  rootTypes = [];

  typeIndex.forEach(function (t) {
    if (!t.inherits_from || t.inherits_from.length === 0) {
      rootTypes.push(t);
    } else {
      var parentName = extractParentName(t.inherits_from[0]);
      if (parentName) {
        if (!childrenMap[parentName]) childrenMap[parentName] = [];
        childrenMap[parentName].push(t);
      } else {
        rootTypes.push(t);
      }
    }
  });

  // =========================================================================
  // 3. Render tree
  // =========================================================================

  // Mobile select dropdown
  var mobileSelect = document.createElement('select');
  mobileSelect.className = 'tree-toggle';
  mobileSelect.innerHTML = '<option value="">— select a type —</option>';

  function addMobileOption(t, depth) {
    var opt = document.createElement('option');
    opt.value = t.name;
    opt.textContent = '\u00A0\u00A0'.repeat(depth) + t.label + ' (' + t.kind + ')';
    mobileSelect.appendChild(opt);
  }

  function renderTreeNode(type, depth) {
    var node = document.createElement('div');
    node.className = 'type-node' + (type.kind === 'abstract' ? ' abstract' : '');
    node.setAttribute('data-type', type.name);

    var labelSpan = document.createElement('span');
    labelSpan.textContent = type.label;
    node.appendChild(labelSpan);

    var badge = document.createElement('span');
    badge.className = 'kind-badge ' + type.kind;
    badge.textContent = type.kind;
    node.appendChild(badge);

    node.addEventListener('click', function (e) {
      e.stopPropagation();
      selectType(type.name);
    });

    addMobileOption(type, depth);

    var children = childrenMap[type.name];
    if (children && children.length > 0) {
      var wrapper = document.createElement('div');
      wrapper.appendChild(node);
      var childContainer = document.createElement('div');
      childContainer.className = 'type-children';
      children.forEach(function (child) {
        childContainer.appendChild(renderTreeNode(child, depth + 1));
      });
      wrapper.appendChild(childContainer);
      return wrapper;
    }

    return node;
  }

  treeEl.insertAdjacentElement('beforebegin', mobileSelect);

  rootTypes.forEach(function (type) {
    treeEl.appendChild(renderTreeNode(type, 0));
  });

  mobileSelect.addEventListener('change', function () {
    if (this.value) selectType(this.value);
  });

  // =========================================================================
  // 4. Type selection
  // =========================================================================
  async function selectType(name) {
    // Mark active in tree
    treeEl.querySelectorAll('.type-node').forEach(function (n) {
      n.classList.remove('active');
    });
    var activeNode = treeEl.querySelector('.type-node[data-type="' + name + '"]');
    if (activeNode) activeNode.classList.add('active');

    // Update mobile select
    mobileSelect.value = name;

    // Update hash
    location.hash = '#type=' + name;

    // Show loading
    detailEl.innerHTML = '<p style="color:var(--text-muted)">loading…</p>';

    // Fetch type data
    var typeData = await fetchType(name);
    if (!typeData) {
      detailEl.innerHTML = '<p style="color:#e57373">failed to load type data</p>';
      return;
    }

    renderDetail(typeData);
  }

  async function fetchType(name) {
    if (typeCache.has(name)) return typeCache.get(name);

    var entry = typeMap[name];
    if (!entry) return null;

    // Convert permalink to relative URL for same-origin fetch
    var url = entry.permalink.replace('https://yettagam.net', '');

    try {
      var resp = await fetch(url);
      var data = await resp.json();
      typeCache.set(name, data);
      return data;
    } catch (e) {
      console.error('Failed to fetch type:', name, e);
      return null;
    }
  }

  // =========================================================================
  // 5. Detail rendering
  // =========================================================================
  function renderDetail(typeData) {
    var html = '';

    // Tab bar
    html += '<div class="tab-bar">';
    html += '<button class="active" data-tab="overview">Overview</button>';
    html += '<button data-tab="schema">Schema</button>';
    html += '<button data-tab="predicates">Predicates</button>';
    html += '<button data-tab="raw">Raw JSON</button>';
    html += '</div>';

    // Overview tab
    html += '<div class="tab-content active" data-tab-content="overview">';
    html += renderOverview(typeData);
    html += '</div>';

    // Schema tab
    html += '<div class="tab-content" data-tab-content="schema">';
    html += renderSchema(typeData);
    html += '</div>';

    // Predicates tab
    html += '<div class="tab-content" data-tab-content="predicates">';
    html += renderPredicates(typeData);
    html += '</div>';

    // Raw JSON tab
    html += '<div class="tab-content" data-tab-content="raw">';
    html += '<pre><code>' + escapeHtml(JSON.stringify(typeData, null, 2)) + '</code></pre>';
    html += '</div>';

    detailEl.innerHTML = html;

    // Tab switching
    detailEl.querySelectorAll('.tab-bar button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        detailEl.querySelectorAll('.tab-bar button').forEach(function (b) { b.classList.remove('active'); });
        detailEl.querySelectorAll('.tab-content').forEach(function (c) { c.classList.remove('active'); });
        btn.classList.add('active');
        var target = detailEl.querySelector('[data-tab-content="' + btn.getAttribute('data-tab') + '"]');
        if (target) target.classList.add('active');
      });
    });

    // Inheritance chain click handlers
    detailEl.querySelectorAll('.inheritance-chain a[data-type-link]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        selectType(this.getAttribute('data-type-link'));
      });
    });

    // Copy button
    var copyBtn = detailEl.querySelector('.copy-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        var text = this.getAttribute('data-copy');
        navigator.clipboard.writeText(text).then(function () {
          copyBtn.textContent = 'copied!';
          setTimeout(function () { copyBtn.textContent = 'copy'; }, 1500);
        }).catch(function () {
          // Fallback
          var ta = document.createElement('textarea');
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          copyBtn.textContent = 'copied!';
          setTimeout(function () { copyBtn.textContent = 'copy'; }, 1500);
        });
      });
    }

    // Predicate group toggles
    detailEl.querySelectorAll('.predicate-group-header').forEach(function (header) {
      header.addEventListener('click', function () {
        this.parentElement.classList.toggle('open');
      });
    });
  }

  // =========================================================================
  // Overview tab
  // =========================================================================
  function renderOverview(typeData) {
    var html = '';

    // Metadata card
    html += '<div class="card" style="margin-bottom:1rem">';
    html += '<h3>' + escapeHtml(typeData.label || typeData.name) + '</h3>';
    html += '<p>' + escapeHtml(typeData.description || '') + '</p>';
    html += '<table>';
    html += '<tr><td><strong>name</strong></td><td><code>' + escapeHtml(typeData.name) + '</code></td></tr>';
    html += '<tr><td><strong>kind</strong></td><td><span class="kind-badge ' + typeData.kind + '">' + typeData.kind + '</span></td></tr>';
    html += '<tr><td><strong>version</strong></td><td>' + escapeHtml(typeData.$version || '') + '</td></tr>';
    html += '<tr><td><strong>final</strong></td><td>' + (typeData.final ? 'yes' : 'no') + '</td></tr>';
    html += '<tr><td><strong>singleton</strong></td><td>' + (typeData.singleton ? 'yes' : 'no') + '</td></tr>';
    html += '</table>';
    html += '</div>';

    // Inheritance chain
    var chain = resolveInheritanceChain(typeData.name);
    html += '<h4>inheritance chain</h4>';
    html += '<div class="inheritance-chain">';
    chain.forEach(function (cName, i) {
      if (i > 0) html += '<span class="arrow">→</span>';
      if (cName === typeData.name) {
        html += '<strong>' + escapeHtml(cName) + '</strong>';
      } else {
        html += '<a href="#type=' + cName + '" data-type-link="' + cName + '">' + escapeHtml(cName) + '</a>';
      }
    });
    html += '</div>';

    // Permalink box
    var entry = typeMap[typeData.name];
    var permalink = entry ? entry.permalink : '';
    html += '<h4>permalink</h4>';
    html += '<div class="permalink-box">';
    html += '<span>' + escapeHtml(permalink) + '</span>';
    html += '<button class="copy-btn" data-copy="' + escapeHtml(permalink) + '">copy</button>';
    html += '</div>';

    return html;
  }

  function resolveInheritanceChain(name) {
    var chain = [];
    var visited = new Set();
    var current = name;

    // Walk up from the current type to root
    while (current && !visited.has(current)) {
      visited.add(current);
      chain.unshift(current);
      var entry = typeMap[current];
      if (!entry || !entry.inherits_from || entry.inherits_from.length === 0) break;
      current = extractParentName(entry.inherits_from[0]);
    }

    return chain;
  }

  // =========================================================================
  // Schema tab
  // =========================================================================
  function renderSchema(typeData) {
    var schema = typeData.schema;
    if (!schema || !schema.properties) {
      return '<p>no schema properties defined for this type</p>';
    }

    var requiredArr = schema.required || [];
    var html = '<table class="property-table">';
    html += '<thead><tr><th>Name</th><th>Type</th><th>Description</th><th>Required</th><th>ReadOnly</th></tr></thead>';
    html += '<tbody>';
    html += renderPropertyRows(schema.properties, requiredArr, 0);
    html += '</tbody></table>';
    return html;
  }

  function renderPropertyRows(properties, requiredArr, depth) {
    var html = '';
    var indent = depth > 0 ? 'padding-left:' + (depth * 1.5) + 'rem;' : '';

    Object.keys(properties).forEach(function (propName) {
      var prop = properties[propName];
      var typeStr = prop.type || '';

      // For array types, show items type inline
      if (typeStr === 'array' && prop.items) {
        if (prop.items.type === 'object') {
          typeStr = 'array&lt;object&gt;';
        } else {
          typeStr = 'array&lt;' + escapeHtml(prop.items.type || 'any') + '&gt;';
        }
      }

      var isRequired = requiredArr.includes(propName);
      var isReadOnly = prop.readOnly === true;

      html += '<tr>';
      html += '<td style="' + indent + '"><code>' + escapeHtml(propName) + '</code></td>';
      html += '<td>' + typeStr + '</td>';
      html += '<td>' + escapeHtml(prop.description || '') + '</td>';
      html += '<td>' + (isRequired ? '<span class="badge" style="background:rgba(40,167,69,0.2);color:#28a745">yes</span>' : 'no') + '</td>';
      html += '<td>' + (isReadOnly ? '<span class="badge" style="background:rgba(255,193,7,0.2);color:#ffc107">yes</span>' : 'no') + '</td>';
      html += '</tr>';

      // Nested object properties (up to 2 levels)
      if (prop.type === 'object' && prop.properties && depth < 2) {
        html += renderPropertyRows(prop.properties, prop.required || [], depth + 1);
      }

      // Array items with object properties (up to 2 levels)
      if (prop.type === 'array' && prop.items && prop.items.type === 'object' && prop.items.properties && depth < 2) {
        html += renderPropertyRows(prop.items.properties, prop.items.required || [], depth + 1);
      }
    });

    return html;
  }

  // =========================================================================
  // Predicates tab
  // =========================================================================
  function renderPredicates(typeData) {
    var groups = (typeData.definition && typeData.definition.predicateGroups)
      || (typeData.definition && typeData.definition.logic && typeData.definition.logic.predicateGroups)
      || {};

    var groupKeys = Object.keys(groups);
    if (groupKeys.length === 0) {
      return '<p>no predicate groups defined for this type</p>';
    }

    var html = '';
    groupKeys.forEach(function (groupKey) {
      var group = groups[groupKey];
      html += '<div class="predicate-group">';
      html += '<div class="predicate-group-header">';
      html += '<div>';
      html += '<strong>' + escapeHtml(group.label || groupKey) + '</strong>';
      if (group.description) {
        html += '<br><span style="font-size:0.85rem;color:var(--text-muted)">' + escapeHtml(group.description) + '</span>';
      }
      html += '</div>';
      html += '</div>';

      html += '<div class="predicate-group-body">';
      var predicates = group.predicates || {};
      var predKeys = Object.keys(predicates);

      if (predKeys.length === 0) {
        html += '<p style="color:var(--text-muted);font-size:0.9rem">no predicates in this group</p>';
      } else {
        predKeys.forEach(function (predName) {
          var pred = predicates[predName];
          html += '<div style="padding:0.5rem 0;border-bottom:1px solid var(--border)">';
          html += '<code>' + escapeHtml(groupKey + ':' + predName) + '</code>';

          // Badges for boolean properties
          var booleanProps = ['symmetric', 'transitive', 'reflexive', 'functional', 'inverseFunctional', 'asymmetric', 'irreflexive'];
          booleanProps.forEach(function (bp) {
            // Check top-level and nested properties
            if (pred[bp] === true || (pred.properties && pred.properties[bp] === true)) {
              html += ' <span class="badge">' + bp + '</span>';
            }
          });

          if (pred.inverse) {
            html += ' <span class="badge" style="background:rgba(126,200,227,0.15);color:var(--accent)">inverse: ' + escapeHtml(String(pred.inverse)) + '</span>';
          }

          html += '<br><span style="font-size:0.85rem;color:var(--text-muted)">' + escapeHtml(pred.description || '') + '</span>';
          html += '</div>';
        });
      }

      html += '</div>';
      html += '</div>';
    });

    return html;
  }

  // =========================================================================
  // Utilities
  // =========================================================================
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // =========================================================================
  // 6. URL hash navigation
  // =========================================================================
  function getHashType() {
    var hash = location.hash;
    var match = hash.match(/^#type=([a-z_]+)/);
    return match ? match[1] : null;
  }

  window.addEventListener('hashchange', function () {
    var name = getHashType();
    if (name && typeMap[name]) {
      selectType(name);
    }
  });

  // Initial selection
  var initialType = getHashType();
  if (initialType && typeMap[initialType]) {
    selectType(initialType);
  } else {
    selectType('base');
  }
})();
