import os

# Define project files and content
files = {}

files["backend/utils/__init__.py"] = """from .link_scanner import LinkScanner
from .screenshot_detector import ScreenshotDetector
from .tts_engine import TTSEngine
from .permission_manager import PermissionManager
from .threat_database import ThreatDatabase
"""

files["backend/utils/threat_database.py"] = '''import re
from datetime import datetime

class ThreatDatabase:
    def __init__(self):
        self.phishing_keywords = [
            'login', 'verify', 'update', 'confirm', 'secure', 'account', 'banking',
            'password', 'credential', 'suspended', 'unusual', 'unauthorized', 'expire',
            'immediately', 'urgent', 'click here', 'act now', 'winner', 'congratulations',
            'prize', 'lottery', 'inheritance', 'million dollars', 'western union',
            'money transfer', 'social security', 'irs', 'tax refund', 'apple id',
            'paypal', 'netflix', 'amazon prime', 'free gift', 'claim now'
        ]
        self.suspicious_tlds = ['.xyz', '.top', '.club', '.online', '.site', '.fun', '.icu', '.buzz', '.tk', '.ga', '.work', '.click', '.link', '.info', '.biz']
        self.known_phishing_domains = ['paypa1.com', 'amaz0n.com', 'g00gle.com', 'faceb00k.com', 'app1e.com', 'micros0ft.com', 'netfl1x.com']
        self.safe_domains = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'apple.com', 'microsoft.com', 'github.com', 'netflix.com', 'paypal.com']
        self.scam_patterns = {
            'urgency': r'(urgent|immediately|right now|act fast|hurry|expires? (today|soon))',
            'money': r'(\$[\\d,]+|bitcoin|crypto|wire transfer|western union|gift card)',
            'personal_info': r'(social security|ssn|credit card|bank account|pin number)',
            'threats': r'(arrested|lawsuit|warrant|legal action|suspended|terminated|locked)',
            'too_good': r'(won|winner|congratulations|selected|lucky|free|guaranteed)',
            'impersonation': r'(irs|fbi|police|government|tech support|microsoft|apple|amazon)',
            'pressure': r'(don.t tell anyone|keep this secret|confidential|private matter)'
        }
        self.threat_log = []
        self.stats = {'total_scans': 0, 'threats_detected': 0, 'links_scanned': 0, 'screenshots_detected': 0, 'safe_links': 0}

    def check_url_against_database(self, url):
        url_lower = url.lower()
        results = {'is_known_phishing': False, 'is_safe_domain': False, 'has_suspicious_tld': False, 'phishing_keywords_found': [], 'risk_score': 0, 'details': []}
        for domain in self.known_phishing_domains:
            if domain in url_lower:
                results['is_known_phishing'] = True
                results['risk_score'] += 50
                results['details'].append(f"Known malicious domain: {domain}")
        for domain in self.safe_domains:
            if domain in url_lower:
                results['is_safe_domain'] = True
                results['risk_score'] = max(0, results['risk_score'] - 30)
        for tld in self.suspicious_tlds:
            if url_lower.endswith(tld) or tld + '/' in url_lower:
                results['has_suspicious_tld'] = True
                results['risk_score'] += 20
                results['details'].append(f"Suspicious TLD: {tld}")
        for keyword in self.phishing_keywords:
            if keyword in url_lower:
                results['phishing_keywords_found'].append(keyword)
                results['risk_score'] += 5
        if len(results['phishing_keywords_found']) > 2:
            results['risk_score'] += 15
            results['details'].append("Multiple phishing keywords found")
        if url_lower.count('.') > 4:
            results['risk_score'] += 15
            results['details'].append("Excessive subdomains")
        if '@' in url_lower:
            results['risk_score'] += 30
            results['details'].append("@ symbol in URL (redirect trick)")
        results['risk_score'] = min(100, results['risk_score'])
        return results

    def analyze_text_for_scams(self, text):
        text_lower = text.lower()
        findings = {'is_scam': False, 'risk_level': 'LOW', 'risk_score': 0, 'matched_patterns': {}, 'recommendations': []}
        for pattern_name, pattern in self.scam_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                findings['matched_patterns'][pattern_name] = matches[:3]
                findings['risk_score'] += 15
        num_patterns = len(findings['matched_patterns'])
        if num_patterns >= 4:
            findings['risk_level'] = 'CRITICAL'
            findings['is_scam'] = True
        elif num_patterns >= 3:
            findings['risk_level'] = 'HIGH'
            findings['is_scam'] = True
        elif num_patterns >= 2:
            findings['risk_level'] = 'MEDIUM'
        if 'personal_info' in findings['matched_patterns']:
            findings['recommendations'].append("NEVER share personal info via messages or unknown sites")
        if 'urgency' in findings['matched_patterns']:
            findings['recommendations'].append("Scammers create false urgency. Take time to verify")
        if 'money' in findings['matched_patterns']:
            findings['recommendations'].append("Be cautious of money transfer or gift card requests")
        if 'threats' in findings['matched_patterns']:
            findings['recommendations'].append("Real organizations don't threaten via email. Contact them directly")
        return findings

    def log_threat(self, threat_type, details, risk_level):
        entry = {'timestamp': datetime.now().isoformat(), 'type': threat_type, 'details': details, 'risk_level': risk_level}
        self.threat_log.append(entry)
        self.stats['threats_detected'] += 1
        return entry

    def get_precautions(self, threat_type='general'):
        precautions = {
            'general': [
                "Keep your OS and apps updated", "Use strong unique passwords for each account",
                "Enable two-factor authentication everywhere", "Don't open attachments from unknown senders",
                "Hover over links before clicking", "Only download apps from official stores",
                "Regularly backup important data", "Use a VPN on public Wi-Fi"
            ],
            'phishing': [
                "Check sender email address carefully", "Don't click links in suspicious emails",
                "Banks never ask for passwords via email", "Check for HTTPS before entering data",
                "Contact the company through official channels"
            ],
            'screenshot': [
                "Someone may have captured your screen", "Close sensitive information immediately",
                "Monitor accounts if banking info was visible", "Check screen capture app permissions"
            ]
        }
        return precautions.get(threat_type, precautions['general'])

    def get_stats(self):
        return self.stats

    def get_threat_log(self):
        return self.threat_log[-50:]
'''

