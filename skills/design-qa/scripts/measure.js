// FLIK design QA: browser pass. Paste into the page (javascript_tool) on each screen.
// Returns a compact JSON report of what's visible right now.
(() => {
  const MAX = 8;
  const vis = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && r.right > 0 && r.left < innerWidth && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0; };
  const name = el => { let n = el.tagName.toLowerCase(); if (el.id) return n + '#' + el.id;
    const c = [...el.classList].slice(0, 2).join('.'); return c ? n + '.' + c : n; };
  const path = el => { const p = []; for (let e = el; e && e !== document.body && p.length < 3; e = e.parentElement) p.unshift(name(e)); return p.join(' > '); };
  const txt = el => (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 40);
  const all = [...document.querySelectorAll('body *')].filter(vis);
  const out = { viewport: `${innerWidth}x${innerHeight}`, hash: location.hash };

  // 1. Uneven gaps between repeated siblings (same tag + class), e.g. cards, rows, fields
  const uneven = [];
  for (const p of new Set(all.map(e => e.parentElement))) {
    if (!p) continue;
    const kids = [...p.children].filter(vis);
    const key = k => k.tagName + '.' + k.className, gapsBy = {};
    for (let i = 1; i < kids.length; i++) {           // only directly adjacent siblings of the same kind
      const a = kids[i - 1], b = kids[i]; if (key(a) !== key(b)) continue;
      const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
      const g = Math.round(Math.abs(rb.top - ra.top) < 2 ? rb.left - ra.right : rb.top - ra.bottom);
      if (g >= 0 && g < 200) (gapsBy[key(a)] ||= { el: a, g: [] }).g.push(g);
    }
    for (const { el, g } of Object.values(gapsBy))
      if (g.length >= 2 && Math.max(...g) - Math.min(...g) > 2) uneven.push(`${path(el)}: gaps ${[...new Set(g)].join('/')}px`);
  }
  out.unevenGaps = uneven.slice(0, MAX);

  // 2. Off-grid computed spacing (odd px) on visible elements
  const odd = {};
  for (const el of all) {
    const s = getComputedStyle(el);
    for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'marginTop', 'marginBottom', 'rowGap', 'columnGap']) {
      const v = parseFloat(s[p]); if (v > 2 && Math.round(v) % 2) (odd[`${p} ${Math.round(v)}px`] ||= []).push(name(el));
    }
  }
  out.offGridSpacing = Object.entries(odd).sort((a, b) => b[1].length - a[1].length).slice(0, MAX)
    .map(([k, v]) => `${k} ×${v.length} (${[...new Set(v)].slice(0, 3).join(', ')})`);

  // 3. Horizontal overflow (page and inside elements that don't scroll on purpose)
  out.pageScrollsSideways = document.documentElement.scrollWidth > innerWidth + 1;
  out.overflowing = all.filter(el => { const s = getComputedStyle(el);
      return el.scrollWidth > el.clientWidth + 1 && !/(auto|scroll|hidden|clip)/.test(s.overflowX) && el.clientWidth > 0; })
    .filter(el => el.children.length || el.innerText).slice(0, MAX).map(el => `${path(el)} (+${el.scrollWidth - el.clientWidth}px)`);
  out.clippedText = all.filter(el => { const s = getComputedStyle(el);
      return s.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth && !el.title; })
    .slice(0, MAX).map(el => `${path(el)} "${txt(el)}" (no title/tooltip)`);

  // 4. Small tap targets
  const minT = innerWidth < 768 ? 40 : 28;
  out.smallTargets = all.filter(el => el.matches('button, a[href], [role=button], input:not([type=hidden]), select'))
    .filter(el => { const r = el.getBoundingClientRect(); return r.height < minT || r.width < minT; })
    .slice(0, MAX).map(el => { const r = el.getBoundingClientRect(); return `${path(el)} "${txt(el)}" ${Math.round(r.width)}x${Math.round(r.height)}`; });

  // 5. Low text contrast (WCAG AA)
  const rgb = c => (c.match(/[\d.]+/g) || []).map(Number);
  const lum = ([r, g, b]) => { const f = v => (v /= 255) <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length === 3 || c[3] > .5) return c.slice(0, 3); } return [255, 255, 255]; };
  const low = [];
  for (const el of all) {
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const s = getComputedStyle(el), fs = parseFloat(s.fontSize), big = fs >= 18.66 || (fs >= 14 && +s.fontWeight >= 700);
    const a = lum(rgb(s.color)), b = lum(bgOf(el)), ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    if (ratio < (big ? 3 : 4.5)) low.push(`${path(el)} "${txt(el)}" ${ratio.toFixed(1)}:1 at ${fs}px`);
  }
  out.lowContrast = low.slice(0, MAX); out.lowContrastCount = low.length;

  // 6. Type in use, to spot one-off sizes on this screen
  const sizes = {}; all.forEach(el => { if (el.childNodes[0]?.nodeType === 3 && el.innerText?.trim()) { const k = getComputedStyle(el).fontSize; sizes[k] = (sizes[k] || 0) + 1; } });
  out.fontSizes = Object.entries(sizes).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}×${v}`).join(' ');

  // 7. Missing labels on what's visible
  out.unlabelled = all.filter(el => el.matches('button, a[href], input:not([type=hidden]), select, textarea'))
    .filter(el => !txt(el) && !el.labels?.length && !el.title && !el.placeholder).slice(0, MAX).map(path);
  return out;
})();
