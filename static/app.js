'use strict';

const TYPE_COLOR = {
  droplet: '#58a6ff',
  db: '#f778ba',
  vpc: '#a371f7',
  firewall: '#f85149',
  lb: '#ffa657',
  reserved_ip: '#79c0ff',
  volume: '#56d364',
  snapshot: '#2ea043',
  domain: '#d2a8ff',
  record: '#bc8cff',
  k8s: '#1f6feb',
  app: '#fb8500',
  function_ns: '#ffd60a',
  registry: '#8b949e',
};

// ----- theme -----

function readThemeVar(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

function currentTheme() {
  return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
}

function themeColors() {
  return {
    textOutline: readThemeVar('--cy-text-outline', '#0d1117'),
    nodeBorder: readThemeVar('--cy-node-border', '#0d1117'),
    edge: readThemeVar('--cy-edge', '#30363d'),
    edgeFirewall: readThemeVar('--cy-edge-firewall', '#f85149'),
    edgeLb: readThemeVar('--cy-edge-lb', '#ffa657'),
    edgeVolume: readThemeVar('--cy-edge-volume', '#56d364'),
    edgeDns: readThemeVar('--cy-edge-dns', '#bc8cff'),
    textPrimary: readThemeVar('--text-primary', '#e6edf3'),
  };
}

const TYPE_SHAPE = {
  droplet: 'round-rectangle',
  db: 'barrel',
  vpc: 'octagon',
  firewall: 'diamond',
  lb: 'hexagon',
  reserved_ip: 'tag',
  volume: 'cylinder',
  snapshot: 'cylinder',
  domain: 'star',
  record: 'ellipse',
  k8s: 'pentagon',
  app: 'round-tag',
  function_ns: 'rhomboid',
  registry: 'round-rectangle',
};

function buildLayoutOptions(name) {
  const base = { name, animate: false, padding: 50, fit: true };
  if (name === 'cose') {
    return {
      ...base,
      nodeRepulsion: () => 1500000,
      idealEdgeLength: () => 130,
      edgeElasticity: () => 80,
      nodeOverlap: 32,
      componentSpacing: 140,
      gravity: 0.3,
      gravityRange: 3.8,
      numIter: 2500,
      initialTemp: 220,
      coolingFactor: 0.96,
      minTemp: 1.0,
      nestingFactor: 5,
      randomize: true,
    };
  }
  if (name === 'concentric') {
    return { ...base, minNodeSpacing: 40, spacingFactor: 1.4 };
  }
  if (name === 'breadthfirst') {
    return { ...base, spacingFactor: 1.3, directed: true };
  }
  if (name === 'grid') {
    return { ...base, avoidOverlap: true, spacingFactor: 1.3 };
  }
  return base;
}

function buildCytoscapeStyle() {
  const t = themeColors();
  const selectedBorder = currentTheme() === 'light' ? '#1f2328' : '#fff';
  return [
    {
      selector: 'node',
      style: {
        'background-color': (e) => TYPE_COLOR[e.data('type')] || '#8b949e',
        'shape': (e) => TYPE_SHAPE[e.data('type')] || 'ellipse',
        'label': 'data(label)',
        'color': t.textPrimary,
        'font-size': 10,
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 4,
        'text-outline-color': t.textOutline,
        'text-outline-width': 2,
        'text-wrap': 'ellipsis',
        'text-max-width': 110,
        'width': 26,
        'height': 26,
        'border-color': t.nodeBorder,
        'border-width': 1.5,
      },
    },
    { selector: 'node[type = "vpc"]', style: { width: 36, height: 36 } },
    { selector: 'node[type = "domain"]', style: { width: 32, height: 32 } },
    { selector: 'node:selected', style: { 'border-color': selectedBorder, 'border-width': 3 } },
    { selector: 'node.dim', style: { opacity: 0.15 } },
    {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'width': 1.2,
        'line-color': t.edge,
        'target-arrow-color': t.edge,
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.8,
        'opacity': 0.7,
      },
    },
    {
      selector: 'edge[kind = "resolves_to"]',
      style: { 'line-color': t.edgeDns, 'line-style': 'dashed', 'target-arrow-color': t.edgeDns },
    },
    {
      selector: 'edge[kind = "alias_of"]',
      style: { 'line-color': t.edgeDns, 'line-style': 'dotted', 'target-arrow-color': t.edgeDns },
    },
    {
      selector: 'edge[kind = "protects"]',
      style: { 'line-color': t.edgeFirewall, 'target-arrow-color': t.edgeFirewall },
    },
    {
      selector: 'edge[kind = "routes_to"]',
      style: { 'line-color': t.edgeLb, 'target-arrow-color': t.edgeLb },
    },
    {
      selector: 'edge[kind = "attached_to"]',
      style: { 'line-color': t.edgeVolume, 'target-arrow-color': t.edgeVolume },
    },
    { selector: 'edge.dim', style: { opacity: 0.05 } },
    { selector: '.hidden-type', style: { display: 'none' } },
    { selector: '.hidden-isolation', style: { display: 'none' } },
    {
      selector: 'node.marked-deletion',
      style: {
        'outline-color': '#ff5454',
        'outline-style': 'solid',
        'outline-width': 4,
        'outline-offset': 3,
        'outline-opacity': 1,
      },
    },
    {
      selector: 'node.marked-deletion:selected',
      style: { 'outline-color': '#ff7b72', 'outline-width': 6 },
    },
  ];
}

