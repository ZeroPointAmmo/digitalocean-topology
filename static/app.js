'use strict';

const ICONS = {
  app: '<rect x="3" y="4" width="18" height="14" rx="2"></rect><path d="M8 20h8"></path><path d="M12 18v2"></path>',
  cloud: '<path d="M17.5 19H8a5 5 0 1 1 1.2-9.85A6 6 0 0 1 20 12.5 3.5 3.5 0 0 1 17.5 19z"></path>',
  database: '<ellipse cx="12" cy="5" rx="8" ry="3"></ellipse><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"></path><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"></path>',
  flag: '<path d="M5 21V4"></path><path d="M5 4h11l-1 4 1 4H5"></path>',
  focus: '<path d="M4 8V5a1 1 0 0 1 1-1h3"></path><path d="M16 4h3a1 1 0 0 1 1 1v3"></path><path d="M20 16v3a1 1 0 0 1-1 1h-3"></path><path d="M8 20H5a1 1 0 0 1-1-1v-3"></path><circle cx="12" cy="12" r="3"></circle>',
  globe: '<circle cx="12" cy="12" r="9"></circle><path d="M3 12h18"></path><path d="M12 3a14 14 0 0 1 0 18"></path><path d="M12 3a14 14 0 0 0 0 18"></path>',
  hardDrive: '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="M7 15h.01"></path><path d="M11 15h6"></path>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7"></path><path d="M3 4v6h6"></path><path d="M12 7v5l3 2"></path>',
  key: '<circle cx="7.5" cy="15.5" r="4.5"></circle><path d="M11 12l9-9"></path><path d="M15 4l3 3"></path>',
  lambda: '<path d="M6 20 13 4"></path><path d="M10 4h3l5 16"></path>',
  layout: '<rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect>',
  lock: '<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V7a4 4 0 0 1 8 0v4"></path>',
  maximize: '<path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M16 3h3a2 2 0 0 1 2 2v3"></path><path d="M21 16v3a2 2 0 0 1-2 2h-3"></path><path d="M8 21H5a2 2 0 0 1-2-2v-3"></path>',
  minus: '<path d="M5 12h14"></path>',
  moon: '<path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.5 6.5 0 0 0 9.8 9.8z"></path>',
  mousePointer: '<path d="M4 3l7.5 18 2.2-7.3L21 11.5z"></path>',
  'mouse-pointer': '<path d="M4 3l7.5 18 2.2-7.3L21 11.5z"></path>',
  network: '<rect x="16" y="16" width="5" height="5" rx="1"></rect><rect x="3" y="3" width="5" height="5" rx="1"></rect><rect x="16" y="3" width="5" height="5" rx="1"></rect><path d="M8 5.5h8"></path><path d="M18.5 8v8"></path><path d="M8 5.5c5 0 5 13 8 13"></path>',
  package: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"></path><path d="m4 7.5 8 4.5 8-4.5"></path><path d="M12 12v9"></path>',
  palette: '<circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 3a9 9 0 0 0 0 18h1.5a2 2 0 0 0 1.5-3.3 1.5 1.5 0 0 1 1.1-2.5H18a3 3 0 0 0 3-3A9 9 0 0 0 12 3z"></path>',
  plus: '<path d="M12 5v14"></path><path d="M5 12h14"></path>',
  refresh: '<path d="M21 12a9 9 0 0 1-15.5 6.2"></path><path d="M3 12A9 9 0 0 1 18.5 5.8"></path><path d="M18 2v4h-4"></path><path d="M6 22v-4h4"></path>',
  search: '<circle cx="11" cy="11" r="7"></circle><path d="m21 21-4.3-4.3"></path>',
  server: '<rect x="3" y="4" width="18" height="7" rx="2"></rect><rect x="3" y="13" width="18" height="7" rx="2"></rect><path d="M7 8h.01"></path><path d="M7 17h.01"></path>',
  settings: '<path d="M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5z"></path><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.7 1.7 0 0 0 4.6 15 1.7 1.7 0 0 0 3 14H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1A2 2 0 1 1 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3h.1A1.7 1.7 0 0 0 10 3V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6h.1a1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9v.1A1.7 1.7 0 0 0 21 10h.1a2 2 0 1 1 0 4H21a1.7 1.7 0 0 0-1.6 1z"></path>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
  sun: '<circle cx="12" cy="12" r="4"></circle><path d="M12 2v2"></path><path d="M12 20v2"></path><path d="m4.9 4.9 1.4 1.4"></path><path d="m17.7 17.7 1.4 1.4"></path><path d="M2 12h2"></path><path d="M20 12h2"></path><path d="m4.9 19.1 1.4-1.4"></path><path d="m17.7 6.3 1.4-1.4"></path>',
  tag: '<path d="M20.6 13.1 13.1 20.6a2 2 0 0 1-2.8 0L3 13.3V3h10.3l7.3 7.3a2 2 0 0 1 0 2.8z"></path><path d="M7.5 7.5h.01"></path>',
  x: '<path d="M18 6 6 18"></path><path d="m6 6 12 12"></path>',
};

