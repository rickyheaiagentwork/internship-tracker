/* ============================================================
   OPPORTUNITY TRACKER — Main Application Logic
   ============================================================ */

// ─── State ──────────────────────────────────────────────────
let entries = [];
let currentEditId = null;          // null = add mode, string = edit mode
let currentView = 'cards';         // 'cards' | 'calendar'
let calYear = new Date().getFullYear();
let calMonth = new Date().getMonth();

const STATUS_FLOW = [
  'Discovered','Saving','Tailored-CV','Applying','Applied','Screened',
  'OA-Pending','OA-Done','Interview-Scheduled','Tech-Int1','Tech-Int2',
  'Superday','Offer','Accepted','Rejected','Waitlisted','Archived'
];

// ─── ID Generation ──────────────────────────────────────────
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }

// ─── Data Persistence ───────────────────────────────────────
async function loadData() {
  try {
    const resp = await fetch('./data/tracker.json');
    if (!resp.ok) throw new Error('fetch failed');
    entries = await resp.json();
    if (!Array.isArray(entries)) entries = [];
  } catch {
    entries = [];
  }
  renderAll();
}

function saveToDisk() {
  // Write to in-memory blob; trigger download since we can't write to filesystem from browser
  const json = JSON.stringify(entries, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'tracker-export.json'; a.click();
  URL.revokeObjectURL(url);
}

function loadFromDisk(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => {
      try {
        const data = JSON.parse(r.result);
        if (!Array.isArray(data)) throw new Error('invalid');
        entries = data;
        saveToLocalState();
        renderAll();
        showToast('Data imported successfully.', 'success');
      } catch (e) { reject(e); }
    };
    r.onerror = () => reject(r.error);
    r.readAsText(file);
  });
}

function saveToLocalState() {
  try { localStorage.setItem('tracker-data', JSON.stringify(entries)); } catch {}
}

function loadFromCache() {
  try {
    const d = localStorage.getItem('tracker-data');
    if (d) { entries = JSON.parse(d); return true; }
  } catch {}
  return false;
}

// ─── Rendering ──────────────────────────────────────────────
function renderAll() {
  renderStats();
  renderCards();
  renderCalendar();
}

