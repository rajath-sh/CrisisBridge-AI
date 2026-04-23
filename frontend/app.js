/**
 * CrisisBridge AI — Frontend Logic
 * ================================
 * Handles API calls, view switching, and dynamic UI updates.
 */

const API_BASE = '/api/v1';
let authToken = localStorage.getItem('token');
let currentUser = null;
let lastQueryLogId = null;

// ── Initialization ──────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();

    // Check if logged in
    if (authToken) {
        initApp();
    } else {
        showView('login');
    }

    // Event Listeners
    document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    document.getElementById('chat-form')?.addEventListener('submit', handleChat);
    document.getElementById('safety-form')?.addEventListener('submit', handleSafetyCheck);
});

async function initApp() {
    try {
        const resp = await apiCall('/auth/me');
        currentUser = resp;
        document.getElementById('user-display-name').textContent = currentUser.full_name || currentUser.username;
        document.getElementById('main-nav').style.display = 'flex';
        showView('dashboard');
        refreshDashboard();
    } catch (e) {
        console.error("Session expired", e);
        logout();
    }
}

// ── Navigation ──────────────────────────────────

function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.style.display = 'none');
    const target = document.getElementById(`view-${viewId}`);
    if (target) {
        target.style.display = 'block';
    }
    
    if (viewId === 'dashboard') refreshDashboard();
    lucide.createIcons();
}

function logout() {
    localStorage.removeItem('token');
    authToken = null;
    currentUser = null;
    document.getElementById('main-nav').style.display = 'none';
    showView('login');
}

// ── Authentication ──────────────────────────────

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const resp = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!resp.ok) throw new Error("Invalid credentials");

        const data = await resp.json();
        authToken = data.access_token;
        localStorage.setItem('token', authToken);
        initApp();
    } catch (err) {
        alert(err.message);
    }
}

// ── Dashboard & Incidents ───────────────────────