const RESOURCE_META = {
  droplet: { label: 'droplet', color: '#4ea1ff', shape: 'round-rectangle', icon: 'cloud' },
  db: { label: 'database', color: '#f778ba', shape: 'barrel', icon: 'database' },
  vpc: { label: 'vpc', color: '#a371f7', shape: 'octagon', icon: 'network' },
  firewall: { label: 'firewall', color: '#ee5d5d', shape: 'diamond', icon: 'shield' },
  lb: { label: 'load balancer', color: '#f59e57', shape: 'hexagon', icon: 'layout' },
  reserved_ip: { label: 'reserved ip', color: '#66c6ff', shape: 'tag', icon: 'tag' },
  volume: { label: 'volume', color: '#55c87f', shape: 'cylinder', icon: 'hardDrive' },
  snapshot: { label: 'snapshot', color: '#2e9d67', shape: 'cylinder', icon: 'history' },
  domain: { label: 'domain', color: '#d2a8ff', shape: 'star', icon: 'globe' },
  record: { label: 'dns record', color: '#b794f6', shape: 'ellipse', icon: 'server' },
  k8s: { label: 'k8s cluster', color: '#2f8f83', shape: 'pentagon', icon: 'package' },
  app: { label: 'app', color: '#f4b860', shape: 'round-tag', icon: 'app' },
  function_ns: { label: 'functions ns', color: '#e5c84f', shape: 'rhomboid', icon: 'lambda' },
  registry: { label: 'registry', color: '#8d9a91', shape: 'round-rectangle', icon: 'package' },
};

const TYPE_COLOR = Object.fromEntries(
  Object.entries(RESOURCE_META).map(([type, meta]) => [type, meta.color])
);

const NODE_ICON_DATA = Object.fromEntries(
  Object.entries(RESOURCE_META).map(([type, meta]) => [type, svgDataUri(meta.icon)])
);

const cy = cytoscape({
  container: document.getElementById('cy'),
  wheelSensitivity: 0.2,
  minZoom: 0.18,
  maxZoom: 3.5,
  style: buildCytoscapeStyle(),
  layout: buildLayoutOptions('cose'),
});

const els = {
  refresh: document.getElementById('refresh'),
  search: document.getElementById('search'),
  layoutSelect: document.getElementById('layout-select'),
  statusPill: document.getElementById('status-pill'),
  lastFetched: document.getElementById('last-fetched'),
  snapshotMode: document.getElementById('snapshot-mode'),
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
  fitView: document.getElementById('fit-view'),
  resetLayout: document.getElementById('reset-layout'),
  zoomIn: document.getElementById('zoom-in'),
  zoomOut: document.getElementById('zoom-out'),
  clearIsolationToolbar: document.getElementById('clear-isolation-toolbar'),
  visibleCount: document.getElementById('visible-count'),
  historyOpen: document.getElementById('history-open'),
  historyDrawer: document.getElementById('history-drawer'),
  historyClose: document.getElementById('history-close'),
  historyList: document.getElementById('history-list'),
};

let cachedSettings = null;
let currentSnapshot = null;
let viewingHistorical = false;
let isolatedNodeId = null;

const annotationsByNodeId = new Map();
const saveTimers = new Map();
const hiddenTypes = new Set();

hydrateIcons();
updateThemeToggleLabel();
updateThemeChoices();

function iconEl(name, className = 'icon') {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', className);
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = ICONS[name] || ICONS.app;
  return svg;
}

function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    if (el.firstElementChild?.classList.contains('icon')) return;
    el.prepend(iconEl(el.dataset.icon));
  });
}

function svgDataUri(name) {
  const body = ICONS[name] || ICONS.app;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function readThemeVar(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

function currentTheme() {
  return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
}

function themeColors() {
  return {
    textOutline: readThemeVar('--cy-text-outline', '#090b0a'),
    nodeBorder: readThemeVar('--cy-node-border', 'rgba(255,255,255,.28)'),
    edge: readThemeVar('--cy-edge', '#39413a'),
    edgeFirewall: readThemeVar('--cy-edge-firewall', '#ee5d5d'),
    edgeLb: readThemeVar('--cy-edge-lb', '#f59e57'),
    edgeVolume: readThemeVar('--cy-edge-volume', '#55c87f'),
    edgeDns: readThemeVar('--cy-edge-dns', '#b794f6'),
    textPrimary: readThemeVar('--text-primary', '#eef2ed'),
  };
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem('do-topology.theme', theme); } catch (e) {}
  updateThemeToggleLabel();
  updateThemeChoices();
  cy.style().fromJson(buildCytoscapeStyle()).update();
}

function updateThemeToggleLabel() {
  const theme = currentTheme();
  const icon = els.themeToggle.querySelector('[data-icon]');
  if (icon) {
    icon.dataset.icon = theme === 'light' ? 'moon' : 'sun';
    icon.replaceChildren(iconEl(icon.dataset.icon));
  }
  const label = els.themeToggle.querySelector('span:last-child');
  if (label) label.textContent = theme === 'light' ? 'Dark' : 'Light';
}

function updateThemeChoices() {
  document.querySelectorAll('[data-theme-choice]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.themeChoice === currentTheme());
  });
}

