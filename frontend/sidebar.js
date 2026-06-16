/* sidebar.js – Componente de sidebar + modal de configuración */
(function () {
  'use strict';

  /* ── Inyectar CSS ─────────────────────────────────────────────────────── */
  if (!document.getElementById('sidebar-css-link')) {
    const lnk = document.createElement('link');
    lnk.id = 'sidebar-css-link';
    lnk.rel = 'stylesheet';
    lnk.href = '/sidebar.css';
    document.head.appendChild(lnk);
  }

  const path = window.location.pathname;
  const isIndex = path.endsWith('index.html') || path === '/' || path === '';
  const isUsuario = path.endsWith('usuario.html');
  const isDetalle = path.endsWith('detalle.html');

  /* ── HTML del Sidebar ─────────────────────────────────────────────────── */
  const sidebarHTML = `
<aside class="sidebar" id="app-sidebar">
  <div class="sidebar-logo">
    <a href="/" class="sidebar-logo-link" title="Inicio">
      <svg width="34" height="34" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="11" fill="#e60023"/>
        <path d="M12 2C6.48 2 2 6.48 2 12c0 4.24 2.65 7.86 6.39 9.29-.09-.78-.17-1.98.03-2.83.19-.77 1.27-5.22 1.27-5.22s-.32-.65-.32-1.6c0-1.5.87-2.62 1.95-2.62.92 0 1.37.69 1.37 1.52 0 .93-.59 2.32-.89 3.6-.25 1.08.53 1.96 1.58 1.96 1.9 0 3.36-2 3.36-4.89 0-2.56-1.84-4.34-4.47-4.34-3.04 0-4.83 2.28-4.83 4.64 0 .92.35 1.9.79 2.44.09.1.1.19.07.29-.08.33-.26 1.08-.3 1.23-.05.2-.17.24-.38.14-1.43-.67-2.32-2.77-2.32-4.46 0-3.62 2.63-6.95 7.59-6.95 3.98 0 7.07 2.84 7.07 6.62 0 3.96-2.49 7.14-5.95 7.14-1.16 0-2.26-.6-2.63-1.31l-.72 2.68c-.26.99-.95 2.24-1.41 2.99C10.73 21.96 11.36 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2z" fill="white"/>
      </svg>
    </a>
  </div>

  <nav class="sidebar-nav">
    <a href="/" class="sidebar-btn ${isIndex ? 'active' : ''}" title="Inicio" id="sb-home">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
    </a>

    <button class="sidebar-btn" title="Buscar / Explorar" id="sb-explore">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
    </button>

    <button class="sidebar-btn" title="Nueva publicación" id="sb-create">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="3"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
      </svg>
    </button>

    <button class="sidebar-btn" title="Notificaciones" id="sb-notif">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
    </button>

    <button class="sidebar-btn" title="Mensajes" id="sb-msg">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </button>
  </nav>

  <div class="sidebar-bottom">
    <a href="usuario.html" class="sidebar-btn sidebar-profile-btn ${isUsuario ? 'active' : ''}" title="Mi Perfil" id="sb-profile">
      <img src="/avatar.png" alt="Perfil" id="sidebar-avatar-img" class="sidebar-avatar">
    </a>
    <button class="sidebar-btn" title="Configuración" id="sb-settings">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    </button>
  </div>
</aside>`;

  /* ── HTML del Modal de Configuración ──────────────────────────────────── */
  const modalHTML = `
<div class="settings-modal-overlay" id="settings-modal-overlay">
  <div class="settings-modal">
    <div class="settings-modal-header">
      <h3>Configuración</h3>
      <button class="settings-modal-close" id="settings-modal-close">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="settings-section">
      <p class="settings-section-title">Apariencia</p>
      <div class="settings-row">
        <div class="settings-row-info">
          <span class="settings-row-icon">🌙</span>
          <span class="settings-row-label">Modo oscuro</span>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" id="toggle-dark-mode">
          <span class="toggle-slider"></span>
        </label>
      </div>
      <div class="settings-row" id="nsfw-settings-row">
        <div class="settings-row-info">
          <span class="settings-row-icon">🔞</span>
          <span class="settings-row-label">Contenido para adultos (NSFW)</span>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" id="toggle-nsfw">
          <span class="toggle-slider nsfw-slider"></span>
        </label>
      </div>
    </div>

    <div class="settings-section">
      <p class="settings-section-title">Cuenta</p>
      <a href="usuario.html" class="settings-link-row">
        <span class="settings-row-icon">👤</span>
        <span>Personalizar perfil</span>
        <svg class="settings-link-row-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </a>
    </div>

    <div class="settings-footer">
      <button class="settings-logout-btn" id="sb-logout-btn">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Cerrar sesión
      </button>
    </div>
  </div>
</div>`;

  /* ── Init ─────────────────────────────────────────────────────────────── */
  function init() {
    document.body.classList.add('has-sidebar');
    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Avatar del usuario logueado
    const username = sessionStorage.getItem('username');
    if (username) {
      fetch('/profile/' + encodeURIComponent(username))
        .then(r => r.json())
        .then(d => {
          if (d.avatar_url) {
            const img = document.getElementById('sidebar-avatar-img');
            if (img) img.src = d.avatar_url + '?t=' + Date.now();
          }
          // Guardar is_adult si el servidor lo devuelve
          if (d.is_adult !== undefined) {
            sessionStorage.setItem('isAdult', d.is_adult);
          }
        })
        .catch(() => { });
    }

    // Configuración: abrir/cerrar modal
    document.getElementById('sb-settings').addEventListener('click', openSettings);
    document.getElementById('settings-modal-close').addEventListener('click', closeSettings);
    document.getElementById('settings-modal-overlay').addEventListener('click', e => {
      if (e.target.id === 'settings-modal-overlay') closeSettings();
    });

    // Dark mode
    const darkToggle = document.getElementById('toggle-dark-mode');
    const savedDark = localStorage.getItem('darkMode');
    const isDark = savedDark === null ? true : savedDark === 'true';
    darkToggle.checked = isDark;
    applyDark(isDark);
    darkToggle.addEventListener('change', () => {
      localStorage.setItem('darkMode', darkToggle.checked);
      applyDark(darkToggle.checked);
    });

    // NSFW mode
    const nsfwToggle = document.getElementById('toggle-nsfw');
    const savedNsfw = localStorage.getItem('nsfwMode') === 'true';
    nsfwToggle.checked = savedNsfw;
    applyNsfw(savedNsfw);
    nsfwToggle.addEventListener('change', () => {
      localStorage.setItem('nsfwMode', nsfwToggle.checked);
      applyNsfw(nsfwToggle.checked);
    });

    const isAdult = sessionStorage.getItem('isAdult') === 'true';

    if (!isAdult) {
      nsfwToggle.disabled = true;

      nsfwToggle.addEventListener('click', (e) => {
        e.preventDefault();

        mostrarMensaje(
          'Acceso restringido',
          'Debes tener al menos 18 años para activar contenido para adultos.'
        );
      });
    }


    // Botón crear publicación
    document.getElementById('sb-create').addEventListener('click', () => {
      if (!sessionStorage.getItem('username')) {
        window.location.href = 'login.html'; return;
      }
      if (typeof abrirModalPublicar === 'function') {
        abrirModalPublicar();
      } else {
        window.location.href = '/';
      }
    });

    // Explorar → scroll/focus en buscador
    document.getElementById('sb-explore').addEventListener('click', () => {
      const buscador = document.getElementById('busqueda');
      if (buscador) { buscador.focus(); buscador.scrollIntoView({ behavior: 'smooth' }); }
      else window.location.href = '/';
    });

    // Logout
    document.getElementById('sb-logout-btn').addEventListener('click', () => {
      sessionStorage.clear();
      window.location.href = 'login.html';
    });
  }

  function openSettings() { document.getElementById('settings-modal-overlay').classList.add('open'); }
  function closeSettings() { document.getElementById('settings-modal-overlay').classList.remove('open'); }
  function applyDark(v) { v ? document.documentElement.removeAttribute('data-theme') : document.documentElement.setAttribute('data-theme', 'light'); }
  function applyNsfw(v) { document.documentElement.classList.toggle('nsfw-enabled', v); }

  // Exponer para uso externo
  window.openSettingsModal = openSettings;
  window.closeSettingsModal = closeSettings;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
