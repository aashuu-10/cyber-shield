import os
import re
import time
import urllib.parse
from datetime import datetime

import kivy
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget

# Plyer for native features
try:
    from plyer import tts, clipboard, notification, vibrator
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

# Platform check
IS_ANDROID = (platform == "android")
if IS_ANDROID:
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.POST_NOTIFICATIONS,
            Permission.VIBRATE,
            Permission.CALL_PHONE
        ])
    except Exception as e:
        print("Android permission error:", e)

# -------------------------------------------------------------
# BILINGUAL TEXT DATABASE (English + Hindi)
# -------------------------------------------------------------
TEXTS = {
    "en": {
        "app_title": "CYBER SHIELD PRO",
        "tagline": "PAUSE - CHECK - PROTECT",
        "sub_tagline": "First-line digital safety assistant. Detect scam SMS, UPI requests, phone calls & risky links.",
        "analyze_btn": "Start Analyzing",
        "helpline_btn": "Helpline 1930",
        "risk_safe": "SAFE (Low Risk)",
        "risk_medium": "MEDIUM RISK (Caution)",
        "risk_high": "HIGH RISK (Suspicious)",
        "risk_critical": "CRITICAL RISK (Scam Confirmed!)",
        "precautions_title": "Recommended Safety Precautions:",
        "precaution_1": "- Never share OTP, PIN, or password with anyone.",
        "precaution_2": "- Do not tap on unknown links or install APKs sent via SMS.",
        "precaution_3": "- Banks never ask for sensitive credentials over phone calls.",
        "precaution_4": "- Immediately report fraudulent transactions on 1930.",
        "lang_toggle": "Language: English"
    },
    "hi": {
        "app_title": "साइबर शील्ड प्रो",
        "tagline": "रुकें - जांचें - सुरक्षित रहें",
        "sub_tagline": "आपकी डिजिटल सुरक्षा सहायक। धोखाधड़ी एसएमएस, यूपीआई अनुरोध और संदिग्ध लिंक की जांच करें।",
        "analyze_btn": "जांच शुरू करें",
        "helpline_btn": "हेल्पलाइन 1930",
        "risk_safe": "सुरक्षित (कम जोखिम)",
        "risk_medium": "मध्यम जोखिम (सावधानी)",
        "risk_high": "उच्च जोखिम (संदिग्ध)",
        "risk_critical": "गंभीर खतरा (स्कैम की पुष्टि!)",
        "precautions_title": "अनुशंसित सुरक्षा सावधानियां:",
        "precaution_1": "- कभी भी किसी के साथ ओटीपी, पिन या पासवर्ड साझा न करें।",
        "precaution_2": "- अज्ञात लिंक पर क्लिक न करें या अज्ञात एपीके इंस्टॉल न करें।",
        "precaution_3": "- बैंक कभी भी फोन कॉल पर गोपनीय जानकारी नहीं मांगते।",
        "precaution_4": "- धोखाधड़ी लेनदेन की तुरंत 1930 पर रिपोर्ट करें।",
        "lang_toggle": "भाषा: हिंदी"
    }
}