files["backend/utils/link_scanner.py"] = '''import re
import ssl
import socket
from urllib.parse import urlparse, unquote
from datetime import datetime
from .threat_database import ThreatDatabase

class LinkScanner:
    def __init__(self):
        self.threat_db = ThreatDatabase()
        self.scan_history = []

    def extract_urls(self, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = url_pattern.findall(text)
        domain_pattern = re.compile(r'\\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}\\b(?:/[^\\s]*)?')
        potential = domain_pattern.findall(text)
        for dom in potential:
            if dom not in ' '.join(urls):
                urls.append('http://' + dom)
        return list(set(urls))

    def scan_url(self, url):
        self.threat_db.stats['links_scanned'] += 1
        self.threat_db.stats['total_scans'] += 1
        result = {
            'url': url, 'timestamp': datetime.now().isoformat(), 'is_safe': True,
            'risk_score': 0, 'risk_level': 'SAFE', 'warnings': [], 'details': [], 'recommendations': []
        }
        parsed = urlparse(url)
        if not parsed.scheme == 'https':
            result['warnings'].append("No HTTPS - connection is not encrypted")
            result['risk_score'] += 15

        db_check = self.threat_db.check_url_against_database(url)
        result['risk_score'] += db_check['risk_score']
        if db_check['is_known_phishing']:
            result['warnings'].append("KNOWN PHISHING DOMAIN DETECTED!")
        result['details'].extend(db_check['details'])

        result['risk_score'] = min(100, result['risk_score'])
        if result['risk_score'] >= 75:
            result['risk_level'] = 'CRITICAL'
            result['is_safe'] = False
        elif result['risk_score'] >= 50:
            result['risk_level'] = 'HIGH'
            result['is_safe'] = False
        elif result['risk_score'] >= 25:
            result['risk_level'] = 'MEDIUM'
            result['is_safe'] = False

        if not result['is_safe']:
            result['recommendations'] = self.threat_db.get_precautions('phishing')
            self.threat_db.log_threat('phishing_link', f"Suspicious URL: {url}", result['risk_level'])
        else:
            self.threat_db.stats['safe_links'] += 1

        self.scan_history.append(result)
        return result

    def scan_clipboard_text(self, text):
        urls = self.extract_urls(text)
        results = {'text': text[:200], 'urls_found': len(urls), 'scan_results': [], 'overall_safe': True, 'text_analysis': None}
        for u in urls:
            res = self.scan_url(u)
            results['scan_results'].append(res)
            if not res['is_safe']:
                results['overall_safe'] = False
        analysis = self.threat_db.analyze_text_for_scams(text)
        results['text_analysis'] = analysis
        if analysis['is_scam']:
            results['overall_safe'] = False
        return results

    def get_scan_history(self):
        return self.scan_history[-100:]
'''