function getFilteredEntries() {
  const season = document.getElementById('filter-season').value;
  const type = document.getElementById('filter-type').value;
  const status = document.getElementById('filter-status').value;
  const workModel = document.getElementById('filter-work-model').value;
  const search = document.getElementById('filter-search').value.toLowerCase().trim();

  return entries.filter(e => {
    if (season && e.season !== season) return false;
    if (type && e.opportunity_type !== type) return false;
    if (status && e.status !== status) return false;
    if (workModel && e.work_model !== workModel) return false;
    if (search) {
      const hay = `${e.company} ${e.role_title} ${e.team_name || ''}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }
    return true;
  });
}

function renderStats() {
  const bar = document.getElementById('stats-bar');
  const total = entries.length;
  const counts = {};
  STATUS_FLOW.forEach(s => counts[s] = 0);
  entries.forEach(e => { if (counts[e.status] !== undefined) counts[e.status]++; });

  const cards = [
    { label: 'Total', count: total, color: '#e6edf3' },
    { label: 'Pending', count: ['Discovered','Saving','Tailored-CV','Applying'].reduce((a,s)=>a+counts[s],0), color: '#58a6ff' },
    { label: 'Applied', count: counts['Applied'], color: '#3fb950' },
    { label: 'Interviewing', count: ['Screened','OA-Pending','OA-Done','Interview-Scheduled','Tech-Int1','Tech-Int2','Superday'].reduce((a,s)=>a+counts[s],0), color: '#bc8cff' },
    { label: 'Offer', count: counts['Offer'], color: '#3fb950' },
    { label: 'Rejected', count: counts['Rejected'], color: '#f85149' },
  ];

  bar.innerHTML = cards.map(c => {
    const cls = c.label === 'Pending' ? '' : (c.label === 'Interviewing' ? '' : '');
    return `<div class="stat-card" onclick="">
      <div class="stat-count" style="color:${c.color}">${c.count}</div>
      <div class="stat-label">${c.label}</div>
    </div>`;
  }).join('');
}

function filterFromStats(label) {
  // Quick toggle: clicking stats doesn't drive much; let filters handle it
}

function getPriorityClass(score) {
  if (score >= 8) return 'priority-high';
  if (score >= 5) return 'priority-medium';
  return 'priority-low';
}

function getStatusBadgeClass(status) {
  const map = {
    'Discovered':'badge-discovered','Saving':'badge-saving','Tailored-CV':'badge-tailored-cv',
    'Applying':'badge-applying','Applied':'badge-applied','Screened':'badge-screened',
    'OA-Pending':'badge-oa-pending','OA-Done':'badge-oa-done',
    'Interview-Scheduled':'badge-interview','Tech-Int1':'badge-tech-int1','Tech-Int2':'badge-tech-int2',
    'Superday':'badge-superday','Offer':'badge-offer','Accepted':'badge-accepted',
    'Rejected':'badge-rejected','Waitlisted':'badge-waitlisted','Archived':'badge-archived'
  };
  return map[status] || 'badge-discovered';
}

function getSeasonClass(s) {
  if (s === 'Summer 2027') return 'season-summer';
  if (s === 'Fall 2026') return 'season-fall';
  if (s === 'Spring 2027') return 'season-spring';
  return '';
}

function getTypeClass(t) {
  if (t === 'Internship') return 'type-internship';
  if (t === 'Fellowship') return 'type-fellowship';
  if (t === 'Research-Internship') return 'type-research';
  return '';
}

function isUrgent(entry) {
  if (!entry.deadline) return false;
  const d = new Date(entry.deadline + 'T23:59:59');
  const now = new Date();
  const diff = (d - now) / (1000*60*60*24);
  return diff >= 0 && diff <= 7;
}

function formatDate(d) {
  if (!d) return '—';
  const dt = new Date(d + 'T00:00:00');
  return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function renderCards() {
  const grid = document.getElementById('card-grid');
  const filtered = getFilteredEntries();

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1;">
        <div class="empty-icon">📋</div>
        <div class="empty-title">${entries.length === 0 ? 'No entries yet' : 'No matches found'}</div>
        <div class="empty-desc">${entries.length === 0 ? 'Click "+ Add Entry" to start tracking your opportunities.' : 'Try adjusting your filters or search query.'}</div>
      </div>`;
    return;
  }

  grid.innerHTML = filtered.map(e => {
    const urgent = isUrgent(e) ? ' deadline-urgent' : '';
    const priorityClass = getPriorityClass(e.priority_score || 5);
    const statusClass = getStatusBadgeClass(e.status);
    const seasonClass = getSeasonClass(e.season);
    const typeClass = getTypeClass(e.opportunity_type);

    return `
      <div class="card${urgent}" data-id="${e.id}">
        <div class="card-header">
          <div>
            <div class="company-name">${escHtml(e.company)}</div>
          </div>
          <button class="card-menu-btn" onclick="toggleDropdown(event,'menu-${e.id}')">⋮</button>
        </div>
        ${e.role_title ? `<div class="role-title">${escHtml(e.role_title)}</div>` : ''}
        <div style="margin-bottom:8px;">
          ${seasonClass ? `<span class="season-badge ${seasonClass}">${escHtml(e.season)}</span>` : ''}
          ${typeClass ? `<span class="type-badge ${typeClass}">${escHtml(e.opportunity_type)}</span>` : ''}
        </div>
        <div class="card-meta">
          ${e.deadline ? `<span class="meta-item">📅 ${formatDate(e.deadline)}</span>` : ''}
          ${e.work_model ? `<span class="meta-item">🏠 ${escHtml(e.work_model)}</span>` : ''}
          ${e.location ? `<span class="meta-item">📍 ${escHtml(e.location)}</span>` : ''}
        </div>
        <div class="card-badges">
          <span class="status-badge ${statusClass}">${escHtml(e.status || 'Discovered')}</span>
          <span class="priority-badge ${priorityClass}">P${e.priority_score ?? 5}</span>
          ${e.is_paid ? '<span class="status-badge" style="background:rgba(63,185,80,0.1);color:#3fb950;border-color:rgba(63,185,80,0.3);">Paid</span>' : ''}
        </div>
        <div class="card-footer">
          <div class="card-links">
            ${e.posting_link ? `<a href="${escAttr(e.posting_link)}" target="_blank" rel="noopener">Posting ↗</a>` : ''}
            ${e.application_link ? `<a href="${escAttr(e.application_link)}" target="_blank" rel="noopener">Apply ↗</a>` : ''}
          </div>
          <div class="card-actions">
            <button class="btn btn-ghost btn-sm" onclick="editEntry('${e.id}')">✏️ Edit</button>
          </div>
        </div>
        <!-- Dropdown -->
        <div class="dropdown-menu" id="menu-${e.id}">
          <button class="dropdown-item" onclick="editEntry('${e.id}')">✏️ Edit</button>
          <button class="dropdown-item" onclick="duplicateEntry('${e.id}')">📋 Duplicate</button>
          ${e.posting_link ? `<a class="dropdown-item" href="${escAttr(e.posting_link)}" target="_blank" rel="noopener">🔗 Open Posting ↗</a>` : ''}
          <div class="dropdown-divider"></div>
          <button class="dropdown-item" onclick="deleteEntry('${e.id}')" style="color:var(--accent-red);">🗑 Delete</button>
        </div>
      </div>`;
  }).join('');
}

function escHtml(s) { if (!s) return ''; const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function escAttr(s) { if (!s) return ''; return s.replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

// ─── Dropdowns ──────────────────────────────────────────────
function toggleDropdown(evt, id) {
  evt.stopPropagation();
  document.querySelectorAll('.dropdown-menu.show').forEach(d => { if (d.id !== id) d.classList.remove('show'); });
  document.getElementById(id).classList.toggle('show');
}
document.addEventListener('click', () => document.querySelectorAll('.dropdown-menu.show').forEach(d => d.classList.remove('show')));

// ─── Entry CRUD ──────────────────────────────────────────────
function openModal(id) {
  currentEditId = id || null;
  const modal = document.getElementById('modal-overlay');
  document.getElementById('modal-title').textContent = id ? 'Edit Entry' : 'Add Entry';
  document.getElementById('btn-delete').style.display = id ? 'inline-flex' : 'none';

  if (id) {
    const e = entries.find(x => x.id === id);
    if (!e) return;
    fillForm(e);
  } else {
    clearForm();
  }

  // Reset to basic tab
  document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector('[data-tab="basic"]').classList.add('active');
  document.getElementById('tab-basic').classList.add('active');

  modal.classList.add('show');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('show');
  currentEditId = null;
}

function fillForm(e) {
  document.getElementById('f-company').value = e.company || '';
  document.getElementById('f-role-title').value = e.role_title || '';
  document.getElementById('f-season').value = e.season || '';
  document.getElementById('f-opportunity-type').value = e.opportunity_type || '';
  document.getElementById('f-status').value = e.status || 'Discovered';
  document.getElementById('f-work-model').value = e.work_model || '';
  document.getElementById('f-deadline').value = e.deadline || '';
  document.getElementById('f-priority-score').value = e.priority_score ?? 5;
  document.getElementById('f-posting-link').value = e.posting_link || '';
  document.getElementById('f-application-link').value = e.application_link || '';
  document.getElementById('f-director-link').value = e.director_link || '';
  document.getElementById('f-location').value = e.location || '';
  document.getElementById('f-team-name').value = e.team_name || '';
  document.getElementById('f-is-paid').checked = !!e.is_paid;
  document.getElementById('f-compensation-note').value = e.compensation_note || '';
  document.getElementById('f-role-summary').value = e.role_summary || '';
  document.getElementById('f-cover-letter-hook').value = e.cover_letter_hook || '';
  document.getElementById('f-personal-note').value = e.personal_note || '';
  document.getElementById('f-notes').value = e.notes || '';

  renderArrayItems('requirements-list', e.key_requirements || []);
  renderArrayItems('nice-haves-list', e.nice_to_haves || []);
  renderSuggestedProjects(e.suggested_projects || []);
  renderExistingMatches(e.existing_projects_match || []);
}

function clearForm() {
  ['f-company','f-role-title','f-season','f-opportunity-type','f-status','f-work-model',
   'f-deadline','f-posting-link','f-application-link','f-director-link','f-location',
   'f-team-name','f-compensation-note','f-role-summary','f-cover-letter-hook',
   'f-personal-note','f-notes'].forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
  document.getElementById('f-priority-score').value = 5;
  document.getElementById('f-is-paid').checked = false;
  clearArrayItems('requirements-list');
  clearArrayItems('nice-haves-list');
  document.getElementById('suggested-projects-list').innerHTML = '';
  document.getElementById('existing-projects-match-list').innerHTML = '';
}

function readForm() {
  return {
    company: document.getElementById('f-company').value.trim(),
    role_title: document.getElementById('f-role-title').value.trim(),
    season: document.getElementById('f-season').value,
    opportunity_type: document.getElementById('f-opportunity-type').value,
    status: document.getElementById('f-status').value || 'Discovered',
    work_model: document.getElementById('f-work-model').value,
    deadline: document.getElementById('f-deadline').value,
    priority_score: parseInt(document.getElementById('f-priority-score').value) || 5,
    posting_link: document.getElementById('f-posting-link').value.trim(),
    application_link: document.getElementById('f-application-link').value.trim(),
    director_link: document.getElementById('f-director-link').value.trim(),
    location: document.getElementById('f-location').value.trim(),
    team_name: document.getElementById('f-team-name').value.trim(),
    is_paid: document.getElementById('f-is-paid').checked,
    compensation_note: document.getElementById('f-compensation-note').value.trim(),
    role_summary: document.getElementById('f-role-summary').value.trim(),
    cover_letter_hook: document.getElementById('f-cover-letter-hook').value.trim(),
    key_requirements: readArrayItems('requirements-list'),
    nice_to_haves: readArrayItems('nice-haves-list'),
    suggested_projects: readSuggestedProjects(),
    existing_projects_match: readExistingMatches(),
    personal_note: document.getElementById('f-personal-note').value.trim(),
    notes: document.getElementById('f-notes').value.trim(),
  };
}

// ─── Array Helpers ──────────────────────────────────────────
function renderArrayItems(containerId, items) {
  const container = document.getElementById(containerId);
  container.innerHTML = items.map((item, i) => `
    <div class="array-item">
      <input type="text" class="form-input array-val" value="${escHtml(item)}">
      <button class="array-remove" onclick="this.parentElement.remove()">✕</button>
    </div>`).join('');
}

function clearArrayItems(containerId) {
  document.getElementById(containerId).innerHTML = '';
}

function readArrayItems(containerId) {
  return [...document.querySelectorAll(`#${containerId} .array-val`)].map(i => i.value.trim()).filter(Boolean);
}

// ─── Suggested Projects ──────────────────────────────────────
let suggestedProjectCounter = 0;
function renderSuggestedProjects(projs) {
  const container = document.getElementById('suggested-projects-list');
  if (projs.length === 0) { suggestedProjectCounter = 0; return; }
  container.innerHTML = projs.map((p, i) => buildSuggestedProjectCard(p, i)).join('');
  suggestedProjectCounter = projs.length;
}

function buildSuggestedProjectCard(p, idx) {
  const id = `sp-${Date.now()}-${idx}`;
  return `
    <div class="sub-object-card" id="${id}">
      <div class="sub-object-header">
        <span class="sub-object-title">Suggested Project ${idx + 1}</span>
        <button class="sub-object-remove" onclick="document.getElementById('${id}').remove()">✕</button>
      </div>
      <div class="form-row">
        <div class="form-group full">
          <label class="form-label">Project Reference</label>
          <input type="text" class="form-input sp-ref" value="${escAttr(p.project_ref || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group full">
          <label class="form-label">Rationale</label>
          <input type="text" class="form-input sp-rationale" value="${escAttr(p.rationale || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group full">
          <label class="form-label">Keywords to Emphasize</label>
          <input type="text" class="form-input sp-keywords" value="${escAttr(p.keywords_to_emphasize || '')}">
        </div>
      </div>
    </div>`;
}

function addSuggestedProject() {
  const container = document.getElementById('suggested-projects-list');
  const card = buildSuggestedProjectCard({}, suggestedProjectCounter);
  container.insertAdjacentHTML('beforeend', card);
  suggestedProjectCounter++;
}

function readSuggestedProjects() {
  return [...document.querySelectorAll('#suggested-projects-list .sub-object-card')].map(card => ({
    project_ref: card.querySelector('.sp-ref')?.value.trim() || '',
    rationale: card.querySelector('.sp-rationale')?.value.trim() || '',
    keywords_to_emphasize: card.querySelector('.sp-keywords')?.value.trim() || ''
  })).filter(p => p.project_ref || p.rationale);
}

// ─── Existing Projects Match ────────────────────────────────
function renderExistingMatches(matches) {
  const container = document.getElementById('existing-projects-match-list');
  if (matches.length === 0) return;
  container.innerHTML = matches.map((m, i) => buildExistingMatchCard(m, i)).join('');
}

function buildExistingMatchCard(m, idx) {
  const id = `ep-${Date.now()}-${idx}`;
  const strengths = ['Strong','Partial','Weak'];
  const opts = strengths.map(s => `<option value="${s}" ${m.match_strength===s?'selected':''}>${s}</option>`).join('');
  return `
    <div class="sub-object-card" id="${id}">
      <div class="sub-object-header">
        <span class="sub-object-title">Existing Match ${idx + 1}</span>
        <button class="sub-object-remove" onclick="document.getElementById('${id}').remove()">✕</button>
      </div>
      <div class="form-row">
        <div class="form-group half">
          <label class="form-label">Project Name</label>
          <input type="text" class="form-input ep-name" value="${escAttr(m.project_name || '')}">
        </div>
        <div class="form-group half">
          <label class="form-label">Match Strength</label>
          <select class="form-select ep-strength"><option value="">— select —</option>${opts}</select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group full">
          <label class="form-label">Gaps Identified</label>
          <input type="text" class="form-input ep-gaps" value="${escAttr(m.gaps_identified || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group full">
          <label class="form-label">Action Items</label>
          <input type="text" class="form-input ep-actions" value="${escAttr(m.action_items || '')}">
        </div>
      </div>
    </div>`;
}

function addExistingMatch() {
  const container = document.getElementById('existing-projects-match-list');
  const card = buildExistingMatchCard({}, Date.now());
  container.insertAdjacentHTML('beforeend', card);
}

function readExistingMatches() {
  return [...document.querySelectorAll('#existing-projects-match-list .sub-object-card')].map(card => ({
    project_name: card.querySelector('.ep-name')?.value.trim() || '',
    match_strength: card.querySelector('.ep-strength')?.value || '',
    gaps_identified: card.querySelector('.ep-gaps')?.value.trim() || '',
    action_items: card.querySelector('.ep-actions')?.value.trim() || ''
  })).filter(m => m.project_name);
}

// ─── Save / Delete ──────────────────────────────────────────
function saveEntry() {
  const company = document.getElementById('f-company').value.trim();
  const roleTitle = document.getElementById('f-role-title').value.trim();
  if (!company || !roleTitle) { showToast('Company and Role Title are required.', 'error'); return; }

  const data = readForm();
  // Remove empty keys from objects
  if (data.suggested_projects) data.suggested_projects = data.suggested_projects.filter(p => p.project_ref || p.rationale);
  if (data.existing_projects_match) data.existing_projects_match = data.existing_projects_match.filter(m => m.project_name);

  if (currentEditId) {
    const idx = entries.findIndex(e => e.id === currentEditId);
    if (idx >= 0) entries[idx] = { ...entries[idx], ...data, id: currentEditId };
    showToast('Entry updated.', 'success');
  } else {
    data.id = uid();
    data.created_at = new Date().toISOString();
    entries.unshift(data);
    showToast('Entry added.', 'success');
  }

  saveToLocalState();
  closeModal();
  renderAll();
}

function editEntry(id) { openModal(id); }

function deleteEntry(id) {
  if (!confirm('Delete this entry? This cannot be undone.')) return;
  entries = entries.filter(e => e.id !== id);
  saveToLocalState();
  renderAll();
  showToast('Entry deleted.', 'success');
}

function duplicateEntry(id) {
  const orig = entries.find(e => e.id === id);
  if (!orig) return;
  const dup = { ...JSON.parse(JSON.stringify(orig)), id: uid(), created_at: new Date().toISOString() };
  dup.company = dup.company + ' (copy)';
  dup.status = 'Saving';
  entries.unshift(dup);
  saveToLocalState();
  renderAll();
  showToast('Entry duplicated.', 'success');
}

// ─── Calendar View ──────────────────────────────────────────
function renderCalendar() {
  const grid = document.getElementById('cal-grid');
  const monthLabel = document.getElementById('cal-month-year');
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  monthLabel.textContent = `${months[calMonth]} ${calYear}`;

  const dayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  let html = dayNames.map(d => `<div class="calendar-day-name">${d}</div>`).join('');

  const firstDay = new Date(calYear, calMonth, 1).getDay();
  const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
  const prevDays = new Date(calYear, calMonth, 0).getDate();
  const today = new Date();
  const isCurrentMonth = today.getFullYear() === calYear && today.getMonth() === calMonth;

  // Get all entries with deadlines for the calendar month range (plus nearby)
  const deadlineEntries = [];
  entries.forEach(e => {
    if (!e.deadline) return;
    const d = new Date(e.deadline + 'T00:00:00');
    if (d.getFullYear() === calYear && d.getMonth() === calMonth) {
      deadlineEntries.push(e);
    }
  });

  // Previous month trailing days
  for (let i = firstDay - 1; i >= 0; i--) {
    html += `<div class="calendar-day other-month"><div class="day-number">${prevDays - i}</div></div>`;
  }

  // Current month days
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${calYear}-${String(calMonth+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    const isToday = isCurrentMonth && today.getDate() === day;
    const dayEntries = deadlineEntries.filter(e => e.deadline === dateStr);
    const dots = dayEntries.slice(0, 3).map(e => {
      const urgent = isUrgent(e) ? 'background:rgba(248,81,73,0.35);color:#fff;' : '';
      return `<div class="deadline-item" style="${urgent}" onclick="editEntry('${e.id}')" title="${escAttr(e.company)} — ${escAttr(e.role_title)}">${escHtml(e.company)}: ${escHtml(e.role_title)}</div>`;
    }).join('');
    if (dayEntries.length > 3) dots += `<div class="deadline-item" style="background:rgba(139,148,158,0.2);color:var(--text-muted)">+${dayEntries.length - 3} more</div>`;

    html += `<div class="calendar-day${isToday ? ' today' : ''}">
      <div class="day-number">${day}</div>${dots}</div>`;
  }

  // Next month leading days
  const totalCells = firstDay + daysInMonth;
  const remaining = (7 - (totalCells % 7)) % 7;
  for (let i = 1; i <= remaining; i++) {
    html += `<div class="calendar-day other-month"><div class="day-number">${i}</div></div>`;
  }

  grid.innerHTML = html;
}

function showView(view) {
  currentView = view;
  document.querySelectorAll('.view-btn').forEach(b => b.classList.toggle('active', b.dataset.view === view));
  document.getElementById('view-cards').style.display = view === 'cards' ? '' : 'none';
  const calContainer = document.getElementById('view-calendar');
  calContainer.classList.toggle('active', view === 'calendar');
  if (view === 'calendar') renderCalendar();
}

// ─── Toast ──────────────────────────────────────────────────
function showToast(msg, type='success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}

// ─── Event Wiring ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  // Load data (filesystem JSON first, then local storage fallback)
  const loaded = loadFromCache();
  if (!loaded) await loadData();

  renderAll();

  // Add button
  document.getElementById('btn-add').addEventListener('click', () => openModal(null));

  // Modal close
  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('btn-cancel').addEventListener('click', closeModal);
  document.getElementById('modal-overlay').addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal(); });

  // Save
  document.getElementById('btn-save').addEventListener('click', saveEntry);

  // Delete
  document.getElementById('btn-delete').addEventListener('click', () => {
    if (currentEditId) deleteEntry(currentEditId);
    closeModal();
  });

  // Filter changes
  ['filter-season','filter-type','filter-status','filter-work-model'].forEach(id => {
    document.getElementById(id).addEventListener('change', () => renderCards());
  });
  document.getElementById('filter-search').addEventListener('input', () => renderCards());

  // Clear filters
  document.getElementById('btn-clear-filters').addEventListener('click', () => {
    document.getElementById('filter-season').value = '';
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-work-model').value = '';
    document.getElementById('filter-search').value = '';
    renderCards();
  });

  // View toggle
  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view));
  });

  // Calendar nav
  document.getElementById('cal-prev').addEventListener('click', () => { calMonth--; if (calMonth < 0) { calMonth = 11; calYear--; } renderCalendar(); });
  document.getElementById('cal-next').addEventListener('click', () => { calMonth++; if (calMonth > 11) { calMonth = 0; calYear++; } renderCalendar(); });

  // Export
  document.getElementById('btn-export').addEventListener('click', saveToDisk);

  // Import
  document.getElementById('btn-import').addEventListener('click', () => document.getElementById('import-input').click());
  document.getElementById('import-input').addEventListener('change', (e) => {
    if (e.target.files[0]) { loadFromDisk(e.target.files[0]).catch(err => showToast('Import failed: ' + err.message, 'error')); e.target.value = ''; }
  });

  // Tab switching in modal
  document.querySelectorAll('.modal-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    });
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') { e.preventDefault(); openModal(null); }
  });
});
