
function quickScan() {
    const url = document.getElementById('quickUrl').value;
    if (!url) return alert('Enter a URL');
    fetch('/api/scan-link', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url})
    })
    .then(r => r.json())
    .then(data => {
        const div = document.getElementById('quickResults');
        div.classList.remove('hidden');
        div.innerHTML = `<h3>Result: ${data.risk_level}</h3><p>Risk Score: ${data.risk_score}/100</p><p>${data.warnings.join('<br>')}</p>`;
    });
}

function quickTextScan() {
    const text = document.getElementById('quickText').value;
    if (!text) return alert('Enter text');
    fetch('/api/scan-text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: text})
    })
    .then(r => r.json())
    .then(data => {
        const div = document.getElementById('quickResults');
        div.classList.remove('hidden');
        div.innerHTML = `<h3>Result: ${data.overall_safe ? 'SAFE' : 'SCAM DETECTED'}</h3>`;
    });
}

function speakPrec() {
    fetch('/api/precautions/speak', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({type: 'general'})});
}
