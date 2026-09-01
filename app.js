const state = { openings: [], watchlist: [], meta: null };

const el = (id) => document.getElementById(id);

function escHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escUrl(url) {
  if (!url || !/^https?:\/\//i.test(url)) return '#';
  return escHtml(url);
}

async function load() {
  const [openings, watchlist, meta] = await Promise.all([
    fetch('./data/openings.json').then((r) => r.json()),
    fetch('./data/watchlist.json').then((r) => r.json()),
    fetch('./data/meta.json').then((r) => r.json()),
  ]);
  state.openings = openings;
  state.watchlist = watchlist;
  state.meta = meta;
  render();
}

function filters() {
  return {
    q: el('q').value.trim().toLowerCase(),
    season: el('season').value,
    category: el('category').value,
    bucket: el('bucket').value,
  };
}

function match(item, f, kind) {
  if (f.bucket === 'open' && kind !== 'open') return false;
  if (f.bucket === 'watch' && kind !== 'watch') return false;
  if (f.season && item.season !== f.season) return false;
  if (f.category && item.category !== f.category) return false;
  if (f.q) {
    const hay = `${item.company} ${item.role_title || item.target_role || ''} ${item.notes || ''}`.toLowerCase();
    if (!hay.includes(f.q)) return false;
  }
  return true;
}

function badge(text, cls) {
  return `<span class="badge ${escHtml(cls)}">${escHtml(text)}</span>`;
}

function openCard(item) {
  const degrees = escHtml((item.degree_level || []).join(' · '));
  return `<article class="card">
    <div class="card-top">
      <div>
        <div class="company">Tier ${escHtml(item.tier)} · ${escHtml(item.company)}</div>
        <h3 class="role">${escHtml(item.role_title)}</h3>
      </div>
      <div class="badges">
        ${badge('Open', 'open')}
        ${badge(item.season, 'soft')}
        ${badge(item.category, 'soft')}
      </div>
    </div>
    <div class="details">${escHtml(item.location || '—')} · ${escHtml(item.work_model || '—')} · ${degrees || 'Any'} · verified ${escHtml(item.verified_at)}</div>
    ${item.notes ? `<div class="notes">${escHtml(item.notes)}</div>` : ''}
    <div class="actions">
      <a href="${escUrl(item.application_url || item.posting_url)}" target="_blank" rel="noopener noreferrer">Apply</a>
      ${item.posting_url && item.application_url && item.posting_url !== item.application_url
        ? `<a class="secondary" href="${escUrl(item.posting_url)}" target="_blank" rel="noopener noreferrer">Posting</a>`
        : ''}
    </div>
  </article>`;
}

function watchCard(item) {
  return `<article class="card">
    <div class="card-top">
      <div>
        <div class="company">Tier ${escHtml(item.tier)} · ${escHtml(item.company)}</div>
        <h3 class="role">${escHtml(item.target_role)}</h3>
      </div>
      <div class="badges">
        ${badge('Watch', 'watch')}
        ${badge(item.season, 'soft')}
        ${badge(item.category, 'soft')}
      </div>
    </div>
    <div class="details">Expected open: ${escHtml(item.expected_open)}</div>
    ${item.notes ? `<div class="notes">${escHtml(item.notes)}</div>` : ''}
    <div class="actions">
      <a class="secondary" href="${escUrl(item.careers_url)}" target="_blank" rel="noopener noreferrer">Careers page</a>
    </div>
  </article>`;
}

function render() {
  const f = filters();
  const opens = state.openings.filter((i) => match(i, f, 'open'));
  const watches = state.watchlist.filter((i) => match(i, f, 'watch'));

  el('meta-box').innerHTML = `
    <strong>Last verified:</strong> ${escHtml(state.meta.last_full_verify)}<br/>
    <strong>Open:</strong> ${escHtml(state.openings.length)} · <strong>Watch:</strong> ${escHtml(state.watchlist.length)}<br/>
    Seasons: ${escHtml((state.meta.target_seasons || []).join(', '))}
  `;

  el('stats').innerHTML = `
    <span class="chip">${opens.length} open shown</span>
    <span class="chip">${watches.length} watch shown</span>
    <span class="chip">No fake listings</span>
  `;

  el('open-list').innerHTML = opens.length
    ? opens.map(openCard).join('')
    : `<div class="empty">No open listings match these filters.</div>`;

  el('watch-list').innerHTML = watches.length
    ? watches.map(watchCard).join('')
    : `<div class="empty">No watchlist items match these filters.</div>`;
}

['q', 'season', 'category', 'bucket'].forEach((id) => {
  el(id).addEventListener('input', render);
  el(id).addEventListener('change', render);
});

load().catch((err) => {
  el('meta-box').textContent = `Failed to load data: ${err.message}`;
});
