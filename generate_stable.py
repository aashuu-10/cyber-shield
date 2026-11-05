import os

main_py_content = """import os
import re
import time
import urllib.parse
from datetime import datetime

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

# Safe Native Imports
try:
    from plyer import tts, clipboard, vibrator
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

IS_ANDROID = (platform == "android")

# -------------------------------------------------------------
# THREAT ENGINE (Scam Detection Logic)
# -------------------------------------------------------------
class ThreatEngine:
    SUSPICIOUS_KEYWORDS = ["lottery", "winner", "prize", "urgent", "blocked", "kyc", "verify", "account suspended", "electricity bill", "part time job", "earn daily", "click here", "claim now", "free recharge", "banned", "reward points", "लॉटरी", "इनाम", "खाता निलंबित", "बिजली बिल", "पार्ट टाइम जॉब", "ओटीपी"]
    SUSPICIOUS_TLDS = [".xyz", ".top", ".club", ".tk", ".ml", ".ga", ".cf", ".gq", ".vip", ".work", ".site", ".online", ".info"]
    KNOWN_PHISHING = ["paypa1.com", "amaz0n.com", "g00gle.com", "sbi-kyc-update.com", "free-recharge-net.com", "yono-sbi-login.xyz", "bank-verify.top"]
    SAFE_DOMAINS = ["google.com", "amazon.in", "sbi.co.in", "hdfcbank.com", "icicibank.com", "gov.in", "nic.in"]

    @classmethod
    def analyze(cls, text):
        if not text or not text.strip():
            return {"score": 0, "level": "SAFE", "flags": ["Empty text input"]}

        text_lower = text.lower()
        score = 0
        flags = []

        urls = re.findall(r'https?://\S+|www\.\S+', text_lower)
        for url in urls:
            parsed = urllib.parse.urlparse(url if url.startswith('http') else 'http://' + url)
            domain = parsed.netloc
            if any(bad in domain for bad in cls.KNOWN_PHISHING):
                score += 80
                flags.append(f"Known phishing domain: {domain}")
            if any(domain.endswith(tld) for tld in cls.SUSPICIOUS_TLDS):
                score += 40
                flags.append(f"Suspicious high-risk TLD: {domain}")
            if not any(safe in domain for safe in cls.SAFE_DOMAINS) and not flags:
                score += 15
                flags.append(f"Unverified third-party link: {domain}")

        for kw in cls.SUSPICIOUS_KEYWORDS:
            if kw in text_lower:
                score += 15
                flags.append(f"Urgency/Scam keyword detected: '{kw}'")

        if re.search(r'\b(otp|pin|password|cvv)\b', text_lower):
            score += 35
            flags.append("Requests sensitive credentials (OTP/PIN/Password)")

        score = min(score, 100)
        if score >= 70: level = "CRITICAL"
        elif score >= 40: level = "HIGH"
        elif score >= 20: level = "MEDIUM"
        else: level = "SAFE"

        return {"score": score, "level": level, "flags": flags if flags else ["No suspicious patterns found."]}

# -------------------------------------------------------------
# MAIN APP
# -------------------------------------------------------------
class CyberShieldProApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scan_history = []
        self.last_screenshot_time = time.time()
        self.last_clipboard = ""

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "A400"
        Window.clearcolor = (0.03, 0.06, 0.04, 1)
        return Builder.load_string(KV_LAYOUT)

    def on_start(self):
        # SAFELY REQUEST PERMISSIONS ON STARTUP (Prevents Android Crash)
        if IS_ANDROID:
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.INTERNET,
                    Permission.VIBRATE,
                    Permission.CALL_PHONE
                ])
            except Exception as e:
                print("Permission request failed safely:", e)

        # Start background tasks safely
        Clock.schedule_interval(self.safe_check_screenshots, 8)
        Clock.schedule_interval(self.safe_check_clipboard, 5)

    def show_toast(self, text):
        Snackbar(text=text, duration=2).open()

    def speak(self, text):
        if PLYER_AVAILABLE:
            try: tts.speak(text)
            except: self.show_toast("Voice Alert: " + text[:30])

    def run_analysis(self):
        input_text = self.root.ids.scan_input.text
        if not input_text.strip():
            self.show_toast("Please enter text to analyze.")
            return

        res = ThreatEngine.analyze(input_text)
        score = res["score"]
        level = res["level"]

        self.scan_history.append({"text": input_text[:40], "score": score, "level": level, "time": datetime.now().strftime("%H:%M:%S")})

        self.root.ids.score_lbl.text = f"RISK SCORE: {score} / 100"
        self.root.ids.level_lbl.text = level
        
        if level == "CRITICAL":
            self.root.ids.level_lbl.text_color = (1, 0.2, 0.2, 1)
            self.root.ids.result_card.md_bg_color = (0.2, 0.05, 0.05, 1)
            self.speak("Warning! Critical scam detected. Do not click links.")
            if PLYER_AVAILABLE:
                try: vibrator.vibrate(1)
                except: pass
        elif level == "HIGH":
            self.root.ids.level_lbl.text_color = (1, 0.6, 0.1, 1)
            self.root.ids.result_card.md_bg_color = (0.2, 0.12, 0.02, 1)
            self.speak("Caution! High risk message detected.")
        else:
            self.root.ids.level_lbl.text_color = (0.2, 1, 0.4, 1)
            self.root.ids.result_card.md_bg_color = (0.03, 0.15, 0.05, 1)

        self.root.ids.details_lbl.text = "\\n".join([f"- {flag}" for flag in res["flags"]])

    def safe_check_screenshots(self, dt):
        if not IS_ANDROID: return
        try:
            dirs = ["/sdcard/Pictures/Screenshots", "/sdcard/DCIM/Screenshots"]
            now = time.time()
            for folder in dirs:
                if os.path.exists(folder):
                    for f in os.listdir(folder):
                        fpath = os.path.join(folder, f)
                        if os.path.isfile(fpath) and os.path.getmtime(fpath) > self.last_screenshot_time:
                            self.last_screenshot_time = now
                            self.root.ids.sc_log_lbl.text = f"SCREENSHOT DETECTED: {f}\\nTime: {datetime.now().strftime('%H:%M:%S')}"
                            self.speak("Screenshot detected! Protect confidential data.")
                            return
        except Exception as e:
            print("Screenshot check blocked by Android security:", e)

    def safe_check_clipboard(self, dt):
        if not PLYER_AVAILABLE: return
        try:
            content = clipboard.paste()
            if content and content != self.last_clipboard:
                self.last_clipboard = content
                if "http" in content.lower():
                    self.root.ids.cb_log_lbl.text = f"COPIED LINK DETECTED:\\n{content}"
                    self.root.ids.scan_input.text = content
                    self.show_toast("Link detected in clipboard!")
        except Exception as e:
            print("Clipboard check blocked by Android security:", e)

    def call_1930(self):
        self.show_toast("Initiating Call to 1930...")
        if IS_ANDROID:
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                intent = Intent(Intent.ACTION_DIAL)
                intent.setData(Uri.parse("tel:1930"))
                currentActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                currentActivity.startActivity(intent)
            except Exception as e:
                self.show_toast("Dialer error: " + str(e))

# -------------------------------------------------------------
# KIVY UI LAYOUT
# -------------------------------------------------------------
KV_LAYOUT = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "CYBER SHIELD PRO"
            elevation: 4
            md_bg_color: 0.05, 0.15, 0.08, 1
            specific_text_color: 0, 1, 0.4, 1

        MDBottomNavigation:
            selected_color_background: 0, 0.3, 0.1, 0.5
            text_color_active: 0, 1, 0.4, 1
            panel_color: 0.04, 0.1, 0.06, 1

            MDBottomNavigationItem:
                name: 'home_tab'
                text: 'Home'
                icon: 'shield-home'

                MDScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(15)
                        adaptive_height: True

                        MDCard:
                            orientation: 'vertical'
                            padding: dp(20)
                            spacing: dp(10)
                            radius: [15]
                            md_bg_color: 0.06, 0.14, 0.09, 1
                            line_color: 0, 1, 0.4, 0.4

                            MDIconButton:
                                icon: "shield-lock"
                                user_font_size: "64sp"
                                pos_hint: {"center_x": .5}
                                theme_text_color: "Custom"
                                text_color: 0, 1, 0.4, 1

                            MDLabel:
                                text: "CYBER SHIELD PRO"
                                font_style: "H4"
                                halign: "center"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0, 1, 0.4, 1

                            MDLabel:
                                text: "PAUSE - CHECK - PROTECT"
                                font_style: "Subtitle1"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0, 0.8, 0.5, 1

                        MDBoxLayout:
                            spacing: dp(10)
                            adaptive_height: True

                            MDFillRoundFlatButton:
                                text: "Start Analyzing"
                                icon: "magnify"
                                md_bg_color: 0, 0.8, 0.3, 1
                                text_color: 0, 0, 0, 1
                                size_hint_x: 0.5
                                on_release: scan_input.focus = True

                            MDFillRoundFlatButton:
                                text: "Helpline 1930"
                                icon: "phone-alert"
                                md_bg_color: 0.9, 0.2, 0.2, 1
                                text_color: 1, 1, 1, 1
                                size_hint_x: 0.5
                                on_release: app.call_1930()

            MDBottomNavigationItem:
                name: 'analyze_tab'
                text: 'Analyze'
                icon: 'magnify-scan'

                MDScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(15)
                        adaptive_height: True

                        MDTextField:
                            id: scan_input
                            hint_text: "Paste SMS, UPI request, or Link here..."
                            mode: "rectangle"
                            multiline: True
                            max_height: dp(120)

                        MDRaisedButton:
                            text: "ANALYZE THREAT"
                            md_bg_color: 0, 0.8, 0.3, 1
                            text_color: 0, 0, 0, 1
                            size_hint_x: 1
                            on_release: app.run_analysis()

                        MDCard:
                            id: result_card
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(8)
                            radius: [10]
                            md_bg_color: 0.04, 0.1, 0.06, 1
                            adaptive_height: True

                            MDLabel:
                                id: score_lbl
                                text: "RISK SCORE: -- / 100"
                                font_style: "H6"
                                bold: True

                            MDLabel:
                                id: level_lbl
                                text: "Awaiting analysis..."
                                font_style: "Subtitle1"
                                theme_text_color: "Custom"

                            MDLabel:
                                id: details_lbl
                                text: "Threat indicators will appear here."
                                font_style: "Body2"

            MDBottomNavigationItem:
                name: 'report_tab'
                text: 'Monitors'
                icon: 'eye-outline'

                MDScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(15)
                        adaptive_height: True

                        MDCard:
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(8)
                            md_bg_color: 0.04, 0.1, 0.06, 1
                            radius: [10]

                            MDLabel:
                                text: "Screenshot Monitor Log"
                                font_style: "Subtitle1"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0, 1, 0.4, 1

                            MDLabel:
                                id: sc_log_lbl
                                text: "Monitoring active. No recent screenshots."
                                font_style: "Caption"

                        MDCard:
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(8)
                            md_bg_color: 0.04, 0.1, 0.06, 1
                            radius: [10]

                            MDLabel:
                                text: "Clipboard Link Monitor"
                                font_style: "Subtitle1"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0, 1, 0.4, 1

                            MDLabel:
                                id: cb_log_lbl
                                text: "Monitoring active. No links copied."
                                font_style: "Caption"
'''

if __name__ == '__main__':
    CyberShieldProApp().run()
"""

os.makedirs("mobile_app", exist_ok=True)
with open("mobile_app/main.py", "w", encoding="utf-8") as f:
    f.write(main_py_content)
print("SUCCESS: Written Crash-Proof mobile_app/main.py!")