function buildLayoutOptions(name) {
  const base = { name, animate: false, padding: 58, fit: true };
  if (name === 'cose') {
    return {
      ...base,
      nodeRepulsion: () => 1500000,
      idealEdgeLength: () => 135,
      edgeElasticity: () => 80,
      nodeOverlap: 34,
      componentSpacing: 150,
      gravity: 0.28,
      gravityRange: 3.8,
      numIter: 2500,
      initialTemp: 220,
      coolingFactor: 0.96,
      minTemp: 1.0,
      nestingFactor: 5,
      randomize: true,
    };
  }
  if (name === 'concentric') return { ...base, minNodeSpacing: 48, spacingFactor: 1.45 };
  if (name === 'breadthfirst') return { ...base, spacingFactor: 1.35, directed: true };
  if (name === 'grid') return { ...base, avoidOverlap: true, spacingFactor: 1.35 };
  return base;
}

function buildCytoscapeStyle() {
  const t = themeColors();
  const selectedBorder = currentTheme() === 'light' ? '#1f2622' : '#fff';
  return [
    {
      selector: 'node',
      style: {
        'background-color': (e) => TYPE_COLOR[e.data('type')] || '#8d9a91',
        'shape': (e) => RESOURCE_META[e.data('type')]?.shape || 'ellipse',
        'background-image': (e) => NODE_ICON_DATA[e.data('type')] || '',
        'background-fit': 'contain',
        'background-width-relative-to': 'inner',
        'background-height-relative-to': 'inner',
        'background-image-opacity': 0.92,
        'label': 'data(label)',
        'color': t.textPrimary,
        'font-size': 10,
        'font-weight': 600,
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 7,
        'text-outline-color': t.textOutline,
        'text-outline-width': 2.5,
        'text-wrap': 'ellipsis',
        'text-max-width': 116,
        'width': 31,
        'height': 31,
        'border-color': t.nodeBorder,
        'border-width': 1.4,
        'overlay-opacity': 0,
      },
    },
    { selector: 'node[type = "vpc"], node[type = "domain"]', style: { width: 40, height: 40 } },
    { selector: 'node:selected', style: { 'border-color': selectedBorder, 'border-width': 4, 'shadow-blur': 18, 'shadow-color': selectedBorder, 'shadow-opacity': 0.35 } },
    { selector: 'node.hover', style: { width: 36, height: 36, 'border-width': 3 } },
    { selector: 'node.dim', style: { opacity: 0.13 } },
    {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'width': 1.35,
        'line-color': t.edge,
        'target-arrow-color': t.edge,
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.82,
        'opacity': 0.74,
      },
    },
    { selector: 'edge[kind = "resolves_to"]', style: { 'line-color': t.edgeDns, 'line-style': 'dashed', 'target-arrow-color': t.edgeDns } },
    { selector: 'edge[kind = "alias_of"]', style: { 'line-color': t.edgeDns, 'line-style': 'dotted', 'target-arrow-color': t.edgeDns } },
    { selector: 'edge[kind = "protects"]', style: { 'line-color': t.edgeFirewall, 'target-arrow-color': t.edgeFirewall, 'width': 1.7 } },
    { selector: 'edge[kind = "routes_to"]', style: { 'line-color': t.edgeLb, 'target-arrow-color': t.edgeLb, 'width': 1.7 } },
    { selector: 'edge[kind = "attached_to"]', style: { 'line-color': t.edgeVolume, 'target-arrow-color': t.edgeVolume } },
    { selector: 'edge.dim', style: { opacity: 0.05 } },
    { selector: '.hidden-type', style: { display: 'none' } },
    { selector: '.hidden-isolation', style: { display: 'none' } },
    {
      selector: 'node.marked-deletion',
      style: {
        'outline-color': '#ff6b65',
        'outline-style': 'solid',
        'outline-width': 4,
        'outline-offset': 4,
        'outline-opacity': 1,
      },
    },
    { selector: 'node.marked-deletion:selected', style: { 'outline-color': '#ffaaa3', 'outline-width': 6 } },
  ];
}

function setStatus(state, text) {
  els.statusPill.className = `pill ${state || 'pending'}`;
  els.statusPill.textContent = text || state || 'idle';
}

function setLastFetched(iso) {
  if (!iso) {
    els.lastFetched.textContent = 'never fetched';
    return;
  }
  const d = new Date(iso);
  els.lastFetched.textContent = `fetched ${d.toLocaleString()}`;
}

function setCurrentSnapshot(snapshot, historical) {
  currentSnapshot = snapshot || null;
  viewingHistorical = !!historical;
  els.snapshotMode.hidden = !viewingHistorical;
  if (snapshot?.fetched_at) setLastFetched(snapshot.fetched_at);
}

function showOverlay(text) {
  els.overlayText.textContent = text || 'Fetching...';
  els.overlay.hidden = false;
}

function hideOverlay() {
  els.overlay.hidden = true;
}

