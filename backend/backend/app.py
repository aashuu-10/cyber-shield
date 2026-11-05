from flask import Flask, render_template, request, jsonify
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
    print("\n==========================================\n      CYBER SHIELD ACTIVE\n==========================================\nRunning on http://localhost:5000\n")
    screenshot_detector.start_monitoring()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