const cy = cytoscape({
  container: document.getElementById('cy'),
  wheelSensitivity: 0.2,
  style: buildCytoscapeStyle(),
  layout: buildLayoutOptions('cose'),
});

const els = {
  refresh: document.getElementById('refresh'),
  search: document.getElementById('search'),
  layoutSelect: document.getElementById('layout-select'),
  statusPill: document.getElementById('status-pill'),
  lastFetched: document.getElementById('last-fetched'),
  detailsContent: document.getElementById('details-content'),
  detailsEmpty: document.getElementById('details-empty'),
  overlay: document.getElementById('overlay'),
  overlayText: document.getElementById('overlay-text'),
  flaggedChip: document.getElementById('flagged-chip'),
  flaggedCount: document.getElementById('flagged-count'),
  isolationBanner: document.getElementById('isolation-banner'),
  isolationName: document.getElementById('isolation-name'),
  isolationMeta: document.getElementById('isolation-meta'),
  isolationClear: document.getElementById('isolation-clear'),
  themeToggle: document.getElementById('theme-toggle'),
  settingsOpen: document.getElementById('settings-open'),
  settingsModal: document.getElementById('settings-modal'),
  settingsClose: document.getElementById('settings-close'),
  tokenStatus: document.getElementById('token-status'),
  tokenInput: document.getElementById('token-input'),
  tokenShow: document.getElementById('token-show'),
  tokenSave: document.getElementById('token-save'),
  tokenClear: document.getElementById('token-clear'),
  tokenFeedback: document.getElementById('token-feedback'),
};

function updateThemeToggleLabel() {
  els.themeToggle.textContent = currentTheme() === 'light' ? 'Dark mode' : 'Light mode';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem('do-topology.theme', theme); } catch (e) {}
  updateThemeToggleLabel();
  // Cytoscape doesn't read CSS variables — re-build its stylesheet from the
  // freshly-resolved theme colors and tell it to use the new style.
  cy.style().fromJson(buildCytoscapeStyle()).update();
}

els.themeToggle.addEventListener('click', () => {
  applyTheme(currentTheme() === 'light' ? 'dark' : 'light');
});

updateThemeToggleLabel();

// ----- settings modal (DO API token) -----

let cachedSettings = null;

async function fetchSettings() {
  const res = await fetch('/api/settings');
  if (!res.ok) throw new Error(`GET /api/settings -> ${res.status}`);
  cachedSettings = await res.json();
  renderTokenStatus(cachedSettings);
  return cachedSettings;
}

function renderTokenStatus(s) {
  if (!s.token_configured) {
    els.tokenStatus.className = 'token-status missing';
    els.tokenStatus.textContent =
      'No token configured. Paste a DigitalOcean Personal Access Token below to get started.';
    els.tokenClear.hidden = true;
  } else {
    const sourceLabel =
      s.source === 'env' ? 'from .env (DO_TOKEN)' : 'saved in this app';
    els.tokenStatus.className = 'token-status configured';
    els.tokenStatus.textContent = `Token configured (${sourceLabel}) ending in ••••${s.token_hint}.`;
    els.tokenClear.hidden = s.source !== 'db';
  }
}