function enrichGraph(graph) {
  return {
    nodes: (graph.nodes || []).map((node) => {
      const data = { ...node.data };
      const meta = RESOURCE_META[data.type] || {};
      data.type_label = meta.label || data.type;
      return { ...node, data };
    }),
    edges: graph.edges || [],
  };
}

function renderGraph(graph) {
  const enriched = enrichGraph(graph);
  cy.elements().remove();
  cy.add(enriched.nodes);
  cy.add(enriched.edges);
  applyTypeFilter();
  applyAnnotations();
  applyIsolation();
  applySearch();
  runLayout();
  updateLegendCounts();
  updateVisibleCount();
}

function visibleElements() {
  return cy.elements().not('.hidden-type').not('.hidden-isolation');
}

function visibleNodes() {
  return cy.nodes().not('.hidden-type').not('.hidden-isolation');
}

function updateVisibleCount() {
  const visible = visibleNodes().length;
  const total = cy.nodes().length;
  els.visibleCount.textContent = `${visible}/${total} visible`;
}

function fitVisible() {
  const visible = visibleElements();
  if (visible.length) {
    cy.resize();
    cy.fit(visible, 58);
  }
}

function runLayout() {
  cy.resize();
  const visible = visibleElements();
  if (visible.length === 0) {
    updateVisibleCount();
    return;
  }
  const layout = visible.layout(buildLayoutOptions(els.layoutSelect.value));
  layout.one('layoutstop', () => {
    fitVisible();
    updateVisibleCount();
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
      d.label, d.type_label, d.type, d.public_ip, d.private_ip, d.ip,
      d.fqdn, d.domain, d.host, d.engine, d.region, d.size, d.role,
      ...(d.tags || []),
    ].filter(Boolean).join(' ').toLowerCase();
    n.toggleClass('dim', !hay.includes(q));
  });
  cy.edges().forEach((e) => {
    const src = e.source();
    const tgt = e.target();
    e.toggleClass('dim', src.hasClass('dim') && tgt.hasClass('dim'));
  });
}

function summaryFields(d) {
  switch (d.type) {
    case 'droplet':
      return [['size', d.size], ['region', d.region], ['status', d.status], ['public IP', d.public_ip], ['private IP', d.private_ip], ['memory', d.memory ? `${d.memory} MB` : null], ['vcpus', d.vcpus], ['disk', d.disk ? `${d.disk} GB` : null]];
    case 'db':
      return [['role', d.role === 'replica' ? 'read-only replica' : 'primary'], ['engine', `${d.engine || ''} ${d.version || ''}`.trim()], ['size', d.size], ['nodes', d.num_nodes], ['region', d.region], ['status', d.status], ['disk', d.disk_size_gb ? `${d.disk_size_gb} GB` : null], ['host', d.host]];
    case 'vpc':
      return [['region', d.region], ['ip range', d.ip_range]];
    case 'firewall':
      return [['tags', d.tags]];
    case 'lb':
      return [['ip', d.ip], ['region', d.region], ['tags', d.tags]];
    case 'reserved_ip':
      return [['ip', d.ip], ['region', d.region]];
    case 'volume':
      return [['size', d.size_gigabytes ? `${d.size_gigabytes} GB` : null], ['region', d.region], ['tags', d.tags]];
    case 'snapshot':
      return [['size', d.size_gigabytes ? `${d.size_gigabytes} GB` : null], ['source type', d.resource_type], ['source id', d.resource_id], ['tags', d.tags]];
    case 'record':
      return [['type', d.rtype], ['fqdn', d.fqdn], ['data', d.data_value], ['ttl', d.ttl]];
    case 'k8s':
      return [['region', d.region], ['node pools', d.node_pool_count], ['tags', d.tags]];
    case 'app':
      return [['region', d.region], ['ingress', d.default_ingress], ['live url', d.live_url]];
    case 'function_ns':
      return [['region', d.region]];
    case 'registry':
      return [['tier', d.subscription_tier_slug]];
    default:
      return [];
  }
}

function relationLabel(selfNode, edge, otherNode) {
  const isOutgoing = edge.source().id() === selfNode.id();
  const kind = edge.data('kind');
  const otherType = otherNode.data('type_label') || otherNode.data('type');
  const map = {
    member_of: { out: 'VPC', in: `Members (${otherType})`, icon: 'network' },
    protects: { out: 'Protected droplets', in: 'Firewalls protecting', icon: 'shield' },
    routes_to: { out: 'Backend droplets', in: 'Load balancers routing to', icon: 'layout' },
    assigned_to: { out: 'Assigned to droplet', in: 'Reserved IPs', icon: 'tag' },
    attached_to: { out: 'Attached to droplet', in: 'Volumes attached', icon: 'hardDrive' },
    snapshot_of: { out: 'Source resource', in: 'Snapshots', icon: 'history' },
    resolves_to: { out: 'Resolves to', in: 'DNS records pointing here', icon: 'globe' },
    has_record: { out: 'DNS records', in: 'Parent domain', icon: 'server' },
    alias_of: { out: 'CNAME alias of', in: 'CNAMEs aliasing this', icon: 'server' },
    exposed_via: { out: 'Exposed via DNS', in: 'Apps exposed by this record', icon: 'app' },
    replica_of: { out: 'Replica of', in: 'Read-only replicas', icon: 'database' },
  };
  const labels = map[kind];
  if (!labels) return { label: isOutgoing ? kind : `${kind} (in)`, icon: 'network' };
  return { label: isOutgoing ? labels.out : labels.in, icon: labels.icon };
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
    case 'record': return d.data_value ? `${d.rtype} -> ${d.data_value}` : d.rtype;
    case 'app': return d.region || '';
    default: return '';
  }
}