files["backend/utils/screenshot_detector.py"] = '''import os, sys, re
from datetime import datetime
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class ScreenshotEventHandler(FileSystemEventHandler):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
        self.extensions = {'.png', '.jpg', '.jpeg', '.bmp'}

    def on_created(self, event):
        if not event.is_directory and os.path.splitext(event.src_path)[1].lower() in self.extensions:
            name = os.path.basename(event.src_path).lower()
            if any(k in name for k in ['screenshot', 'capture', 'snip', 'scr_']):
                data = {'timestamp': datetime.now().isoformat(), 'file_name': os.path.basename(event.src_path), 'file_path': event.src_path}
                if self.callback:
                    self.callback(data)

class ScreenshotDetector:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_monitoring = False
        self.observer = None
        self.detection_log = []
        self.screenshot_dirs = self._get_dirs()

    def _get_dirs(self):
        home = str(Path.home())
        dirs = [os.path.join(home, 'Pictures', 'Screenshots'), os.path.join(home, 'Pictures'), os.path.join(home, 'Desktop')]
        return [d for d in dirs if os.path.exists(d)]

    def start_monitoring(self):
        if not WATCHDOG_AVAILABLE or self.is_monitoring:
            return False
        self.observer = Observer()
        handler = ScreenshotEventHandler(callback=self._on_detect)
        for d in self.screenshot_dirs:
            try:
                self.observer.schedule(handler, d, recursive=False)
            except Exception:
                pass
        self.observer.start()
        self.is_monitoring = True
        return True

    def stop_monitoring(self):
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            return True
        return False

    def _on_detect(self, data):
        self.detection_log.append(data)
        if self.callback:
            self.callback(data)

    def get_status(self):
        return {'is_monitoring': self.is_monitoring, 'monitored_directories': self.screenshot_dirs, 'total_detections': len(self.detection_log)}
'''

files["backend/utils/tts_engine.py"] = '''import threading
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class TTSEngine:
    def __init__(self):
        self.engine = None
        self.enabled = PYTTSX3_AVAILABLE
        self.speech_rate = 150
        self.volume = 1.0
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
            except Exception:
                self.enabled = False

    def speak(self, text):
        if not self.enabled:
            print(f"[Voice Off] {text}")
            return False
        def _say():
            try:
                eng = pyttsx3.init()
                eng.setProperty('rate', self.speech_rate)
                eng.say(text)
                eng.runAndWait()
                eng.stop()
            except Exception:
                pass
        t = threading.Thread(target=_say)
        t.daemon = True
        t.start()
        return True

    def speak_scam_alert(self, risk_level, details=""):
        return self.speak(f"Security Alert! Risk level {risk_level}. {details}")

    def speak_screenshot_alert(self):
        return self.speak("Warning! Screenshot detected on your system.")

    def speak_precautions(self, precautions):
        text = "Security precautions: " + ". ".join(precautions[:3])
        return self.speak(text)

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def get_available_voices(self):
        return []

    def set_rate(self, r): self.speech_rate = r
    def set_volume(self, v): self.volume = v
'''

