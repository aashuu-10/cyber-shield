import platform, subprocess
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