function openSettings() {
  els.settingsModal.hidden = false;
  els.tokenInput.value = '';
  els.tokenInput.type = 'password';
  els.tokenShow.textContent = 'show';
  els.tokenFeedback.textContent = '';
  els.tokenFeedback.className = 'save-status';
  fetchSettings().catch((e) => {
    els.tokenStatus.className = 'token-status missing';
    els.tokenStatus.textContent = `Could not check settings: ${e.message}`;
  });
  setTimeout(() => els.tokenInput.focus(), 50);
}

function closeSettings() {
  els.settingsModal.hidden = true;
}

async function saveToken() {
  const token = els.tokenInput.value.trim();
  if (!token) return;
  els.tokenSave.disabled = true;
  els.tokenFeedback.className = 'save-status saving';
  els.tokenFeedback.textContent = 'validating with DigitalOcean…';
  try {
    const res = await fetch('/api/settings/token', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    cachedSettings = await res.json();
    renderTokenStatus(cachedSettings);
    els.tokenInput.value = '';
    els.tokenFeedback.className = 'save-status saved';
    els.tokenFeedback.textContent = 'saved';
    // Trigger a refresh so the UI immediately reflects data from the new token.
    setTimeout(() => {
      closeSettings();
      els.refresh.click();
    }, 600);
  } catch (e) {
    els.tokenFeedback.className = 'save-status error';
    els.tokenFeedback.textContent = e.message;
  } finally {
    els.tokenSave.disabled = false;
  }
}

async function clearToken() {
  if (!confirm('Remove the saved token from this app? You can paste a new one any time.')) return;
  els.tokenClear.disabled = true;
  try {
    const res = await fetch('/api/settings/token', { method: 'DELETE' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    cachedSettings = await res.json();
    renderTokenStatus(cachedSettings);
    els.tokenFeedback.className = 'save-status';
    els.tokenFeedback.textContent = 'cleared';
  } catch (e) {
    els.tokenFeedback.className = 'save-status error';
    els.tokenFeedback.textContent = e.message;
  } finally {
    els.tokenClear.disabled = false;
  }
}

els.settingsOpen.addEventListener('click', openSettings);
els.settingsClose.addEventListener('click', closeSettings);
els.settingsModal.addEventListener('click', (e) => {
  if (e.target.dataset.closeModal !== undefined) closeSettings();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !els.settingsModal.hidden) closeSettings();
});
els.tokenSave.addEventListener('click', saveToken);
els.tokenClear.addEventListener('click', clearToken);
els.tokenInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') saveToken();
});
els.tokenShow.addEventListener('click', () => {
  const showing = els.tokenInput.type === 'text';
  els.tokenInput.type = showing ? 'password' : 'text';
  els.tokenShow.textContent = showing ? 'show' : 'hide';
});

function setStatus(state, text) {
  els.statusPill.className = `pill ${state}`;
  els.statusPill.textContent = text;
}

function setLastFetched(iso) {
  if (!iso) {
    els.lastFetched.textContent = 'never fetched';
    return;
  }
  const d = new Date(iso);
  els.lastFetched.textContent = `last fetched ${d.toLocaleString()}`;
}

function showOverlay(text) {
  els.overlayText.textContent = text || 'Fetching…';
  els.overlay.hidden = false;
}
function hideOverlay() { els.overlay.hidden = true; }

function renderGraph(graph) {
  cy.elements().remove();
  cy.add(graph.nodes);
  cy.add(graph.edges);
  applyTypeFilter();
  applyAnnotations();
  applyIsolation();
  runLayout();
  updateLegendCounts();
}

function runLayout() {
  // Always recompute the cytoscape viewport before laying out — the container
  // may have resized since cy was constructed, especially right after page
  // load when CSS/fonts are still settling.
  cy.resize();
  const visible = cy.elements()
    .not('.hidden-type')
    .not('.hidden-isolation');
  if (visible.length === 0) return;
  const layout = visible.layout(buildLayoutOptions(els.layoutSelect.value));
  layout.one('layoutstop', () => {
    // Built-in fit:true on a subset layout can mis-fit because cytoscape
    // computes the bounding box including hidden elements. Explicitly fit
    // the camera to ONLY the visible elements once positions are final.
    cy.resize();
    cy.fit(visible, 50);
  });
  layout.run();
}

