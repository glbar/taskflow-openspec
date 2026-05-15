const API_BASE = '/api';

function getToken() { return localStorage.getItem('token'); }
function setToken(t) { localStorage.setItem('token', t); }
function removeToken() { localStorage.removeItem('token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } }
function setUser(u) { localStorage.setItem('user', JSON.stringify(u)); }

function requireAuth() {
    if (!getToken()) { window.location.href = '/login.html'; return false; }
    return true;
}

function requireTeam() {
    if (!requireAuth()) return false;
    const u = getUser();
    if (!u || u.team_id == null) { window.location.href = '/team.html'; return false; }
    return true;
}

async function apiFetch(path, options = {}) {
    const token = getToken();
    const res = await fetch(API_BASE + path, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...(options.headers || {}),
        },
    });

    if (res.status === 401) {
        removeToken();
        localStorage.removeItem('user');
        window.location.href = '/login.html';
        throw new Error('Unauthorized');
    }

    const data = res.status === 204 ? {} : await res.json().catch(() => ({}));
    if (!res.ok) throw { status: res.status, error: data.error || { code: 'UNKNOWN', message: '오류가 발생했습니다' } };
    return data;
}

function showToast(message, type = 'error') {
    document.getElementById('toast')?.remove();
    const el = document.createElement('div');
    el.id = 'toast';
    const color = type === 'success' ? 'bg-green-500' : type === 'info' ? 'bg-blue-500' : 'bg-red-500';
    el.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded text-white text-sm shadow-lg ${color}`;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

function showError(err) {
    showToast(err?.error?.message || err?.message || '오류가 발생했습니다', 'error');
}

function logout() {
    apiFetch('/auth/logout', { method: 'POST' }).catch(() => {});
    removeToken();
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}