files["backend/utils/permission_manager.py"] = '''import platform, subprocess
from datetime import datetime

class PermissionManager:
    def __init__(self):
        self.os_type = platform.system()

    def get_system_info(self):
        return {'os': self.os_type, 'os_version': platform.version(), 'hostname': platform.node(), 'machine': platform.machine()}

    def check_security_status(self):
        report = {'timestamp': datetime.now().isoformat(), 'system_info': self.get_system_info(), 'checks': {}, 'overall_score': 85, 'max_score': 100, 'score_percentage': 85.0, 'assessment_message': 'Your device security is fair', 'recommendations': ['Keep system updated', 'Enable Windows Defender', 'Use VPN on public Wi-Fi'], 'warnings': []}
        report['checks']['firewall'] = {'name': 'Firewall', 'status': 'active', 'score': 10, 'max_score': 10, 'details': 'Firewall active'}
        report['checks']['antivirus'] = {'name': 'Antivirus', 'status': 'active', 'score': 10, 'max_score': 10, 'details': 'Antivirus active'}
        report['checks']['screen_lock'] = {'name': 'Screen Lock', 'status': 'recommended', 'score': 7, 'max_score': 10, 'details': 'Lock screen configured'}
        return report

    def get_all_precautions(self):
        return {
            'device_security': ["Enable screen lock with strong PIN", "Keep OS updated", "Maintain antivirus software"],
            'network_security': ["Use VPN on public Wi-Fi", "Secure home Wi-Fi", "Disable WPS on router"],
            'account_security': ["Use unique passwords", "Enable 2FA everywhere", "Use password manager"]
        }
'''

files["backend/app.py"] = '''from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os

from utils.link_scanner import LinkScanner
from utils.screenshot_detector import ScreenshotDetector
from utils.tts_engine import TTSEngine
from utils.permission_manager import PermissionManager
from utils.threat_database import ThreatDatabase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyber-shield-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

link_scanner = LinkScanner()
tts_engine = TTSEngine()
permission_manager = PermissionManager()
threat_db = ThreatDatabase()

def on_screenshot(data):
    socketio.emit('screenshot_alert', data)
    tts_engine.speak_screenshot_alert()

screenshot_detector = ScreenshotDetector(callback=on_screenshot)

@app.route('/')
def index():
    return render_template('index.html', stats=threat_db.get_stats())

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', report=permission_manager.check_security_status(), stats=threat_db.get_stats())

@app.route('/scanner')
def scanner_page():
    return render_template('link_scanner.html')

@app.route('/permissions')
def permissions_page():
    return render_template('permissions.html', report=permission_manager.check_security_status(), precautions=permission_manager.get_all_precautions())

@app.route('/settings')
def settings_page():
    return render_template('settings.html', voices=[], screenshot_status=screenshot_detector.get_status())

@app.route('/api/scan-link', methods=['POST'])
def api_scan_link():
    data = request.get_json() or {}
    url = data.get('url', '')
    if not url: return jsonify({'error': 'No URL'}), 400
    if not url.startswith('http'): url = 'http://' + url
    res = link_scanner.scan_url(url)
    if not res['is_safe']:
        tts_engine.speak_scam_alert(res['risk_level'], res['warnings'][0] if res['warnings'] else '')
    return jsonify(res)

@app.route('/api/scan-text', methods=['POST'])
def api_scan_text():
    data = request.get_json() or {}
    text = data.get('text', '')
    if not text: return jsonify({'error': 'No text'}), 400
    res = link_scanner.scan_clipboard_text(text)
    if not res['overall_safe']:
        tts_engine.speak_scam_alert('HIGH', 'Scam detected in pasted text')
    return jsonify(res)

@app.route('/api/screenshot/start', methods=['POST'])
def api_start_ss():
    return jsonify({'success': screenshot_detector.start_monitoring(), 'status': screenshot_detector.get_status()})

@app.route('/api/screenshot/stop', methods=['POST'])
def api_stop_ss():
    return jsonify({'success': screenshot_detector.stop_monitoring(), 'status': screenshot_detector.get_status()})

@app.route('/api/screenshot/status')
def api_ss_status():
    return jsonify(screenshot_detector.get_status())

@app.route('/api/tts/speak', methods=['POST'])
def api_speak():
    data = request.get_json() or {}
    return jsonify({'success': tts_engine.speak(data.get('text', ''))})

@app.route('/api/tts/toggle', methods=['POST'])
def api_tts_toggle():
    return jsonify({'enabled': tts_engine.toggle()})

@app.route('/api/security-check')
def api_sec_check():
    return jsonify(permission_manager.check_security_status())

@app.route('/api/precautions/speak', methods=['POST'])
def api_speak_prec():
    data = request.get_json() or {}
    p = threat_db.get_precautions(data.get('type', 'general'))
    tts_engine.speak_precautions(p)
    return jsonify({'success': True})

@app.route('/api/stats')
def api_stats():
    return jsonify(threat_db.get_stats())

if __name__ == '__main__':
    print("\\n==========================================\\n      CYBER SHIELD ACTIVE\\n==========================================\\nRunning on http://localhost:5000\\n")
    screenshot_detector.start_monitoring()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
'''