# -------------------------------------------------------------
# THREAT ENGINE
# -------------------------------------------------------------
class ThreatEngine:
    SUSPICIOUS_KEYWORDS = [
        "lottery", "winner", "prize", "urgent", "blocked", "kyc", "verify",
        "account suspended", "electricity bill", "part time job", "earn daily",
        "click here", "claim now", "free recharge", "banned", "reward points",
        "लॉटरी", "इनाम", "खाता निलंबित", "बिजली बिल", "पार्ट टाइम जॉब", "ओटीपी"
    ]

    SUSPICIOUS_TLDS = [".xyz", ".top", ".club", ".tk", ".ml", ".ga", ".cf", ".gq", ".vip", ".work", ".site", ".online", ".info"]

    KNOWN_PHISHING = [
        "paypa1.com", "amaz0n.com", "g00gle.com", "sbi-kyc-update.com",
        "free-recharge-net.com", "yono-sbi-login.xyz", "bank-verify.top"
    ]

    SAFE_DOMAINS = ["google.com", "amazon.in", "sbi.co.in", "hdfcbank.com", "icicibank.com", "gov.in", "nic.in"]

    @classmethod
    def analyze(cls, text):
        if not text or not text.strip():
            return {"score": 0, "level": "SAFE", "flags": ["Empty text input"]}

        text_lower = text.lower()
        score = 0
        flags = []

        # 1. URL Analysis
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

            if domain.count('.') > 3:
                score += 25
                flags.append(f"Excessive subdomains in link: {domain}")

            if any(char.isdigit() for char in domain.split('.')[0]):
                score += 20
                flags.append(f"Suspicious numbers in domain: {domain}")

            if not any(safe in domain for safe in cls.SAFE_DOMAINS) and not flags:
                score += 15
                flags.append(f"Unverified third-party link: {domain}")

        # 2. Keyword Analysis
        for kw in cls.SUSPICIOUS_KEYWORDS:
            if kw in text_lower:
                score += 15
                flags.append(f"Urgency/Scam keyword detected: '{kw}'")

        # 3. Urgency / Credential Request Patterns
        if re.search(r'(otp|pin|password|cvv)', text_lower):
            score += 35
            flags.append("Requests sensitive credentials (OTP/PIN/Password)")

        if re.search(r'₹\s*\d+|\d+\s*rs|\d+\s*rupees', text_lower):
            score += 20
            flags.append("Money offer or payment urgency pattern")

        score = min(score, 100)

        if score >= 70:
            level = "CRITICAL"
        elif score >= 40:
            level = "HIGH"
        elif score >= 20:
            level = "MEDIUM"
        else:
            level = "SAFE"

        return {
            "score": score,
            "level": level,
            "flags": flags if flags else ["No suspicious patterns found."]
        }

