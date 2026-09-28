/* ============================================================
   Schedule Manager — JavaScript
   AJAX task toggle/delete, live filter, toasts, sidebar
   ============================================================ */

// ── Toast System ─────────────────────────────────────────────
const toastContainer = document.getElementById('toast-container');
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

function csrfHeaders() {
  return csrfToken ? { 'X-CSRFToken': csrfToken } : {};
}

function showToast(message, type = 'info', duration = 3500) {
  if (!toastContainer) return;
  const icons = {
    success: '✓', danger: '✕', info: 'ℹ', warning: '⚠'
  };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icon = document.createElement('span');
  icon.setAttribute('aria-hidden', 'true');
  icon.textContent = icons[type] || icons.info;
  const text = document.createElement('span');
  text.textContent = message;
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'toast-close';
  close.setAttribute('aria-label', 'Dismiss notification');
  close.textContent = '×';
  close.addEventListener('click', () => closeToast(toast));
  toast.append(icon, text, close);
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
  menuBtn?.setAttribute('aria-expanded', 'true');
  sidebar?.querySelector('a, button')?.focus();
}
function closeSidebar() {
  const wasOpen = sidebar?.classList.contains('open');
  sidebar?.classList.remove('open');
  overlay?.classList.remove('visible');
  menuBtn?.setAttribute('aria-expanded', 'false');
  if (wasOpen) menuBtn?.focus();
}

menuBtn?.addEventListener('click', openSidebar);
overlay?.addEventListener('click', closeSidebar);
sidebar?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeSidebar));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && sidebar?.classList.contains('open')) closeSidebar();
});

document.addEventListener('click', event => {
  if (!(event.target instanceof Element)) return;
  const button = event.target.closest('button[data-task-action]');
  const card = button?.closest('.task-card');
  if (!button || !card) return;

  if (button.dataset.taskAction === 'toggle') {
    toggleTask(button.dataset.taskId, card);
  } else if (button.dataset.taskAction === 'delete') {
    deleteTask(button.dataset.taskId, card, button);
  }
});

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
  const button = cardEl.querySelector('.task-check');
  if (!button || button.disabled) return;
  button.disabled = true;

  try {
    const res  = await fetch(`/api/tasks/${id}/toggle`, { method: 'PATCH', headers: csrfHeaders() });
    if (!res.ok) throw new Error();
    const data = await res.json();

    const checkEl = cardEl.querySelector('.task-check');
    const titleEl = cardEl.querySelector('.task-title');
    const statusChip = cardEl.querySelector('.status-chip');
    cardEl.dataset.status = data.status;

    if (data.status === 'Completed') {
      checkEl.classList.add('done');
      cardEl.classList.add('status-completed');
      titleEl.classList.add('done');
      checkEl.setAttribute('aria-pressed', 'true');
      checkEl.setAttribute('aria-label', `Reopen task: ${titleEl.textContent}`);
      if (statusChip) {
        statusChip.className = 'chip chip-status-completed status-chip';
        statusChip.textContent = 'Completed';
      }
      showToast('Task marked complete.', 'success');
    } else {
      checkEl.classList.remove('done');
      cardEl.classList.remove('status-completed');
      titleEl.classList.remove('done');
      checkEl.setAttribute('aria-pressed', 'false');
      checkEl.setAttribute('aria-label', `Complete task: ${titleEl.textContent}`);
      if (statusChip) {
        statusChip.className = 'chip chip-status-pending status-chip';
        statusChip.textContent = 'Pending';
      }
      showToast('Task reopened', 'info');
    }
    applyFilters();
    try {
      await refreshStats();
    } catch {
      showToast('Task updated, but the summary could not refresh. Reload the page.', 'warning');
    }
  } catch {
    showToast('Could not update the task. Please try again.', 'danger');
  } finally {
    button.disabled = false;
  }
}

// ── AJAX Task Delete ──────────────────────────────────────────
async function deleteTask(id, cardEl, btn) {
  if (!confirm('Delete this task? This cannot be undone.')) return;
  btn.disabled = true;

  try {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE', headers: csrfHeaders() });
    if (!res.ok) throw new Error();

    cardEl.classList.add('removing');
    setTimeout(async () => {
      cardEl.remove();
      checkEmpty();
      showToast('Task deleted.', 'success');
      try {
        await refreshStats();
      } catch {
        showToast('Task deleted, but the summary could not refresh. Reload the page.', 'warning');
      }
    }, 150);
  } catch {
    btn.disabled = false;
    showToast('Could not delete the task. Please try again.', 'danger');
  }
}

// ── Stats refresh ─────────────────────────────────────────────
async function refreshStats() {
  const res = await fetch('/api/stats');
  if (!res.ok) throw new Error('Could not refresh task counts.');
  const data = await res.json();
  const map = { total: 'stat-total', pending: 'stat-pending', in_progress: 'stat-progress', completed: 'stat-completed' };
  for (const [key, id] of Object.entries(map)) {
    const el = document.getElementById(id);
    if (el) el.textContent = data[key] ?? 0;
  }
}

// ── Live filter ───────────────────────────────────────────────
const searchInput  = document.getElementById('search-input');
const filterTabs   = document.querySelectorAll('.filter-tab');
const categorySel  = document.getElementById('category-filter');
const prioritySel  = document.getElementById('priority-filter');
const recurringToggle = document.getElementById('is_recurring');
const recurrenceFields = document.getElementById('recurrence-fields');
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
      emptyEl.setAttribute('role', 'status');
      const heading = document.createElement('h3');
      const message = document.createElement('p');
      heading.textContent = 'No tasks match these filters.';
      message.textContent = 'Try changing a filter or search term.';
      emptyEl.append(heading, message);
      tasksGrid.appendChild(emptyEl);
    }
  } else {
    emptyEl?.remove();
  }
}

filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => {
      t.classList.remove('active');
      t.setAttribute('aria-pressed', 'false');
    });
    tab.classList.add('active');
    tab.setAttribute('aria-pressed', 'true');
    applyFilters();
  });
});

searchInput?.addEventListener('input', applyFilters);
categorySel?.addEventListener('change', applyFilters);
prioritySel?.addEventListener('change', applyFilters);
recurringToggle?.addEventListener('change', () => {
  if (recurrenceFields) recurrenceFields.hidden = !recurringToggle.checked;
});

checkEmpty();