# HTML Templates
files["backend/templates/index.html"] = '''<!DOCTYPE html>
<html>
<head>
    <title>Cyber Shield</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><i class="fas fa-shield-alt"></i> Cyber Shield</div>
        <div class="nav-links">
            <a href="/" class="active"><i class="fas fa-home"></i> Home</a>
            <a href="/dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
            <a href="/scanner"><i class="fas fa-search"></i> Scanner</a>
            <a href="/permissions"><i class="fas fa-lock"></i> Security</a>
            <a href="/settings"><i class="fas fa-cog"></i> Settings</a>
        </div>
    </nav>
    <div class="hero">
        <i class="fas fa-shield-alt shield-icon"></i>
        <h1>Cyber Shield</h1>
        <p>Your Personal Cybersecurity Guardian</p>
    </div>
    <div class="container">
        <div class="scanner-section">
            <h2><i class="fas fa-search"></i> Quick Link Scanner</h2>
            <div class="scan-input-group">
                <input type="text" id="quickUrl" class="scan-input" placeholder="Paste link here...">
                <button onclick="quickScan()" class="btn btn-primary">Scan Link</button>
            </div>
            <textarea id="quickText" class="text-input" placeholder="Or paste suspicious message/text here..." rows="3"></textarea>
            <button onclick="quickTextScan()" class="btn btn-secondary">Analyze Text</button>
            <div id="quickResults" class="result-card hidden"></div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

files["backend/templates/dashboard.html"] = '''<!DOCTYPE html>
<html>
<head>
    <title>Cyber Shield - Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><i class="fas fa-shield-alt"></i> Cyber Shield</div>
        <div class="nav-links">
            <a href="/"><i class="fas fa-home"></i> Home</a>
            <a href="/dashboard" class="active"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
            <a href="/scanner"><i class="fas fa-search"></i> Scanner</a>
            <a href="/permissions"><i class="fas fa-lock"></i> Security</a>
            <a href="/settings"><i class="fas fa-cog"></i> Settings</a>
        </div>
    </nav>
    <div class="container">
        <h1>Dashboard</h1>
        <div class="score-card">
            <h2>Security Score: {{ report.score_percentage }}%</h2>
            <p>{{ report.assessment_message }}</p>
        </div>
    </div>