function applySearch() {
  const q = els.search.value.trim().toLowerCase();
  if (!q) {
    cy.elements().removeClass('dim');
    return;
  }
  cy.nodes().forEach((n) => {
    const d = n.data();
    const hay = [
      d.label, d.type, d.public_ip, d.private_ip, d.ip,
      d.fqdn, d.domain, d.host, d.engine, d.region, d.size, d.role,
      ...(d.tags || []),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    if (hay.includes(q)) {
      n.removeClass('dim');
    } else {
      n.addClass('dim');
    }
  });
  cy.edges().forEach((e) => {
    const src = e.source();
    const tgt = e.target();
    if (src.hasClass('dim') && tgt.hasClass('dim')) {
      e.addClass('dim');
    } else {
      e.removeClass('dim');
    }
  });
}

// ----- details panel -----

const TYPE_LABEL = {
  droplet: 'droplet',
  db: 'database',
  vpc: 'vpc',
  firewall: 'firewall',
  lb: 'load balancer',
  reserved_ip: 'reserved ip',
  volume: 'volume',
  snapshot: 'snapshot',
  domain: 'domain',
  record: 'dns record',
  k8s: 'k8s cluster',
  app: 'app',
  function_ns: 'functions ns',
  registry: 'registry',
};

function summaryFields(d) {
  switch (d.type) {
    case 'droplet':
      return [
        ['size', d.size],
        ['region', d.region],
        ['status', d.status],
        ['public IP', d.public_ip],
        ['private IP', d.private_ip],
        ['memory', d.memory ? `${d.memory} MB` : null],
        ['vcpus', d.vcpus],
        ['disk', d.disk ? `${d.disk} GB` : null],
        ['tags', d.tags],
      ];
    case 'db':
      return [
        ['role', d.role === 'replica' ? 'read-only replica' : 'primary'],
        ['engine', `${d.engine || ''} ${d.version || ''}`.trim()],
        ['size', d.size],
        ['nodes', d.num_nodes],
        ['region', d.region],
        ['status', d.status],
        ['disk', d.disk_size_gb ? `${d.disk_size_gb} GB` : null],
        ['host', d.host],
        ['tags', d.tags],
      ];
    case 'vpc':
      return [
        ['region', d.region],
        ['ip range', d.ip_range],
      ];
    case 'firewall':
      return [['tags', d.tags]];
    case 'lb':
      return [
        ['ip', d.ip],
        ['region', d.region],
        ['tags', d.tags],
      ];
    case 'reserved_ip':
      return [
        ['ip', d.ip],
        ['region', d.region],
      ];
    case 'volume':
      return [
        ['size', d.size_gigabytes ? `${d.size_gigabytes} GB` : null],
        ['region', d.region],
        ['tags', d.tags],
      ];
    case 'snapshot':
      return [
        ['size', d.size_gigabytes ? `${d.size_gigabytes} GB` : null],
        ['source type', d.resource_type],
        ['source id', d.resource_id],
        ['tags', d.tags],
      ];
    case 'domain':
      return [];
    case 'record':
      return [
        ['type', d.rtype],
        ['fqdn', d.fqdn],
        ['data', d.data_value],
        ['ttl', d.ttl],
      ];
    case 'k8s':
      return [
        ['region', d.region],
        ['node pools', d.node_pool_count],
        ['tags', d.tags],
      ];
    case 'app':
      return [
        ['region', d.region],
        ['ingress', d.default_ingress],
        ['live url', d.live_url],
      ];
    case 'function_ns':
      return [
        ['region', d.region],
      ];
    case 'registry':
      return [
        ['tier', d.subscription_tier_slug],
      ];
    default:
      return [];
  }
}

// Returns { label, sortIndex } from `selfNode`'s perspective
function relationLabel(selfNode, edge, otherNode) {
  const isOutgoing = edge.source().id() === selfNode.id();
  const kind = edge.data('kind');
  const otherType = otherNode.data('type');
  const map = {
    member_of: { out: 'VPC', in: `Members (${TYPE_LABEL[otherType] || otherType})` },
    protects: { out: 'Protected droplets', in: 'Firewalls protecting' },
    routes_to: { out: 'Backend droplets', in: 'Load balancers routing to' },
    assigned_to: { out: 'Assigned to droplet', in: 'Reserved IPs' },
    attached_to: { out: 'Attached to droplet', in: 'Volumes attached' },
    snapshot_of: { out: 'Source resource', in: 'Snapshots' },
    resolves_to: { out: 'Resolves to', in: 'DNS records pointing here' },
    has_record: { out: 'DNS records', in: 'Parent domain' },
    alias_of: { out: 'CNAME alias of', in: 'CNAMEs aliasing this' },
    exposed_via: { out: 'Exposed via DNS', in: 'Apps exposed by this record' },
    replica_of: { out: 'Replica of', in: 'Read-only replicas' },
  };
  const labels = map[kind];
  if (!labels) return isOutgoing ? kind : `${kind} (in)`;
  return isOutgoing ? labels.out : labels.in;
}

function nodeLabelForRelation(otherNode) {
  const d = otherNode.data();
  const meta = secondaryLabel(d);
  return { label: d.label, meta };
}

function secondaryLabel(d) {
  switch (d.type) {
    case 'droplet': return d.public_ip || d.private_ip || d.region || '';
    case 'db': return `${d.engine || ''} ${d.size || ''}`.trim();
    case 'vpc': return d.ip_range || d.region || '';
    case 'lb': return d.ip || '';
    case 'reserved_ip': return d.ip || '';
    case 'volume': return d.size_gigabytes ? `${d.size_gigabytes} GB` : '';
    case 'snapshot': return d.size_gigabytes ? `${d.size_gigabytes} GB` : '';
    case 'record': return d.data_value ? `${d.rtype} → ${d.data_value}` : d.rtype;
    case 'app': return d.region || '';
    default: return '';
  }
}

function renderDetails(node) {
  const d = node.data();
  const color = TYPE_COLOR[d.type] || '#8b949e';

  const header = document.createElement('div');
  header.className = 'detail-header';
  const badge = document.createElement('span');
  badge.className = 'detail-type-badge';
  badge.style.background = color;
  badge.textContent = TYPE_LABEL[d.type] || d.type;
  const name = document.createElement('div');
  name.className = 'detail-name';
  name.textContent = d.label;
  header.appendChild(badge);
  header.appendChild(name);

  const isolateBtn = document.createElement('button');
  isolateBtn.type = 'button';
  isolateBtn.className = 'isolate-btn';
  const isThisIsolated = isolatedNodeId === node.id();
  if (isThisIsolated) {
    isolateBtn.textContent = 'Exit isolation';
    isolateBtn.classList.add('active');
    isolateBtn.title = 'Show all nodes again';
  } else {
    isolateBtn.textContent = isolatedNodeId ? 'Isolate this' : 'Isolate';
    isolateBtn.title = 'Show only this node and its direct connections';
  }
  isolateBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (isolatedNodeId === node.id()) clearIsolation();
    else setIsolation(node.id());
  });
  header.appendChild(isolateBtn);

  const summary = document.createElement('div');
  summary.className = 'detail-summary';
  const dl = document.createElement('dl');
  for (const [k, v] of summaryFields(d)) {
    if (v == null || v === '') continue;
    if (Array.isArray(v) && v.length === 0) continue;
    const dt = document.createElement('dt');
    dt.textContent = k;
    const dd = document.createElement('dd');
    if (k === 'tags' && Array.isArray(v)) {
      dd.className = 'tags-cell';
      v.forEach((t) => {
        const chip = document.createElement('span');
        chip.className = 'tag-chip';
        chip.textContent = t;
        dd.appendChild(chip);
      });
    } else {
      dd.textContent = String(v);
    }
    dl.appendChild(dt);
    dl.appendChild(dd);
  }
  if (dl.children.length === 0) {
    summary.style.display = 'none';
  } else {
    summary.appendChild(dl);
  }

  // Group connected nodes by relation label
  const groups = new Map(); // label -> [{node, ...}]
  node.connectedEdges().forEach((edge) => {
    const other = edge.source().id() === node.id() ? edge.target() : edge.source();
    if (other.id() === node.id()) return;
    const label = relationLabel(node, edge, other);
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label).push(other);
  });

  const relations = document.createElement('div');
  relations.className = 'detail-relations';

  if (groups.size === 0) {
    const empty = document.createElement('div');
    empty.className = 'relation-empty';
    empty.textContent = 'No connections.';
    relations.appendChild(empty);
  } else {
    const sortedGroups = [...groups.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    for (const [label, others] of sortedGroups) {
      const group = document.createElement('div');
      group.className = 'relation-group';
      const h = document.createElement('h3');
      const title = document.createElement('span');
      title.textContent = label;
      const count = document.createElement('span');
      count.className = 'count';
      count.textContent = others.length;
      h.appendChild(title);
      h.appendChild(count);
      group.appendChild(h);

      const ul = document.createElement('ul');
      ul.className = 'relation-list';
      others
        .slice()
        .sort((a, b) =>
          (a.data('label') || '').localeCompare(b.data('label') || '')
        )
        .forEach((other) => {
          const li = document.createElement('button');
          li.className = 'relation-item';
          li.type = 'button';
          const dot = document.createElement('span');
          dot.className = 'dot';
          dot.style.background = TYPE_COLOR[other.data('type')] || '#8b949e';
          const main = document.createElement('span');
          main.className = 'relation-label';
          main.textContent = other.data('label') || other.id();
          li.appendChild(dot);
          li.appendChild(main);
          const meta = secondaryLabel(other.data());
          if (meta) {
            const m = document.createElement('span');
            m.className = 'relation-meta';
            m.textContent = meta;
            li.appendChild(m);
          }
          li.addEventListener('click', () => focusNode(other));
          ul.appendChild(li);
        });
      group.appendChild(ul);
      relations.appendChild(group);
    }
  }

  const annotations = buildAnnotationsSection(node);

  els.detailsContent.replaceChildren(header, summary, relations, annotations);
  els.detailsEmpty.hidden = true;
  els.detailsContent.hidden = false;
}