function renderDetails(node) {
  const d = node.data();
  const meta = RESOURCE_META[d.type] || RESOURCE_META.app;

  const card = document.createElement('article');
  card.className = 'resource-card';

  const hero = document.createElement('section');
  hero.className = 'resource-hero';

  const heading = document.createElement('div');
  heading.className = 'resource-heading';

  const resourceIcon = document.createElement('span');
  resourceIcon.className = 'resource-icon';
  resourceIcon.style.background = meta.color;
  resourceIcon.appendChild(iconEl(meta.icon));

  const title = document.createElement('div');
  title.className = 'resource-title';

  const kicker = document.createElement('div');
  kicker.className = 'resource-kicker';
  const typeBadge = document.createElement('span');
  typeBadge.className = 'type-badge';
  typeBadge.style.background = meta.color;
  typeBadge.textContent = meta.label;
  kicker.appendChild(typeBadge);
  if (d.status) {
    const status = document.createElement('span');
    status.className = 'status-badge';
    status.textContent = d.status;
    kicker.appendChild(status);
  }

  const name = document.createElement('h2');
  name.textContent = d.label || node.id();
  title.appendChild(kicker);
  title.appendChild(name);

  const isolateBtn = document.createElement('button');
  isolateBtn.type = 'button';
  isolateBtn.className = 'isolate-btn';
  isolateBtn.appendChild(iconEl('focus'));
  isolateBtn.append(document.createTextNode(isolatedNodeId === node.id() ? 'Exit' : 'Isolate'));
  isolateBtn.classList.toggle('active', isolatedNodeId === node.id());
  isolateBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (isolatedNodeId === node.id()) clearIsolation();
    else setIsolation(node.id());
  });

  heading.append(resourceIcon, title, isolateBtn);
  hero.appendChild(heading);

  const chips = buildMetaChips(d);
  if (chips.children.length) hero.appendChild(chips);
  card.appendChild(hero);

  const summary = buildSummarySection(d);
  if (summary) card.appendChild(summary);
  card.appendChild(buildRelationsSection(node));
  card.appendChild(buildAnnotationsSection(node));
  card.appendChild(buildRawSection(d.raw || d));

  els.detailsContent.replaceChildren(card);
  els.detailsEmpty.hidden = true;
  els.detailsContent.hidden = false;
}

function buildMetaChips(d) {
  const row = document.createElement('div');
  row.className = 'meta-row';
  const values = [
    ['region', d.region],
    ['role', d.role],
    ['ip', d.public_ip || d.ip],
    ['host', d.host],
  ];
  for (const [label, value] of values) {
    if (!value) continue;
    const chip = document.createElement('span');
    chip.className = 'meta-chip';
    chip.textContent = `${label}: ${value}`;
    row.appendChild(chip);
  }
  for (const tag of d.tags || []) {
    const chip = document.createElement('span');
    chip.className = 'tag-chip';
    chip.textContent = tag;
    row.appendChild(chip);
  }
  return row;
}

function buildSummarySection(d) {
  const fields = summaryFields(d).filter(([, v]) => v != null && v !== '' && (!Array.isArray(v) || v.length));
  if (!fields.length) return null;
  const section = document.createElement('section');
  section.className = 'detail-section';
  section.appendChild(sectionTitle('Summary', 'server'));
  const dl = document.createElement('dl');
  dl.className = 'summary-grid';
  for (const [k, v] of fields) {
    const item = document.createElement('div');
    item.className = 'summary-item';
    const dt = document.createElement('dt');
    dt.textContent = k;
    const dd = document.createElement('dd');
    dd.textContent = Array.isArray(v) ? v.join(', ') : String(v);
    item.append(dt, dd);
    dl.appendChild(item);
  }
  section.appendChild(dl);
  return section;
}

