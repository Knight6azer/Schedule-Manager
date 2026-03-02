/* ============================================================
   Schedule Manager — JavaScript
   AJAX task toggle/delete, live filter, toasts, sidebar
   ============================================================ */

// ── Toast System ─────────────────────────────────────────────
const toastContainer = document.getElementById('toast-container');

function showToast(message, type = 'info', duration = 3500) {
  const icons = {
    success: '✓', danger: '✕', info: 'ℹ', warning: '⚠'
  };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span style="font-weight:700;font-size:0.95rem;">${icons[type] || 'ℹ'}</span>
    <span>${message}</span>
    <button class="toast-close" onclick="closeToast(this.parentElement)">×</button>
  `;
  toastContainer.appendChild(toast);
  setTimeout(() => closeToast(toast), duration);
}

function closeToast(el) {
  if (!el || el.classList.contains('hide')) return;
  el.classList.add('hide');
  setTimeout(() => el.remove(), 280);
}

// ── Sidebar Toggle ────────────────────────────────────────────
const sidebar  = document.getElementById('sidebar');
const overlay  = document.getElementById('sidebar-overlay');
const menuBtn  = document.getElementById('menu-btn');

function openSidebar()  {
  sidebar?.classList.add('open');
  overlay?.classList.add('visible');
}
function closeSidebar() {
  sidebar?.classList.remove('open');
  overlay?.classList.remove('visible');
}

menuBtn?.addEventListener('click', openSidebar);
overlay?.addEventListener('click', closeSidebar);

// ── Flash → Toast bridge ──────────────────────────────────────
// Maps Flask flash categories to toast types
document.querySelectorAll('.server-flash').forEach(el => {
  const type = el.dataset.category || 'info';
  showToast(el.dataset.message, type === 'danger' ? 'danger'
    : type === 'success' ? 'success'
    : type === 'warning' ? 'warning' : 'info');
});

// ── AJAX Task Toggle ──────────────────────────────────────────
async function toggleTask(id, cardEl) {
  try {
    const res  = await fetch(`/api/tasks/${id}/toggle`, { method: 'PATCH' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed');

    const checkEl = cardEl.querySelector('.task-check');
    const titleEl = cardEl.querySelector('.task-title');
    const statusChip = cardEl.querySelector('.status-chip');

    if (data.status === 'Completed') {
      checkEl.classList.add('done');
      cardEl.classList.add('status-completed');
      titleEl.classList.add('done');
      if (statusChip) {
        statusChip.className = 'chip chip-status-completed status-chip';
        statusChip.textContent = 'Completed';
      }
      showToast('Task marked complete ✓', 'success');
    } else {
      checkEl.classList.remove('done');
      cardEl.classList.remove('status-completed');
      titleEl.classList.remove('done');
      if (statusChip) {
        statusChip.className = 'chip chip-status-pending status-chip';
        statusChip.textContent = 'Pending';
      }
      showToast('Task reopened', 'info');
    }
    refreshStats();
  } catch (e) {
    showToast('Could not update task', 'danger');
  }
}

// ── AJAX Task Delete ──────────────────────────────────────────
async function deleteTask(id, cardEl, btn) {
  if (!confirm('Delete this task? This cannot be undone.')) return;
  btn.disabled = true;

  try {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();

    cardEl.classList.add('removing');
    setTimeout(() => {
      cardEl.remove();
      checkEmpty();
      showToast('Task deleted', 'danger');
      refreshStats();
    }, 360);
  } catch {
    btn.disabled = false;
    showToast('Could not delete task', 'danger');
  }
}

// ── Stats refresh ─────────────────────────────────────────────
async function refreshStats() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();
    const map  = { total: 'stat-total', pending: 'stat-pending', in_progress: 'stat-progress', completed: 'stat-completed' };
    for (const [key, id] of Object.entries(map)) {
      const el = document.getElementById(id);
      if (el) el.textContent = data[key] ?? 0;
    }
  } catch { /* silent */ }
}

// ── Live filter ───────────────────────────────────────────────
const searchInput  = document.getElementById('search-input');
const filterTabs   = document.querySelectorAll('.filter-tab');
const categorySel  = document.getElementById('category-filter');
const prioritySel  = document.getElementById('priority-filter');
const allCards     = () => document.querySelectorAll('.task-card');

function applyFilters() {
  const q        = (searchInput?.value || '').toLowerCase();
  const status   = document.querySelector('.filter-tab.active')?.dataset.status || '';
  const cat      = categorySel?.value || '';
  const priority = prioritySel?.value || '';

  let visible = 0;
  allCards().forEach(card => {
    const title  = card.dataset.title?.toLowerCase() || '';
    const cStat  = card.dataset.status || '';
    const cCat   = card.dataset.category || '';
    const cPri   = card.dataset.priority || '';

    const show = (q === '' || title.includes(q))
      && (status === '' || cStat === status)
      && (cat    === '' || cCat  === cat)
      && (priority === '' || cPri === priority);

    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });
  checkEmpty(visible);
}

function checkEmpty(count) {
  const tasksGrid = document.getElementById('tasks-grid');
  if (!tasksGrid) return;
  const actual = count !== undefined ? count :
    [...allCards()].filter(c => c.style.display !== 'none').length;
  let emptyEl = document.getElementById('empty-state');
  if (actual === 0) {
    if (!emptyEl) {
      emptyEl = document.createElement('div');
      emptyEl.id = 'empty-state';
      emptyEl.className = 'empty-state';
      emptyEl.innerHTML = `
        <div class="empty-icon">📋</div>
        <h3>No tasks here</h3>
        <p>Try changing your filters or create a new task.</p>
      `;
      tasksGrid.appendChild(emptyEl);
    }
  } else {
    emptyEl?.remove();
  }
}

filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    applyFilters();
  });
});

searchInput?.addEventListener('input', applyFilters);
categorySel?.addEventListener('change', applyFilters);
prioritySel?.addEventListener('change', applyFilters);

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkEmpty();

  // Animate cards in
  allCards().forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(16px)';
    setTimeout(() => {
      card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      card.style.opacity = '1';
      card.style.transform = '';
    }, i * 60);
  });
});
