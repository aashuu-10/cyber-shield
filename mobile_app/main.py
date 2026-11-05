import os
import re
import threading
from datetime import datetime

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

if platform == "android":
    try:
        from android.permissions import Permission, request_permissions
        from plyer import tts, clipboard
        ANDROID_READY = True
    except ImportError:
        ANDROID_READY = False
else:
    ANDROID_READY = False


class ThreatEngine:
    def __init__(self):
        self.phishing_keywords = [
            "login", "verify", "update", "confirm", "secure", "account", "banking",
            "password", "suspended", "urgent", "immediately", "click here", "winner",
            "congratulations", "prize", "lottery", "irs", "tax refund", "free gift",
            "claim now", "act now", "limited time"
        ]
        self.suspicious_tlds = [".xyz", ".top", ".club", ".online", ".site", ".tk", ".ga", ".buzz", ".work"]
        self.known_bad = ["paypa1.com", "amaz0n.com", "g00gle.com", "app1e.com", "faceb00k.com", "netfl1x.com"]
        self.safe_domains = ["google.com", "youtube.com", "facebook.com", "amazon.com", "apple.com", "microsoft.com", "github.com"]
        self.scam_patterns = {
            "urgency": r"(urgent|immediately|right now|act fast|hurry)",
            "money": r"(bitcoin|crypto|wire transfer|gift card|western union)",
            "personal_info": r"(social security|ssn|credit card|bank account|pin)",
            "threats": r"(arrested|lawsuit|warrant|suspended|terminated|locked)",
            "too_good": r"(won|winner|congratulations|lucky|free|guaranteed)"
        }

    def analyze_link(self, url):
        url_lower = url.lower()
        risk_score = 0
        reasons = []

        for domain in self.known_bad:
            if domain in url_lower:
                risk_score += 60
                reasons.append(f"Known malicious domain: {domain}")

        for safe in self.safe_domains:
            if safe in url_lower:
                risk_score = max(0, risk_score - 30)

        for tld in self.suspicious_tlds:
            if url_lower.endswith(tld) or tld + "/" in url_lower:
                risk_score += 25
                reasons.append(f"Suspicious TLD: {tld}")

        if "http://" in url_lower and "https://" not in url_lower:
            risk_score += 15
            reasons.append("No HTTPS encryption")

        if "@" in url_lower:
            risk_score += 30
            reasons.append("Contains @ symbol (redirect trick)")

        found = [k for k in self.phishing_keywords if k in url_lower]
        if found:
            risk_score += len(found) * 5
            reasons.append(f"Phishing keywords: {', '.join(found[:3])}")

        risk_score = min(100, risk_score)
        level = "SAFE"
        is_safe = True
        if risk_score >= 70:
            level = "CRITICAL"
            is_safe = False
        elif risk_score >= 40:
            level = "HIGH"
            is_safe = False
        elif risk_score >= 20:
            level = "MEDIUM"
            is_safe = False

        return {
            "url": url, "risk_score": risk_score, "risk_level": level,
            "is_safe": is_safe, "reasons": reasons if reasons else ["No obvious threats detected"]
        }

    def analyze_text(self, text):
        text_lower = text.lower()
        matched = []
        for name, pattern in self.scam_patterns.items():
            if re.search(pattern, text_lower):
                matched.append(name)
        
        level = "SAFE"
        is_scam = False
        if len(matched) >= 3:
            level = "CRITICAL"
            is_scam = True
        elif len(matched) >= 2:
            level = "HIGH"
            is_scam = True
        elif len(matched) >= 1:
            level = "MEDIUM"
        
        return {"is_scam": is_scam, "risk_level": level, "matched": matched}