// ----- annotations (notes + flag-for-deletion) -----

const annotationsByNodeId = new Map();
const saveTimers = new Map();

async function loadAnnotations() {
  try {
    const res = await fetch('/api/annotations');
    if (!res.ok) throw new Error(`GET /api/annotations -> ${res.status}`);
    const data = await res.json();
    annotationsByNodeId.clear();
    for (const [id, ann] of Object.entries(data.annotations || {})) {
      annotationsByNodeId.set(id, ann);
    }
  } catch (e) {
    console.error('loadAnnotations failed', e);
  }
}

function getAnnotation(nodeId) {
  return annotationsByNodeId.get(nodeId) || {
    node_id: nodeId,
    note: '',
    marked_for_deletion: false,
  };
}

async function saveAnnotation(nodeId, payload) {
  const url = `/api/annotations/${encodeURIComponent(nodeId)}`;
  const res = await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`PUT ${url} -> ${res.status}`);
  const saved = await res.json();
  annotationsByNodeId.set(nodeId, saved);
  return saved;
}

function applyAnnotations() {
  cy.batch(() => {
    cy.nodes().forEach((n) => {
      const ann = annotationsByNodeId.get(n.id());
      if (ann?.marked_for_deletion) n.addClass('marked-deletion');
      else n.removeClass('marked-deletion');
    });
  });
  updateFlaggedCount();
}