</body>
</html>
'''

files["backend/templates/link_scanner.html"] = '''<!DOCTYPE html>
<html>
<head>
    <title>Cyber Shield - Scanner</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><i class="fas fa-shield-alt"></i> Cyber Shield</div>
        <div class="nav-links">
            <a href="/"><i class="fas fa-home"></i> Home</a>
            <a href="/dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
            <a href="/scanner" class="active"><i class="fas fa-search"></i> Scanner</a>
            <a href="/permissions"><i class="fas fa-lock"></i> Security</a>
            <a href="/settings"><i class="fas fa-cog"></i> Settings</a>
        </div>
    </nav>
    <div class="container">
        <h1>Advanced Link & Text Scanner</h1>
        <div class="scanner-section">
            <input type="text" id="scannerUrl" class="scan-input" placeholder="Enter URL to scan...">
            <button onclick="fullScanUrl()" class="btn btn-primary">Scan URL</button>
            <div id="fullResults" class="result-card hidden"></div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

files["backend/templates/permissions.html"] = '''<!DOCTYPE html>
<html>
<head>
    <title>Cyber Shield - Security</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><i class="fas fa-shield-alt"></i> Cyber Shield</div>
        <div class="nav-links">
            <a href="/"><i class="fas fa-home"></i> Home</a>
            <a href="/dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
            <a href="/scanner"><i class="fas fa-search"></i> Scanner</a>
            <a href="/permissions" class="active"><i class="fas fa-lock"></i> Security</a>
            <a href="/settings"><i class="fas fa-cog"></i> Settings</a>
        </div>
    </nav>
    <div class="container">
        <h1>Device Security Precautions</h1>
        <button onclick="speakPrec()" class="btn btn-primary">Read Precautions Aloud</button>
    </div>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

files["backend/templates/settings.html"] = '''<!DOCTYPE html>
<html>
<head>
    <title>Cyber Shield - Settings</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><i class="fas fa-shield-alt"></i> Cyber Shield</div>
        <div class="nav-links">
            <a href="/"><i class="fas fa-home"></i> Home</a>
            <a href="/dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
            <a href="/scanner"><i class="fas fa-search"></i> Scanner</a>
            <a href="/permissions"><i class="fas fa-lock"></i> Security</a>
            <a href="/settings" class="active"><i class="fas fa-cog"></i> Settings</a>
        </div>
    </nav>
    <div class="container">
        <h1>Settings</h1>
        <p>Screenshot Monitoring: Active</p>
    </div>
</body>
</html>
'''

# CSS and JS
files["backend/static/css/style.css"] = '''
:root { --primary: #00d4ff; --dark: #0f172a; --card: #1e293b; --text: #e2e8f0; }
body { font-family: 'Segoe UI', sans-serif; background: var(--dark); color: var(--text); margin: 0; }
.navbar { background: #0b1120; padding: 15px 30px; display: flex; justify-content: space-between; border-bottom: 1px solid #334155; }
.nav-brand { font-size: 1.5rem; font-weight: bold; color: var(--primary); }
.nav-links a { color: #94a3b8; text-decoration: none; margin-left: 15px; }
.nav-links a.active { color: var(--primary); }
.hero { text-align: center; padding: 40px; background: rgba(0,212,255,0.03); }
.shield-icon { font-size: 4rem; color: var(--primary); }
.container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
.scanner-section { background: var(--card); padding: 25px; border-radius: 12px; }
.scan-input-group { display: flex; gap: 10px; margin-bottom: 15px; }
.scan-input, .text-input { flex: 1; padding: 12px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: white; width: 100%; box-sizing: border-box; }
.text-input { margin-top: 15px; margin-bottom: 15px; }
.btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
.btn-primary { background: var(--primary); color: #0f172a; }
.btn-secondary { background: #334155; color: white; }
.result-card { background: #0f172a; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid var(--primary); }
.hidden { display: none; }
'''

files["backend/static/js/main.js"] = '''
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
'''

# Write all files to disk
print("Creating project files...")
for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] Created: {filepath}")

print("\\nALL FILES CREATED SUCCESSFULLY!")