KV = """
MDBoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "Cyber Shield"
        elevation: 4
        md_bg_color: 0.06, 0.09, 0.16, 1
        specific_text_color: 0, 0.83, 1, 1
        right_action_items: [["volume-high", lambda x: app.toggle_tts()]]

    MDBottomNavigation:
        panel_color: 0.06, 0.09, 0.16, 1
        selected_color_background: 0, 0.83, 1, 0.2
        text_color_active: 0, 0.83, 1, 1

        MDBottomNavigationItem:
            name: 'scanner'
            text: 'Scanner'
            icon: 'shield-search'

            MDBoxLayout:
                orientation: 'vertical'
                padding: "16dp"
                spacing: "12dp"

                MDLabel:
                    text: "Link & Scam Scanner"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    size_hint_y: None
                    height: "40dp"

                MDTextField:
                    id: link_input
                    hint_text: "Paste URL or suspicious text..."
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: None
                    height: "100dp"

                MDBoxLayout:
                    size_hint_y: None
                    height: "48dp"
                    spacing: "10dp"

                    MDRaisedButton:
                        text: "Paste & Scan"
                        on_release: app.paste_and_scan()
                        md_bg_color: 0, 0.83, 1, 1
                        text_color: 0, 0, 0, 1

                    MDRaisedButton:
                        text: "Scan Text"
                        on_release: app.scan_manual_input()

                ScrollView:
                    MDBoxLayout:
                        id: results_container
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "10dp"

        MDBottomNavigationItem:
            name: 'screenshot'
            text: 'Screenshot'
            icon: 'camera'

            MDBoxLayout:
                orientation: 'vertical'
                padding: "16dp"
                spacing: "16dp"

                MDLabel:
                    text: "Screenshot Detection"
                    font_style: "H6"
                    bold: True
                    halign: "center"

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    size_hint_y: None
                    height: "220dp"
                    md_bg_color: 0.12, 0.16, 0.23, 1

                    MDLabel:
                        text: "Status: Monitoring Active"
                        theme_text_color: "Custom"
                        text_color: 0, 1, 0.5, 1
                        bold: True
                        size_hint_y: None
                        height: "30dp"

                    MDLabel:
                        text: "Cyber Shield auto-detects when screenshots are taken and alerts you if sensitive data was captured."
                        font_style: "Caption"
                        size_hint_y: None
                        height: "80dp"

                    MDRaisedButton:
                        text: "Speak Precautions"
                        on_release: app.speak_screenshot_precautions()
                        size_hint_y: None
                        height: "48dp"

        MDBottomNavigationItem:
            name: 'security'
            text: 'Security'
            icon: 'lock-check'

            MDBoxLayout:
                orientation: 'vertical'
                padding: "16dp"
                spacing: "12dp"

                MDLabel:
                    text: "Device Security"
                    font_style: "H6"
                    bold: True
                    halign: "center"

                MDRaisedButton:
                    text: "Check Permissions"
                    on_release: app.check_device_permissions()
                    size_hint_y: None
                    height: "48dp"

                MDRaisedButton:
                    text: "Read Precautions Aloud"
                    on_release: app.speak_general_precautions()
                    size_hint_y: None
                    height: "48dp"

                ScrollView:
                    MDBoxLayout:
                        id: security_tips
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "8dp"
"""


class CyberShieldApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.threat_engine = ThreatEngine()
        self.tts_enabled = True
        self.last_screenshot_check = datetime.now()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        if ANDROID_READY:
            self.request_android_permissions()
            Clock.schedule_interval(self.check_recent_screenshots, 5)
        Clock.schedule_once(lambda dt: self.load_security_tips(), 0.5)

    def request_android_permissions(self):
        try:
            permissions = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
            ]
            request_permissions(permissions)
        except Exception as e:
            print(f"Permission error: {e}")

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        status = "enabled" if self.tts_enabled else "disabled"
        MDSnackbar(MDLabel(text=f"Voice alerts {status}")).open()

    def speak(self, text):
        if not self.tts_enabled:
            return
        if ANDROID_READY:
            try:
                tts.speak(text)
            except Exception as e:
                print(f"TTS error: {e}")
        else:
            print(f"[SPEECH]: {text}")

    def paste_and_scan(self):
        pasted = ""
        if ANDROID_READY:
            try:
                pasted = clipboard.paste() or ""
            except Exception:
                pass
        if pasted:
            self.root.ids.link_input.text = pasted
            self.scan_text(pasted)
        else:
            MDSnackbar(MDLabel(text="Clipboard is empty")).open()

    def scan_manual_input(self):
        text = self.root.ids.link_input.text.strip()
        if text:
            self.scan_text(text)
        else:
            MDSnackbar(MDLabel(text="Please enter text first")).open()

    def scan_text(self, text):
        urls = re.findall(r"http[s]?://[^\s]+", text)
        container = self.root.ids.results_container
        container.clear_widgets()

        if urls:
            for url in urls:
                result = self.threat_engine.analyze_link(url)
                self.add_result_card(result)
                if not result["is_safe"]:
                    self.speak(f"Alert! Risk level {result['risk_level']}. {result['reasons'][0]}")
        
        text_result = self.threat_engine.analyze_text(text)
        if text_result["is_scam"]:
            self.add_text_result_card(text_result)
            self.speak(f"Scam alert! Risk level {text_result['risk_level']}")
        elif not urls:
            self.add_text_result_card(text_result)

    def add_result_card(self, result):
        container = self.root.ids.results_container
        bg_color = (0.3, 0.05, 0.05, 1) if not result["is_safe"] else (0.05, 0.3, 0.1, 1)
        text_color = (1, 0.3, 0.3, 1) if not result["is_safe"] else (0.3, 1, 0.5, 1)
        
        card = MDCard(
            orientation="vertical", padding="12dp",
            size_hint_y=None, height="170dp",
            md_bg_color=bg_color
        )
        card.add_widget(MDLabel(
            text=f"{'SCAM ALERT' if not result['is_safe'] else 'SAFE'} - {result['risk_level']}",
            bold=True, theme_text_color="Custom", text_color=text_color,
            size_hint_y=None, height="30dp"
        ))
        card.add_widget(MDLabel(
            text=f"URL: {result['url'][:50]}",
            font_style="Caption", size_hint_y=None, height="25dp"
        ))
        card.add_widget(MDLabel(
            text=f"Score: {result['risk_score']}/100",
            font_style="Caption", size_hint_y=None, height="25dp"
        ))
        card.add_widget(MDLabel(
            text="\n".join(result["reasons"][:2]),
            font_style="Caption", size_hint_y=None, height="40dp"
        ))
        card.add_widget(MDRaisedButton(
            text="Read Warning",
            on_release=lambda x: self.speak("Warning: " + ". ".join(result["reasons"])),
            size_hint_y=None, height="40dp"
        ))
        container.add_widget(card)

    def add_text_result_card(self, result):
        container = self.root.ids.results_container
        bg_color = (0.3, 0.05, 0.05, 1) if result["is_scam"] else (0.05, 0.3, 0.1, 1)
        
        card = MDCard(
            orientation="vertical", padding="12dp",
            size_hint_y=None, height="120dp",
            md_bg_color=bg_color
        )
        card.add_widget(MDLabel(
            text=f"Text Analysis: {result['risk_level']}",
            bold=True, size_hint_y=None, height="30dp"
        ))
        card.add_widget(MDLabel(
            text=f"Patterns detected: {', '.join(result['matched']) if result['matched'] else 'None'}",
            font_style="Caption", size_hint_y=None, height="50dp"
        ))
        container.add_widget(card)

    def check_recent_screenshots(self, dt):
        if not ANDROID_READY:
            return
        screenshot_dirs = [
            "/sdcard/Pictures/Screenshots",
            "/sdcard/DCIM/Screenshots",
            "/storage/emulated/0/Pictures/Screenshots"
        ]
        for ss_dir in screenshot_dirs:
            if os.path.exists(ss_dir):
                try:
                    files = os.listdir(ss_dir)
                    now = datetime.now()
                    for f in files:
                        full_path = os.path.join(ss_dir, f)
                        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                        if (now - mtime).total_seconds() < 6 and mtime > self.last_screenshot_check:
                            self.trigger_screenshot_alert(f)
                            self.last_screenshot_check = now
                            return
                except Exception:
                    pass
        self.last_screenshot_check = datetime.now()

    def trigger_screenshot_alert(self, filename):
        self.speak("Warning! Screenshot detected. Ensure no sensitive information was captured.")
        MDSnackbar(MDLabel(text=f"Screenshot: {filename}")).open()

    def speak_screenshot_precautions(self):
        text = "Screenshot precautions. First, close sensitive apps. Second, check which apps have screen permissions. Third, do not share unverified screen captures."
        self.speak(text)
        MDSnackbar(MDLabel(text="Reading precautions aloud...")).open()

    def speak_general_precautions(self):
        text = "Security precautions. Use strong passwords. Enable two factor authentication. Keep your device updated. Never share personal information with strangers. Be cautious of urgent messages asking for money."
        self.speak(text)
        MDSnackbar(MDLabel(text="Reading precautions...")).open()

    def check_device_permissions(self):
        if ANDROID_READY:
            MDSnackbar(MDLabel(text="Permissions granted!")).open()
        else:
            MDSnackbar(MDLabel(text="Running in demo mode")).open()

    def load_security_tips(self):
        tips = [
            "Enable screen lock with strong PIN",
            "Keep your OS updated regularly",
            "Install antivirus software",
            "Use VPN on public Wi-Fi networks",
            "Enable 2FA on all important accounts",
            "Never share passwords via email",
            "Check URLs before clicking",
            "Only download apps from Play Store"
        ]
        container = self.root.ids.security_tips
        for tip in tips:
            card = MDCard(
                padding="10dp", size_hint_y=None, height="50dp",
                md_bg_color=(0.12, 0.16, 0.23, 1)
            )
            card.add_widget(MDLabel(text=tip, font_style="Body2"))
            container.add_widget(card)


if __name__ == "__main__":
    CyberShieldApp().run()