function buildRelationsSection(node) {
  const section = document.createElement('section');
  section.className = 'detail-section';
  section.appendChild(sectionTitle('Relationships', 'network'));

  const groups = new Map();
  node.connectedEdges().forEach((edge) => {
    const other = edge.source().id() === node.id() ? edge.target() : edge.source();
    if (other.id() === node.id()) return;
    const rel = relationLabel(node, edge, other);
    if (!groups.has(rel.label)) groups.set(rel.label, { icon: rel.icon, nodes: [] });
    groups.get(rel.label).nodes.push(other);
  });

  const wrap = document.createElement('div');
  wrap.className = 'detail-relations';

  if (groups.size === 0) {
    const empty = document.createElement('div');
    empty.className = 'relation-empty';
    empty.textContent = 'No connections.';
    wrap.appendChild(empty);
  } else {
    [...groups.entries()].sort((a, b) => a[0].localeCompare(b[0])).forEach(([label, group]) => {
      const box = document.createElement('div');
      box.className = 'relation-group';

      const h = document.createElement('h3');
      const title = document.createElement('span');
      title.className = 'relation-title';
      title.append(iconEl(group.icon), document.createTextNode(label));
      const count = document.createElement('span');
      count.className = 'count';
      count.textContent = group.nodes.length;
      h.append(title, count);
      box.appendChild(h);

      const ul = document.createElement('ul');
      ul.className = 'relation-list';
      group.nodes
        .slice()
        .sort((a, b) => (a.data('label') || '').localeCompare(b.data('label') || ''))
        .forEach((other) => {
          const li = document.createElement('button');
          li.className = 'relation-item';
          li.type = 'button';
          const dot = document.createElement('span');
          dot.className = 'dot';
          dot.style.background = TYPE_COLOR[other.data('type')] || '#8d9a91';
          const main = document.createElement('span');
          main.className = 'relation-label';
          main.textContent = other.data('label') || other.id();
          const meta = document.createElement('span');
          meta.className = 'relation-meta';
          meta.textContent = secondaryLabel(other.data());
          li.append(dot, main, meta);
          li.addEventListener('click', () => focusNode(other));
          ul.appendChild(li);
        });
      box.appendChild(ul);
      wrap.appendChild(box);
    });
  }

  section.appendChild(wrap);
  return section;
}

function sectionTitle(text, icon) {
  const title = document.createElement('div');
  title.className = 'section-title';
  const left = document.createElement('span');
  left.append(iconEl(icon), document.createTextNode(text));
  title.appendChild(left);
  return title;
}

function buildAnnotationsSection(node) {
  const nodeId = node.id();
  const ann = getAnnotation(nodeId);
  const wrap = document.createElement('section');
  wrap.className = 'cleanup-panel';
  wrap.appendChild(sectionTitle('Cleanup', 'flag'));

  const ta = document.createElement('textarea');
  ta.className = 'notes-textarea';
  ta.placeholder = 'Local notes';
  ta.value = ann.note || '';
  wrap.appendChild(ta);

  const flagRow = document.createElement('div');
  flagRow.className = 'flag-row';
  const label = document.createElement('label');
  label.className = 'flag-toggle';
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = !!ann.marked_for_deletion;
  label.append(cb, document.createTextNode('Flag for deletion'));

  const status = document.createElement('span');
  status.className = 'save-status';
  status.textContent = ann.updated_at ? `saved ${formatTime(new Date(ann.updated_at))}` : '';
  if (ann.updated_at) status.classList.add('saved');

  flagRow.append(label, status);
  wrap.appendChild(flagRow);

  const getPayload = () => ({ note: ta.value, marked_for_deletion: cb.checked });
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

function buildRawSection(raw) {
  const details = document.createElement('details');
  details.className = 'raw-panel';
  const summary = document.createElement('summary');
  summary.append(iconEl('package'), document.createTextNode(' Raw data'));
  const pre = document.createElement('pre');
  pre.textContent = JSON.stringify(raw || {}, null, 2);
  details.append(summary, pre);
  return details;
}

function getAnnotation(nodeId) {
  return annotationsByNodeId.get(nodeId) || {
    node_id: nodeId,
    note: '',
    marked_for_deletion: false,
  };
}

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
      n.toggleClass('marked-deletion', !!ann?.marked_for_deletion);
    });
  });
  updateFlaggedCount();
}

function updateFlaggedCount() {
  const count = cy.nodes('.marked-deletion').length;
  els.flaggedCount.textContent = count;
  els.flaggedChip.hidden = count === 0;
}

function scheduleSave(nodeId, getPayload, statusEl) {
  if (saveTimers.has(nodeId)) clearTimeout(saveTimers.get(nodeId));
  statusEl.textContent = 'editing...';
  statusEl.className = 'save-status';
  saveTimers.set(nodeId, setTimeout(() => doSave(nodeId, getPayload, statusEl), 700));
}

async function doSave(nodeId, getPayload, statusEl) {
  saveTimers.delete(nodeId);
  statusEl.textContent = 'saving...';
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

function focusNode(node) {
  if (node.hasClass('hidden-type')) return;
  cy.elements().unselect();
  node.select();
  cy.animate({
    center: { eles: node },
    zoom: Math.max(cy.zoom(), 1.2),
    duration: 300,
    easing: 'ease-in-out',
  });
  renderDetails(node);
}

function applyTypeFilter() {
  cy.batch(() => {
    cy.nodes().forEach((n) => n.toggleClass('hidden-type', hiddenTypes.has(n.data('type'))));
    cy.edges().forEach((e) => {
      const hidden = hiddenTypes.has(e.source().data('type')) || hiddenTypes.has(e.target().data('type'));
      e.toggleClass('hidden-type', hidden);
    });
  });
  updateVisibleCount();
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
    countEl.textContent = counts[t] || '0';
    el.style.opacity = counts[t] ? '' : '0.4';
    el.classList.toggle('off', hiddenTypes.has(t));
  });
}

