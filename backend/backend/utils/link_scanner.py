import re
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
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = url_pattern.findall(text)
        domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b(?:/[^\s]*)?')
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
