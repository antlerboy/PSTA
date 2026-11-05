/* Keep the approved three-item selection current between static-site builds. */
(function (root) {
  'use strict';
  function select(candidates, now) {
    const topics = new Set(), links = new Set(), selected = [];
    for (const item of candidates) {
      if (item.valid_from && now < Date.parse(item.valid_from)) continue;
      if (item.expires_at && now >= Date.parse(item.expires_at)) continue;
      const topic = item.topic.toLowerCase(), link = item.href.toLowerCase();
      if (topics.has(topic) || links.has(link)) continue;
      selected.push(item); topics.add(topic); links.add(link);
      if (selected.length === 3) return selected;
    }
    throw new Error('Not enough distinct current items for the three-item panel');
  }

  function mount(panel) {
    const data = JSON.parse(panel.querySelector('[data-latest-data]').textContent);
    const grid = panel.querySelector('[data-latest-grid]');
    let timer;
    const make = (tag, text, className) => {
      const node = document.createElement(tag);
      if (text) node.textContent = text;
      if (className) node.className = className;
      return node;
    };
    const link = (item, text, className) => {
      const node = make('a', text, className);
      node.href = item.href;
      if (data.external_tabs && item.href.startsWith('https://')) {
        node.target = '_blank'; node.rel = 'noopener noreferrer';
      }
      return node;
    };
    const refresh = () => {
      clearTimeout(timer);
      const now = Date.now(), items = select(data.candidates, now);
      const cards = items.map(item => {
        const card = make('article');
        const heading = make('h3'); heading.append(link(item, item.title));
        const read = link(item, item.link_label + ' ', data.class_prefix + '-read');
        const arrow = make('span', item.href.startsWith('https://') ? '↗' : '→');
        arrow.setAttribute('aria-hidden', 'true'); read.append(arrow);
        card.append(make('p', item.source, data.class_prefix + '-source'), heading, make('p', item.summary), read);
        return card;
      });
      grid.replaceChildren(...cards);
      panel.dataset.latestAsOf = new Date(now).toISOString();
      panel.dataset.latestFallback = String(items.some(item => item.selection_role === 'fallback'));
      const next = data.candidates.flatMap(item => [item.valid_from, item.expires_at]).filter(Boolean).map(Date.parse).filter(time => time > now);
      if (next.length) timer = setTimeout(refresh, Math.min(Math.min(...next) - now + 10, 2147483647));
    };
    refresh();
    document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
    root.addEventListener('pageshow', refresh);
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = {select};
  if (typeof document !== 'undefined') {
    document.querySelectorAll('[data-latest-panel]').forEach(panel => {
      try { mount(panel); } catch (error) { console.error('Curated latest panel:', error); }
    });
  }
})(typeof window !== 'undefined' ? window : globalThis);