function applyIsolation() {
  cy.batch(() => {
    cy.elements().removeClass('hidden-isolation');
    if (!isolatedNodeId) return;
    const node = cy.getElementById(isolatedNodeId);
    if (node.length === 0) {
      isolatedNodeId = null;
      return;
    }
    const visible = node.closedNeighborhood();
    cy.elements().difference(visible).addClass('hidden-isolation');
  });
  updateIsolationBanner();
  updateVisibleCount();
}

function setIsolation(nodeId) {
  isolatedNodeId = nodeId;
  applyIsolation();
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
  const active = !!isolatedNodeId && cy.getElementById(isolatedNodeId).length !== 0;
  els.isolationBanner.hidden = !active;
  document.body.classList.toggle('isolation-active', active);
  els.clearIsolationToolbar.disabled = !active;
  if (!active) return;
  const node = cy.getElementById(isolatedNodeId);
  els.isolationName.textContent = node.data('label') || isolatedNodeId;
  const neighbors = node.neighborhood('node').length;
  els.isolationMeta.textContent = `${node.data('type_label') || node.data('type')} - ${neighbors} direct connection${neighbors === 1 ? '' : 's'}`;
}

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
    els.tokenStatus.textContent = 'No token configured.';
    els.tokenClear.hidden = true;
  } else {
    const sourceLabel = s.source === 'env' ? 'from .env (DO_TOKEN)' : 'saved in this app';
    els.tokenStatus.className = 'token-status configured';
    els.tokenStatus.textContent = `Token configured (${sourceLabel}) ending in ****${s.token_hint}.`;
    els.tokenClear.hidden = s.source !== 'db';
  }
}

function openSettings(tab = 'token') {
  els.settingsModal.hidden = false;
  activateSettingsTab(tab);
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

function activateSettingsTab(tab) {
  document.querySelectorAll('.settings-tab').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.settingsTab === tab);
  });
  document.querySelectorAll('.settings-panel').forEach((panel) => {
    panel.hidden = panel.dataset.settingsPanel !== tab;
  });
}

async function saveToken() {
  const token = els.tokenInput.value.trim();
  if (!token) return;
  els.tokenSave.disabled = true;
  els.tokenFeedback.className = 'save-status saving';
  els.tokenFeedback.textContent = 'validating...';
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
    setTimeout(() => {
      closeSettings();
      els.refresh.click();
    }, 500);
  } catch (e) {
    els.tokenFeedback.className = 'save-status error';
    els.tokenFeedback.textContent = e.message;
  } finally {
    els.tokenSave.disabled = false;
  }
}

async function clearToken() {
  if (!confirm('Remove the saved token from this app?')) return;
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

async function loadSnapshots() {
  setHistoryMessage('Loading...');
  const res = await fetch('/api/snapshots');
  if (!res.ok) throw new Error(`GET /api/snapshots -> ${res.status}`);
  const data = await res.json();
  renderHistory(data.snapshots || []);
}

function setHistoryMessage(message) {
  const box = document.createElement('div');
  box.className = 'history-empty';
  box.textContent = message;
  els.historyList.replaceChildren(box);
}

function renderHistory(snapshots) {
  els.historyList.replaceChildren();
  if (!snapshots.length) {
    const empty = document.createElement('div');
    empty.className = 'history-empty';
    empty.textContent = 'No snapshots yet.';
    els.historyList.appendChild(empty);
    return;
  }
  snapshots.forEach((snap) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'drawer-snapshot';
    btn.classList.toggle('active', currentSnapshot?.id === snap.id);

    const row = document.createElement('div');
    row.className = 'snapshot-row';
    const title = document.createElement('div');
    title.className = 'snapshot-title';
    title.append(iconEl(snap.status === 'success' ? 'shield' : snap.status === 'partial' ? 'history' : 'x'), document.createTextNode(`Snapshot #${snap.id}`));
    const pill = document.createElement('span');
    pill.className = `pill ${snap.status}`;
    pill.textContent = snap.status;
    row.append(title, pill);

    const meta = document.createElement('div');
    meta.className = 'snapshot-meta';
    [new Date(snap.fetched_at).toLocaleString(), `${snap.duration_ms ?? 0} ms`]
      .concat(snap.error_message ? ['partial data'] : [])
      .forEach((value) => {
        const span = document.createElement('span');
        span.textContent = value;
        meta.appendChild(span);
      });

    btn.append(row, meta);
    btn.addEventListener('click', () => loadSnapshotById(snap.id));
    els.historyList.appendChild(btn);
  });
}

async function loadSnapshotById(id) {
  showOverlay(`Loading snapshot #${id}...`);
  try {
    const res = await fetch(`/api/snapshots/${id}`);
    if (!res.ok) throw new Error(`GET /api/snapshots/${id} -> ${res.status}`);
    const data = await res.json();
    renderGraph(data.graph);
    setStatus(data.snapshot.status, data.snapshot.status);
    setCurrentSnapshot(data.snapshot, true);
    closeHistory();
  } catch (e) {
    console.error(e);
    setHistoryMessage(e.message);
  } finally {
    hideOverlay();
  }
}

