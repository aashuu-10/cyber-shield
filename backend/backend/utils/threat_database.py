import re
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
            'money': r'(\$[\d,]+|bitcoin|crypto|wire transfer|western union|gift card)',
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