async function refreshDashboard() {
    try {
        const data = await apiCall('/incidents');
        const list = document.getElementById('incidents-list');
        list.innerHTML = '';

        if (data.incidents.length === 0) {
            list.innerHTML = '<div class="card"><p class="text-muted">No active incidents reported.</p></div>';
        }

        data.incidents.forEach(inc => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.borderLeft = `4px solid ${getSeverityColor(inc.severity)}`;
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="color: ${getSeverityColor(inc.severity)}">${inc.incident_type.toUpperCase()} - ${inc.severity.toUpperCase()}</h4>
                        <p style="font-weight: 600; margin: 0.25rem 0;">${inc.title}</p>
                        <p class="text-muted" style="font-size: 0.875rem;">${inc.description || 'No description'}</p>
                        <div style="margin-top: 0.75rem; font-size: 0.75rem; display: flex; gap: 1rem;">
                            <span><i data-lucide="map-pin" style="width: 12px;"></i> Floor ${inc.floor}, Room ${inc.room}</span>
                            <span><i data-lucide="clock" style="width: 12px;"></i> ${new Date(inc.reported_at).toLocaleTimeString()}</span>
                        </div>
                    </div>
                    <span class="badge" style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">
                        ${inc.status}
                    </span>
                </div>
            `;
            list.appendChild(card);
        });

        document.getElementById('stat-active').textContent = data.active_count;
        lucide.createIcons();
    } catch (e) {
        console.error("Failed to load incidents", e);
    }
}

async function reportPanic() {
    if (!confirm("This will trigger a CRITICAL emergency alert. Continue?")) return;
    
    try {
        await apiCall('/incidents/report', 'POST', {
            incident_type: 'security',
            severity: 'critical',
            title: 'PANIC BUTTON TRIGGERED',
            description: 'User initiated emergency panic alert from dashboard.',
            floor: currentUser?.current_floor || 1,
            room: currentUser?.current_room || 'Lobby',
            zone: currentUser?.current_zone || 'Main'
        });
        refreshDashboard();
        alert("🚨 Emergency reported! Help is on the way.");
    } catch (e) {
        alert("Failed to report emergency. Please try again.");
    }
}

// ── AI Assistant ────────────────────────────────

async function handleChat(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const query = input.value;
    input.value = '';

    addChatMessage('user', query);

    try {
        const resp = await apiCall('/query', 'POST', { query });
        addChatMessage('ai', resp.answer, resp.cache_status === 'hit', resp.sources);
        lastQueryLogId = resp.query_log_id;
        
        // Show feedback form after AI responds
        setTimeout(() => {
            document.getElementById('feedback-overlay').style.display = 'flex';
        }, 1000);
        
    } catch (e) {
        addChatMessage('ai', 'Sorry, I encountered an error. Please try again.');
    }
}

function addChatMessage(role, text, isCached = false, sources = []) {
    const container = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    
    const isAi = role === 'ai';
    msg.style.cssText = `
        padding: 1rem;
        border-radius: 0.5rem;
        max-width: 85%;
        ${isAi ? 'background: var(--surface-dark); align-self: flex-start;' : 'background: var(--primary); align-self: flex-end;'}
    `;

    let html = `<div>${text}</div>`;
    
    if (isAi) {
        if (isCached) {
            html += `<div style="font-size: 0.7rem; color: var(--success); margin-top: 0.5rem;"><i data-lucide="zap" style="width: 10px;"></i> Cached Response</div>`;
        }
        if (sources && sources.length > 0) {
            html += `<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.75rem; border-top: 1px solid var(--border); padding-top: 0.5rem;">
                Sources: ${sources.join(', ')}
            </div>`;
        }
    }

    msg.innerHTML = html;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
    lucide.createIcons();
}

// ── Safety Check ────────────────────────────────

async function handleSafetyCheck(e) {
    e.preventDefault();
    const floor = parseInt(document.getElementById('safety-floor').value);
    const zone = document.getElementById('safety-zone').value;

    try {
        const resp = await apiCall('/safety/check', 'POST', { floor, zone });
        const resultDiv = document.getElementById('safety-result');
        resultDiv.style.display = 'block';
        
        const color = getStatusColor(resp.safety_level);
        
        resultDiv.innerHTML = `
            <div class="card" style="border: 2px solid ${color}">
                <h3 style="color: ${color}">
                    ${resp.message}
                </h3>
                <p style="margin: 1rem 0;">${resp.recommended_action}</p>
                ${resp.nearby_incidents.length > 0 ? `
                    <div style="font-size: 0.875rem;">
                        <strong>Nearby:</strong> ${resp.nearby_incidents.map(i => i.title).join(', ')}
                    </div>
                ` : ''}
            </div>
        `;
    } catch (e) {
        alert("Safety check failed.");
    }
}

// ── Feedback ────────────────────────────────────

async function submitFeedback(rating) {
    const comment = document.getElementById('feedback-comment').value;
    try {
        await apiCall('/feedback', 'POST', {
            target_type: 'ai_response',
            rating: rating,
            comment: comment,
            query_log_id: lastQueryLogId
        });
        closeFeedback();
    } catch (e) {
        console.error("Feedback failed", e);
        closeFeedback();
    }
}

function closeFeedback() {
    document.getElementById('feedback-overlay').style.display = 'none';
    document.getElementById('feedback-comment').value = '';
}

// ── Utils ───────────────────────────────────────

async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        }
    };
    if (body) options.body = JSON.stringify(body);

    const resp = await fetch(`${API_BASE}${endpoint}`, options);
    if (!resp.ok) {
        if (resp.status === 401) logout();
        throw new Error(`API Error: ${resp.status}`);
    }
    return await resp.json();
}

function getSeverityColor(sev) {
    switch (sev) {
        case 'critical': return '#ef4444';
        case 'high': return '#f59e0b';
        case 'medium': return '#3b82f6';
        default: return '#94a3b8';
    }
}
function getStatusColor(level) {
    switch (level) {
        case 'safe': return '#10b981';
        case 'warning': return '#f59e0b';
        case 'evacuate': return '#ef4444';
        default: return '#94a3b8';
    }
}
