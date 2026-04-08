let currentEmailId = null;

function extractEmailData() {
    const subjectEl = document.querySelector('h2[data-thread-perm-id]');
    const bodyEl = document.querySelector('.a3s.aiL'); 
    const senderEl = document.querySelector('.gD');
    
    if (!subjectEl || !bodyEl) return null;

    const subject = subjectEl.innerText || "";
    const body = bodyEl.innerText || "";
    const sender = senderEl ? (senderEl.getAttribute('email') || senderEl.innerText || "") : "";
    
    const linkEl = bodyEl.querySelector('a');
    const url = linkEl ? linkEl.href : "";
    const allLinks = bodyEl.querySelectorAll('a');
    const link_count = allLinks ? allLinks.length : 0;

    const threadId = subjectEl.getAttribute('data-thread-perm-id');

    return { subject, body, url, sender, link_count, threadId };
}

function injectUI() {
    if (document.getElementById('aegis-security-panel')) return;

    const panel = document.createElement('div');
    panel.id = 'aegis-security-panel';
    panel.innerHTML = `
        <div class="aegis-header">
            <div class="aegis-brand">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                <span>Aegis Security Gateway</span>
            </div>
            <button id="aegis-close">&times;</button>
        </div>
        <div class="aegis-content" id="aegis-content">
            <div class="aegis-status-bar">
                <div class="radar-spinner"></div>
                <span>Intercepting Payload...</span>
            </div>
        </div>
    `;
    
    document.body.appendChild(panel);
    
    document.getElementById('aegis-close').addEventListener('click', () => {
        panel.style.display = 'none';
        currentEmailId = null; 
    });
}

function updateUI(data) {
    const content = document.getElementById('aegis-content');
    if (!content) return;
    
    const colorMap = {
        'green': '#10b981',
        'orange': '#f59e0b',
        'red': '#ef4444'
    };
    const c = colorMap[data.color] || '#3b82f6';

    let listHtml = '';
    data.reasons.forEach((r, idx) => {
        listHtml += `<li style="animation-delay: ${idx * 0.1}s"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg> ${r}</li>`;
    });

    // Gradients for progress bars
    const gradientMap = {
        'green': 'linear-gradient(90deg, #10b981, #34d399)',
        'orange': 'linear-gradient(90deg, #f59e0b, #fbbf24)',
        'red': 'linear-gradient(90deg, #ef4444, #f87171)'
    };
    const bgGrade = gradientMap[data.color] || c;

    content.innerHTML = `
        <div class="aegis-metric-row">
            <div class="aegis-metric" style="border-left: 3px solid ${c}; box-shadow: -4px 0 15px ${c}33;">
                <span class="label">Classification</span>
                <span class="val" style="color:${c}; text-transform:uppercase; letter-spacing:1px;">${data.class}</span>
            </div>
            <div class="aegis-metric">
                <span class="label">Recommended Action</span>
                <span class="val">${data.action}</span>
            </div>
        </div>
        
        <div class="aegis-risk-box">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span>Threat Level: <span style="font-weight:bold; color:${c}">${data.risk}</span></span>
                <span style="font-family: monospace; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;">Conf: ${data.confidence}%</span>
            </div>
            <div class="aegis-progress-track">
                <div class="aegis-progress-bar" style="width: ${data.risk_score}%; background: ${bgGrade}; box-shadow: 0 0 10px ${c};"></div>
            </div>
        </div>

        <div class="aegis-reasons">
            <span class="label"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> Threat Diagnostics</span>
            <ul id="aegis-reasons-list">
                ${listHtml}
            </ul>
        </div>
    `;
}

function analyzeCurrentEmail() {
    const payload = extractEmailData();
    
    if (payload && payload.threadId !== currentEmailId) {
        currentEmailId = payload.threadId;
        
        const panel = document.getElementById('aegis-security-panel');
        if (panel) panel.style.display = 'flex';
        else injectUI();
        
        // Reset to loading state
        document.getElementById('aegis-content').innerHTML = `
            <div class="aegis-status-bar">
                <div class="radar-spinner"></div>
                <span>Intercepting Payload...</span>
            </div>
        `;

        let responded = false;

        const handleResponse = (response) => {
            if (responded) return;
            responded = true;
            
            if (response && response.success) {
                try {
                    updateUI(response.data);
                } catch (err) {
                    document.getElementById('aegis-content').innerHTML = `
                        <div style="color:#ef4444; font-size:12px; padding:10px; text-align:center;">
                            ⚠️ UI Render Error: ${err.message}
                        </div>`;
                }
            } else {
                let errMSG = response ? (response.error || "Unknown Error") : (chrome.runtime.lastError ? chrome.runtime.lastError.message : "No response from background");
                document.getElementById('aegis-content').innerHTML = `
                    <div style="color:#ef4444; font-size:12px; padding:10px; text-align:center;">
                        ⚠️ Gateway Error: ${errMSG}<br><br>Make sure the local Python Backend API is running!
                    </div>`;
                console.error("Aegis Error:", errMSG);
            }
        };

        try {
            chrome.runtime.sendMessage({ action: "analyzePayload", payload: payload }, handleResponse);
            
            setTimeout(() => {
                if (!responded) {
                    handleResponse({ success: false, error: "Request timed out after 5 seconds" });
                }
            }, 5000);
        } catch (e) {
            handleResponse({ success: false, error: e.toString() + " (Try refreshing Gmail!)" });
        }
    }
}

// Observe Gmail DOM dynamically
const observer = new MutationObserver(() => {
    if (window.location.hash.includes('#inbox/') || window.location.hash.includes('#spam/')) {
        setTimeout(analyzeCurrentEmail, 800); 
    } else {
        const panel = document.getElementById('aegis-security-panel');
        if (panel) panel.style.display = 'none';
        currentEmailId = null;
    }
});

observer.observe(document.body, { childList: true, subtree: true });