function updateFlaggedCount() {
  let count = 0;
  cy.nodes().forEach((n) => {
    if (n.hasClass('marked-deletion')) count++;
  });
  els.flaggedCount.textContent = count;
  els.flaggedChip.hidden = count === 0;
}

function scheduleSave(nodeId, getPayload, statusEl) {
  if (saveTimers.has(nodeId)) clearTimeout(saveTimers.get(nodeId));
  statusEl.textContent = 'editing…';
  statusEl.className = 'save-status';
  saveTimers.set(
    nodeId,
    setTimeout(() => doSave(nodeId, getPayload, statusEl), 700)
  );
}

async function doSave(nodeId, getPayload, statusEl) {
  saveTimers.delete(nodeId);
  statusEl.textContent = 'saving…';
  statusEl.className = 'save-status saving';
  try {
    await saveAnnotation(nodeId, getPayload());
    statusEl.textContent = `saved ${formatTime(new Date())}`;
    statusEl.className = 'save-status saved';
    applyAnnotations();
  } catch (e) {
    console.error(e);
    statusEl.textContent = 'save failed';
    statusEl.className = 'save-status error';
  }
}

function formatTime(d) {
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}

function buildAnnotationsSection(node) {
  const nodeId = node.id();
  const ann = getAnnotation(nodeId);

  const wrap = document.createElement('div');
  wrap.className = 'detail-annotations';

  const h = document.createElement('h3');
  h.textContent = 'Notes & flags';
  wrap.appendChild(h);

  const ta = document.createElement('textarea');
  ta.className = 'notes-textarea';
  ta.placeholder = 'Notes about this resource — saved locally as you type.';
  ta.value = ann.note || '';
  wrap.appendChild(ta);

  const flagRow = document.createElement('div');
  flagRow.className = 'flag-row';

  const label = document.createElement('label');
  label.className = 'flag-toggle';
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = !!ann.marked_for_deletion;
  const labelText = document.createElement('span');
  labelText.textContent = 'Flag for deletion';
  label.appendChild(cb);
  label.appendChild(labelText);

  const status = document.createElement('span');
  status.className = 'save-status';
  status.textContent = ann.updated_at ? `saved ${formatTime(new Date(ann.updated_at))}` : '';
  if (ann.updated_at) status.classList.add('saved');

  flagRow.appendChild(label);
  flagRow.appendChild(status);
  wrap.appendChild(flagRow);

  const getPayload = () => ({
    note: ta.value,
    marked_for_deletion: cb.checked,
  });

  ta.addEventListener('input', () => scheduleSave(nodeId, getPayload, status));
  ta.addEventListener('blur', () => {
    if (saveTimers.has(nodeId)) {
      clearTimeout(saveTimers.get(nodeId));
      doSave(nodeId, getPayload, status);
    }
  });
  cb.addEventListener('change', () => doSave(nodeId, getPayload, status));

  return wrap;
}