# -------------------------------------------------------------
# MAIN KIVY UI APPLICATION
# -------------------------------------------------------------
class CyberShieldProApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang = "en"
        self.scan_history = []
        self.last_screenshot_time = time.time()
        self.last_clipboard = ""

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "A400"
        Window.clearcolor = (0.03, 0.06, 0.04, 1)

        # Schedule background monitors
        Clock.schedule_interval(self.check_recent_screenshots, 6)
        Clock.schedule_interval(self.check_clipboard, 4)

        return Builder.load_string(KV_LAYOUT)

    def on_start(self):
        self.root.ids.top_bar.right_action_items = [
            ["translate", lambda x: self.toggle_language()],
            ["shield-half-full", lambda x: self.show_toast("Shield Protection ACTIVE")]
        ]

    def toggle_language(self):
        self.lang = "hi" if self.lang == "en" else "en"
        t = TEXTS[self.lang]
        
        self.root.ids.app_title_lbl.text = t["app_title"]
        self.root.ids.tagline_lbl.text = t["tagline"]
        self.root.ids.sub_tagline_lbl.text = t["sub_tagline"]
        self.root.ids.start_analyze_btn.text = t["analyze_btn"]
        self.root.ids.helpline_btn.text = t["helpline_btn"]
        
        self.show_toast(f"Switched to {t['lang_toggle']}")

    def show_toast(self, text):
        Snackbar(text=text, duration=2).open()

    def speak(self, text):
        if PLYER_AVAILABLE:
            try:
                tts.speak(text)
            except Exception as e:
                self.show_toast("TTS Error: " + str(e))
        else:
            self.show_toast("Voice Alert: " + text[:30] + "...")

    def run_analysis(self):
        input_text = self.root.ids.scan_input.text
        if not input_text.strip():
            self.show_toast("Please enter or paste text to analyze.")
            return

        res = ThreatEngine.analyze(input_text)
        t = TEXTS[self.lang]
        score = res["score"]
        level = res["level"]

        self.scan_history.append({"text": input_text[:40], "score": score, "level": level, "time": datetime.now().strftime("%H:%M:%S")})

        result_card = self.root.ids.result_card
        score_lbl = self.root.ids.score_lbl
        level_lbl = self.root.ids.level_lbl
        details_lbl = self.root.ids.details_lbl
        precautions_lbl = self.root.ids.precautions_lbl

        score_lbl.text = f"RISK SCORE: {score} / 100"
        
        if level == "CRITICAL":
            level_lbl.text = t["risk_critical"]
            level_lbl.theme_text_color = "Custom"
            level_lbl.text_color = (1, 0.2, 0.2, 1)
            result_card.md_bg_color = (0.2, 0.05, 0.05, 1)
            speech = "Warning! Critical scam detected. Do not click links or share OTP." if self.lang == "en" else "चेतावनी! गंभीर स्कैम की पुष्टि हुई है।"
            self.speak(speech)
            if PLYER_AVAILABLE:
                try: vibrator.vibrate(1)
                except: pass
        elif level == "HIGH":
            level_lbl.text = t["risk_high"]
            level_lbl.theme_text_color = "Custom"
            level_lbl.text_color = (1, 0.6, 0.1, 1)
            result_card.md_bg_color = (0.2, 0.12, 0.02, 1)
            self.speak("Caution! High risk message detected.")
        elif level == "MEDIUM":
            level_lbl.text = t["risk_medium"]
            level_lbl.theme_text_color = "Custom"
            level_lbl.text_color = (1, 0.9, 0.2, 1)
            result_card.md_bg_color = (0.15, 0.15, 0.03, 1)
        else:
            level_lbl.text = t["risk_safe"]
            level_lbl.theme_text_color = "Custom"
            level_lbl.text_color = (0.2, 1, 0.4, 1)
            result_card.md_bg_color = (0.03, 0.15, 0.05, 1)

        details_lbl.text = "\n".join([f"- {flag}" for flag in res["flags"]])
        precautions_lbl.text = f"{t['precautions_title']}\n{t['precaution_1']}\n{t['precaution_2']}\n{t['precaution_3']}\n{t['precaution_4']}"

    def run_comparison(self):
        msg1 = self.root.ids.comp_input_1.text
        msg2 = self.root.ids.comp_input_2.text

        if not msg1 or not msg2:
            self.show_toast("Please enter both messages to compare.")
            return

        res1 = ThreatEngine.analyze(msg1)
        res2 = ThreatEngine.analyze(msg2)

        comp_lbl = self.root.ids.comp_result_lbl
        comp_lbl.text = (
            f"MESSAGE A: Risk Score {res1['score']}/100 [{res1['level']}]\n"
            f"MESSAGE B: Risk Score {res2['score']}/100 [{res2['level']}]\n\n"
            f"VERDICT: " + ("Message A is riskier!" if res1['score'] > res2['score'] else "Message B is riskier!" if res2['score'] > res1['score'] else "Both messages have equal risk level.")
        )

    def refresh_dashboard(self):
        container = self.root.ids.history_list
        container.clear_widgets()

        if not self.scan_history:
            container.add_widget(OneLineIconListItem(text="No scan history recorded yet."))
            return

        for item in reversed(self.scan_history):
            icon = IconLeftWidget(icon="alert-decagram" if item["score"] >= 40 else "shield-check")
            list_item = OneLineIconListItem(
                text=f"[{item['time']}] {item['text']}... ({item['score']}/100)",
                on_release=lambda x, it=item: self.show_toast(f"Score: {it['score']} Level: {it['level']}")
            )
            list_item.add_widget(icon)
            container.add_widget(list_item)

    def check_recent_screenshots(self, dt):
        if not IS_ANDROID:
            return

        dirs = [
            "/sdcard/Pictures/Screenshots",
            "/sdcard/DCIM/Screenshots",
            "/storage/emulated/0/Pictures/Screenshots"
        ]

        now = time.time()
        for folder in dirs:
            if os.path.exists(folder):
                try:
                    for f in os.listdir(folder):
                        fpath = os.path.join(folder, f)
                        if os.path.isfile(fpath):
                            mtime = os.path.getmtime(fpath)
                            if mtime > self.last_screenshot_time:
                                self.last_screenshot_time = now
                                self.trigger_screenshot_alert(f)
                                break
                except Exception as e:
                    print("Error checking screenshots:", e)

    def trigger_screenshot_alert(self, filename):
        alert_lbl = self.root.ids.sc_log_lbl
        alert_lbl.text = f"SCREENSHOT DETECTED: {filename}\nTimestamp: {datetime.now().strftime('%H:%M:%S')}\n\nPrecaution: Verify that sensitive OTPs or QR codes are not visible."
        
        if PLYER_AVAILABLE:
            try:
                notification.notify(title="Cyber Shield Alert", message="Screenshot detected! Protect confidential data.")
                vibrator.vibrate(1)
            except: pass
        self.speak("Screenshot detected! Protect confidential data.")

    def check_clipboard(self, dt):
        if not PLYER_AVAILABLE:
            return
        try:
            content = clipboard.paste()
            if content and content != self.last_clipboard:
                self.last_clipboard = content
                if any(kw in content.lower() for kw in ["http://", "https://", "www.", ".xyz", ".top"]):
                    cb_lbl = self.root.ids.cb_log_lbl
                    cb_lbl.text = f"COPIED LINK DETECTED:\n{content}\n\nAuto Analysis: High-priority link scan queued."
                    self.root.ids.scan_input.text = content
                    self.show_toast("Link detected in clipboard! Auto-filled in scanner.")
        except Exception:
            pass

    def call_1930(self):
        self.show_toast("Initiating Call to Emergency Helpline 1930...")
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
# KIVY KV DESIGN LANGUAGE (Matrix Green Cyberpunk Theme)
# -------------------------------------------------------------
KV_LAYOUT = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            id: top_bar
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
                                id: app_title_lbl
                                text: "CYBER SHIELD PRO"
                                font_style: "H4"
                                halign: "center"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0, 1, 0.4, 1

                            MDLabel:
                                id: tagline_lbl
                                text: "PAUSE - CHECK - PROTECT"
                                font_style: "Subtitle1"
                                halign: "center"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0, 0.8, 0.5, 1

                            MDLabel:
                                id: sub_tagline_lbl
                                text: "First-line digital safety assistant. Detect scam SMS, UPI requests, phone calls & risky links."
                                font_style: "Body2"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0.7, 0.9, 0.7, 1

                        MDBoxLayout:
                            spacing: dp(10)
                            adaptive_height: True

                            MDFillRoundFlatButton:
                                id: start_analyze_btn
                                text: "Start Analyzing"
                                icon: "magnify"
                                md_bg_color: 0, 0.8, 0.3, 1
                                text_color: 0, 0, 0, 1
                                size_hint_x: 0.5
                                on_release: scan_input.focus = True

                            MDFillRoundFlatButton:
                                id: helpline_btn
                                text: "Helpline 1930"
                                icon: "phone-alert"
                                md_bg_color: 0.9, 0.2, 0.2, 1
                                text_color: 1, 1, 1, 1
                                size_hint_x: 0.5
                                on_release: app.call_1930()

                        MDGridLayout:
                            cols: 2
                            spacing: dp(10)
                            adaptive_height: True

                            MDCard:
                                padding: dp(15)
                                md_bg_color: 0.05, 0.12, 0.07, 1
                                radius: [10]
                                orientation: 'vertical'
                                MDLabel:
                                    text: "SMART SCAN"
                                    bold: True
                                    theme_text_color: "Custom"
                                    text_color: 0, 1, 0.4, 1
                                MDLabel:
                                    text: "Bilingual Scam Rule Engine"
                                    font_style: "Caption"

                            MDCard:
                                padding: dp(15)
                                md_bg_color: 0.05, 0.12, 0.07, 1
                                radius: [10]
                                orientation: 'vertical'
                                MDLabel:
                                    text: "LOCAL PRIVACY"
                                    bold: True
                                    theme_text_color: "Custom"
                                    text_color: 0, 1, 0.4, 1
                                MDLabel:
                                    text: "100% On-Device Analysis"
                                    font_style: "Caption"

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

                        MDBoxLayout:
                            spacing: dp(10)
                            adaptive_height: True

                            MDRaisedButton:
                                text: "ANALYZE THREAT"
                                md_bg_color: 0, 0.8, 0.3, 1
                                text_color: 0, 0, 0, 1
                                size_hint_x: 0.7
                                on_release: app.run_analysis()

                            MDRectangleFlatButton:
                                text: "CLEAR"
                                size_hint_x: 0.3
                                on_release: scan_input.text = ""

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

                            MDLabel:
                                id: details_lbl
                                text: "Threat indicators will appear here."
                                font_style: "Body2"

                            MDLabel:
                                id: precautions_lbl
                                text: ""
                                font_style: "Caption"
                                theme_text_color: "Custom"
                                text_color: 0.8, 0.8, 0.8, 1

            MDBottomNavigationItem:
                name: 'compare_tab'
                text: 'Compare'
                icon: 'compare-horizontal'

                MDScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(12)
                        adaptive_height: True

                        MDLabel:
                            text: "Message Risk Comparison"
                            font_style: "H6"
                            theme_text_color: "Custom"
                            text_color: 0, 1, 0.4, 1

                        MDTextField:
                            id: comp_input_1
                            hint_text: "Message A (e.g. Received SMS)"
                            mode: "rectangle"

                        MDTextField:
                            id: comp_input_2
                            hint_text: "Message B (e.g. Official Bank SMS)"
                            mode: "rectangle"

                        MDRaisedButton:
                            text: "COMPARE BOTH MESSAGES"
                            md_bg_color: 0, 0.8, 0.3, 1
                            text_color: 0, 0, 0, 1
                            on_release: app.run_comparison()

                        MDCard:
                            padding: dp(15)
                            md_bg_color: 0.04, 0.1, 0.06, 1
                            radius: [10]
                            adaptive_height: True

                            MDLabel:
                                id: comp_result_lbl
                                text: "Enter two messages above and click compare."
                                font_style: "Body1"

            MDBottomNavigationItem:
                name: 'dash_tab'
                text: 'Dashboard'
                icon: 'view-dashboard'
                on_tab_press: app.refresh_dashboard()

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(10)

                    MDLabel:
                        text: "Threat Scan History & Stats"
                        font_style: "H6"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: 0, 1, 0.4, 1

                    MDScrollView:
                        MDList:
                            id: history_list

            MDBottomNavigationItem:
                name: 'report_tab'
                text: 'Report 1930'
                icon: 'phone-alert'

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
                            md_bg_color: 0.15, 0.04, 0.04, 1
                            radius: [12]

                            MDLabel:
                                text: "National Cybercrime Helpline 1930"
                                font_style: "H6"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 1, 0.3, 0.3, 1

                            MDLabel:
                                text: "1. Dial 1930 immediately if you lost money in a financial fraud."
                                font_style: "Body2"

                            MDLabel:
                                text: "2. Have your bank account number and UPI transaction ID ready."
                                font_style: "Body2"

                            MDLabel:
                                text: "3. File a formal complaint at cybercrime.gov.in."
                                font_style: "Body2"

                            MDFillRoundFlatButton:
                                text: "CALL 1930 NOW"
                                md_bg_color: 0.9, 0.1, 0.1, 1
                                pos_hint: {"center_x": .5}
                                on_release: app.call_1930()

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
                                text: "No recent screenshot alerts."
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
                                text: "No suspicious links copied recently."
                                font_style: "Caption"

'''

if __name__ == '__main__':
    CyberShieldProApp().run()