function openHistory() {
  els.historyDrawer.hidden = false;
  loadSnapshots().catch((e) => {
    setHistoryMessage(e.message);
  });
}

function closeHistory() {
  els.historyDrawer.hidden = true;
}

async function init() {
  await new Promise(requestAnimationFrame);
  cy.resize();

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

  setStatus('fetching', 'loading');
  showOverlay('Loading last snapshot...');
  await loadAnnotations();
  let latest;
  try {
    latest = await loadLatest();
  } catch (e) {
    console.error(e);
    setStatus('error', 'load failed');
    els.overlayText.textContent = 'Failed to load snapshot.';
    return;
  }

  if (latest.snapshot) {
    renderGraph(latest.graph);
    setStatus(latest.snapshot.status, latest.snapshot.status);
    setCurrentSnapshot(latest.snapshot, false);
    hideOverlay();
  } else {
    setStatus('fetching', 'first fetch');
    showOverlay('Fetching from DigitalOcean...');
  }

  try {
    const fresh = await refresh();
    renderGraph(fresh.graph);
    const fetchedAt = new Date().toISOString();
    setStatus(fresh.snapshot.status, fresh.snapshot.status);
    setCurrentSnapshot({ ...fresh.snapshot, fetched_at: fetchedAt }, false);
    hideOverlay();
    if (fresh.snapshot.errors && Object.keys(fresh.snapshot.errors).length) {
      console.warn('Partial snapshot errors:', fresh.snapshot.errors);
    }
  } catch (e) {
    console.error(e);
    setStatus('error', 'refresh failed');
    els.overlayText.textContent = 'Refresh failed.';
    setTimeout(hideOverlay, 4000);
  }
}

els.themeToggle.addEventListener('click', () => {
  applyTheme(currentTheme() === 'light' ? 'dark' : 'light');
});

document.querySelectorAll('[data-theme-choice]').forEach((btn) => {
  btn.addEventListener('click', () => applyTheme(btn.dataset.themeChoice));
});

document.querySelectorAll('.settings-tab').forEach((btn) => {
  btn.addEventListener('click', () => activateSettingsTab(btn.dataset.settingsTab));
});

els.settingsOpen.addEventListener('click', () => openSettings('token'));
els.settingsClose.addEventListener('click', closeSettings);
els.settingsModal.addEventListener('click', (e) => {
  if (e.target.dataset.closeModal !== undefined) closeSettings();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (!els.settingsModal.hidden) closeSettings();
    if (!els.historyDrawer.hidden) closeHistory();
  }
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

els.search.addEventListener('input', applySearch);
els.layoutSelect.addEventListener('change', runLayout);
els.fitView.addEventListener('click', fitVisible);
els.resetLayout.addEventListener('click', runLayout);
els.zoomIn.addEventListener('click', () => cy.zoom({ level: cy.zoom() * 1.18, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }));
els.zoomOut.addEventListener('click', () => cy.zoom({ level: cy.zoom() / 1.18, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }));
els.clearIsolationToolbar.addEventListener('click', clearIsolation);
els.isolationClear.addEventListener('click', clearIsolation);
els.historyOpen.addEventListener('click', openHistory);
els.historyClose.addEventListener('click', closeHistory);
els.historyDrawer.addEventListener('click', (e) => {
  if (e.target.dataset.closeHistory !== undefined) closeHistory();
});
els.snapshotMode.addEventListener('click', async () => {
  showOverlay('Loading latest snapshot...');
  try {
    const latest = await loadLatest();
    renderGraph(latest.graph);
    setStatus(latest.snapshot.status, latest.snapshot.status);
    setCurrentSnapshot(latest.snapshot, false);
  } catch (e) {
    console.error(e);
    setStatus('error', 'load failed');
  } finally {
    hideOverlay();
  }
});

els.refresh.addEventListener('click', async () => {
  els.refresh.disabled = true;
  setStatus('fetching', 'fetching');
  showOverlay('Fetching from DigitalOcean...');
  try {
    const fresh = await refresh();
    renderGraph(fresh.graph);
    setStatus(fresh.snapshot.status, fresh.snapshot.status);
    setCurrentSnapshot({ ...fresh.snapshot, fetched_at: new Date().toISOString() }, false);
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
  const selected = cy.$('node:selected');
  let idx = 0;
  if (selected.length === 1) {
    const i = flagged.toArray().findIndex((n) => n.id() === selected.id());
    idx = i >= 0 ? (i + 1) % flagged.length : 0;
  }
  focusNode(flagged[idx]);
});

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

cy.on('mouseover', 'node', (evt) => evt.target.addClass('hover'));
cy.on('mouseout', 'node', (evt) => evt.target.removeClass('hover'));
cy.on('tap', 'node', (evt) => renderDetails(evt.target));
cy.on('tap', (evt) => {
  if (evt.target === cy) {
    els.detailsEmpty.hidden = false;
    els.detailsContent.hidden = true;
    els.detailsContent.replaceChildren();
  }
});

init();