function focusNode(node) {
  if (node.hasClass('hidden-type')) return;
  cy.elements().unselect();
  node.select();
  cy.animate({
    center: { eles: node },
    zoom: Math.max(cy.zoom(), 1.2),
    duration: 350,
    easing: 'ease-in-out',
  });
  renderDetails(node);
}

cy.on('tap', 'node', (evt) => {
  renderDetails(evt.target);
});

cy.on('tap', (evt) => {
  if (evt.target === cy) {
    els.detailsEmpty.hidden = false;
    els.detailsContent.hidden = true;
    els.detailsContent.replaceChildren();
  }
});

els.search.addEventListener('input', applySearch);

els.layoutSelect.addEventListener('change', () => {
  runLayout();
});

// ----- type filter (legend) -----
const hiddenTypes = new Set();

function applyTypeFilter() {
  cy.batch(() => {
    cy.nodes().forEach((n) => {
      if (hiddenTypes.has(n.data('type'))) {
        n.addClass('hidden-type');
      } else {
        n.removeClass('hidden-type');
      }
    });
    cy.edges().forEach((e) => {
      const src = e.source();
      const tgt = e.target();
      if (
        hiddenTypes.has(src.data('type')) ||
        hiddenTypes.has(tgt.data('type'))
      ) {
        e.addClass('hidden-type');
      } else {
        e.removeClass('hidden-type');
      }
    });
  });
}

function updateLegendCounts() {
  const counts = {};
  cy.nodes().forEach((n) => {
    const t = n.data('type');
    counts[t] = (counts[t] || 0) + 1;
  });
  document.querySelectorAll('.legend-row').forEach((el) => {
    const t = el.dataset.type;
    const countEl = el.querySelector('.legend-count');
    countEl.textContent = counts[t] ? counts[t] : '0';
    if (!counts[t]) {
      el.style.opacity = '0.4';
    } else {
      el.style.opacity = '';
    }
    el.classList.toggle('off', hiddenTypes.has(t));
  });
}

document.querySelectorAll('.legend-row').forEach((el) => {
  el.addEventListener('click', () => {
    const t = el.dataset.type;
    if (hiddenTypes.has(t)) hiddenTypes.delete(t);
    else hiddenTypes.add(t);
    applyTypeFilter();
    updateLegendCounts();
    runLayout();
  });
});

document.getElementById('legend-reset').addEventListener('click', (e) => {
  e.stopPropagation();
  hiddenTypes.clear();
  applyTypeFilter();
  updateLegendCounts();
  runLayout();
});

// ----- isolation (focus on a single node + its direct neighbors) -----

let isolatedNodeId = null;

function applyIsolation() {
  cy.batch(() => {
    cy.elements().removeClass('hidden-isolation');
    if (!isolatedNodeId) return;
    const node = cy.getElementById(isolatedNodeId);
    if (node.length === 0) {
      // Isolated node disappeared (e.g., after a refresh removed it)
      isolatedNodeId = null;
      return;
    }
    const visible = node.closedNeighborhood();
    cy.elements().difference(visible).addClass('hidden-isolation');
  });
  updateIsolationBanner();
}

function setIsolation(nodeId) {
  isolatedNodeId = nodeId;
  applyIsolation();
  // Banner just appeared/disappeared → container height changed →
  // cytoscape needs to rebind its click coordinates before we re-layout.
  requestAnimationFrame(() => {
    cy.resize();
    runLayout();
    if (nodeId) {
      const node = cy.getElementById(nodeId);
      if (node.length === 1) {
        cy.elements().unselect();
        node.select();
        renderDetails(node);
      }
    } else {
      const sel = cy.$('node:selected');
      if (sel.length === 1) renderDetails(sel);
    }
  });
}

function clearIsolation() {
  setIsolation(null);
}

function updateIsolationBanner() {
  if (!isolatedNodeId) {
    els.isolationBanner.hidden = true;
    document.body.classList.remove('isolation-active');
    return;
  }
  const node = cy.getElementById(isolatedNodeId);
  if (node.length === 0) {
    els.isolationBanner.hidden = true;
    document.body.classList.remove('isolation-active');
    return;
  }
  els.isolationBanner.hidden = false;
  document.body.classList.add('isolation-active');
  els.isolationName.textContent = node.data('label') || isolatedNodeId;
  const neighbors = node.neighborhood('node').length;
  els.isolationMeta.textContent =
    `${TYPE_LABEL[node.data('type')] || node.data('type')} · ${neighbors} direct connection${neighbors === 1 ? '' : 's'}`;
}

els.isolationClear.addEventListener('click', clearIsolation);

async function loadLatest() {
  const res = await fetch('/api/snapshot/latest');
  if (!res.ok) throw new Error(`GET /api/snapshot/latest -> ${res.status}`);
  return res.json();
}

async function refresh() {
  const res = await fetch('/api/refresh', { method: 'POST' });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST /api/refresh -> ${res.status}: ${text}`);
  }
  return res.json();
}

async function init() {
  // Wait one paint so the container has its real dimensions before cytoscape
  // captures them.
  await new Promise(requestAnimationFrame);
  cy.resize();

  // First-run check: if no DO token is configured, show the settings modal
  // and skip the auto-refresh so the user gets a clear "configure first" UX.
  let settings;
  try {
    settings = await fetchSettings();
  } catch (e) {
    console.error(e);
    settings = { token_configured: false };
  }
  if (!settings.token_configured) {
    setStatus('pending', 'no token');
    hideOverlay();
    openSettings();
    return;
  }

  setStatus('fetching', 'loading…');
  showOverlay('Loading last snapshot…');
  await loadAnnotations();
  let latest;
  try {
    latest = await loadLatest();
  } catch (e) {
    console.error(e);
    setStatus('error', 'load failed');
    els.overlayText.textContent = 'Failed to load snapshot. Check console.';
    return;
  }

  if (latest.snapshot) {
    renderGraph(latest.graph);
    setLastFetched(latest.snapshot.fetched_at);
    setStatus(latest.snapshot.status, latest.snapshot.status);
    hideOverlay();
  } else {
    setStatus('fetching', 'first fetch…');
    showOverlay('No snapshot yet — fetching from DigitalOcean…');
  }

  // Auto-refresh in background to ensure data is fresh
  try {
    const fresh = await refresh();
    renderGraph(fresh.graph);
    setStatus(fresh.snapshot.status, fresh.snapshot.status);
    setLastFetched(new Date().toISOString());
    hideOverlay();
    if (fresh.snapshot.errors && Object.keys(fresh.snapshot.errors).length) {
      console.warn('Partial snapshot errors:', fresh.snapshot.errors);
    }
  } catch (e) {
    console.error(e);
    setStatus('error', 'refresh failed');
    els.overlayText.textContent = 'Refresh failed. Check console / token.';
    setTimeout(hideOverlay, 4000);
  }
}

els.refresh.addEventListener('click', async () => {
  els.refresh.disabled = true;
  setStatus('fetching', 'fetching…');
  showOverlay('Fetching from DigitalOcean…');
  try {
    const fresh = await refresh();
    renderGraph(fresh.graph);
    setStatus(fresh.snapshot.status, fresh.snapshot.status);
    setLastFetched(new Date().toISOString());
  } catch (e) {
    console.error(e);
    setStatus('error', 'refresh failed');
    alert('Refresh failed: ' + e.message);
  } finally {
    els.refresh.disabled = false;
    hideOverlay();
  }
});

els.flaggedChip.addEventListener('click', () => {
  const flagged = cy.nodes('.marked-deletion').not('.hidden-type');
  if (flagged.length === 0) return;
  // Cycle: focus the next flagged node after the currently selected one
  const selected = cy.$('node:selected');
  let idx = 0;
  if (selected.length === 1) {
    const i = flagged.toArray().findIndex((n) => n.id() === selected.id());
    idx = i >= 0 ? (i + 1) % flagged.length : 0;
  }
  focusNode(flagged[idx]);
});

init();
