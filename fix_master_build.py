import os

# 1. WRITE COMPLETE MAIN.PY
main_py = """import os
import re
import time
import urllib.parse
from datetime import datetime

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar

try:
    from plyer import tts, clipboard, vibrator
    PLYER_AVAILABLE = True
except Exception:
    PLYER_AVAILABLE = False

IS_ANDROID = (platform == "android")

class ThreatEngine:
    SUSPICIOUS_KEYWORDS = [
        "lottery", "winner", "prize", "urgent", "blocked", "kyc", "verify",
        "account suspended", "electricity bill", "part time job", "earn daily",
        "click here", "claim now", "free recharge", "banned", "reward points",
        "लॉटरी", "इनाम", "खाता निलंबित", "बिजली बिल", "पार्ट टाइम जॉब", "ओटीपी"
    ]
    SUSPICIOUS_TLDS = [".xyz", ".top", ".club", ".tk", ".ml", ".ga", ".cf", ".gq", ".vip", ".work", ".site", ".online", ".info"]
    KNOWN_PHISHING = ["paypa1.com", "amaz0n.com", "g00gle.com", "sbi-kyc-update.com", "free-recharge-net.com", "yono-sbi-login.xyz", "bank-verify.top"]
    SAFE_DOMAINS = ["google.com", "amazon.in", "sbi.co.in", "hdfcbank.com", "icicibank.com", "gov.in", "nic.in"]

    @classmethod
    def analyze(cls, text):
        if not text or not text.strip():
            return {"score": 0, "level": "SAFE", "flags": ["No text provided"]}

        text_lower = text.lower()
        score = 0
        flags = []

        urls = re.findall(r'https?://\S+|www\.\S+', text_lower)
        for url in urls:
            parsed = urllib.parse.urlparse(url if url.startswith('http') else 'http://' + url)
            domain = parsed.netloc
            if any(bad in domain for bad in cls.KNOWN_PHISHING):
                score += 80
                flags.append(f"Known phishing link: {domain}")
            if any(domain.endswith(tld) for tld in cls.SUSPICIOUS_TLDS):
                score += 40
                flags.append(f"Suspicious high-risk extension: {domain}")
            if not any(safe in domain for safe in cls.SAFE_DOMAINS) and not flags:
                score += 15
                flags.append(f"Unverified third-party link: {domain}")

        for kw in cls.SUSPICIOUS_KEYWORDS:
            if kw in text_lower:
                score += 15
                flags.append(f"Scam keyword detected: '{kw}'")

        if re.search(r'\b(otp|pin|password|cvv)\b', text_lower):
            score += 35
            flags.append("Requests sensitive credentials (OTP/PIN/Password)")

        score = min(score, 100)
        if score >= 70: level = "CRITICAL"
        elif score >= 40: level = "HIGH"
        elif score >= 20: level = "MEDIUM"
        else: level = "SAFE"

        return {"score": score, "level": level, "flags": flags if flags else ["No suspicious patterns found."]}

class CyberShieldProApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_screenshot_time = time.time()
        self.last_clipboard = ""

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        return Builder.load_string(KV_LAYOUT)

    def on_start(self):
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
                print("Permissions error:", e)

        Clock.schedule_interval(self.check_screenshots, 6)
        Clock.schedule_interval(self.check_clipboard, 4)

    def show_toast(self, text):
        try:
            Snackbar(text=text, duration=2).open()
        except Exception:
            pass

    def speak(self, text):
        if PLYER_AVAILABLE:
            try:
                tts.speak(text)
            except Exception:
                self.show_toast("Voice: " + text[:30])
        else:
            self.show_toast("Voice: " + text[:30])

    def run_analysis(self):
        input_text = self.root.ids.scan_input.text
        if not input_text.strip():
            self.show_toast("Please enter text to analyze.")
            return

        res = ThreatEngine.analyze(input_text)
        score = res["score"]
        level = res["level"]

        self.root.ids.score_lbl.text = f"RISK SCORE: {score} / 100"
        self.root.ids.level_lbl.text = f"STATUS: {level}"

        if level == "CRITICAL":
            self.root.ids.level_lbl.theme_text_color = "Custom"
            self.root.ids.level_lbl.text_color = (1, 0.2, 0.2, 1)
            self.root.ids.result_card.md_bg_color = (0.2, 0.05, 0.05, 1)
            self.speak("Warning! Critical scam detected. Do not share OTP.")
            if PLYER_AVAILABLE:
                try: vibrator.vibrate(1)
                except: pass
        elif level == "HIGH":
            self.root.ids.level_lbl.theme_text_color = "Custom"
            self.root.ids.level_lbl.text_color = (1, 0.6, 0.1, 1)
            self.root.ids.result_card.md_bg_color = (0.2, 0.12, 0.02, 1)
            self.speak("Caution! High risk message detected.")
        else:
            self.root.ids.level_lbl.theme_text_color = "Custom"
            self.root.ids.level_lbl.text_color = (0.2, 1, 0.4, 1)
            self.root.ids.result_card.md_bg_color = (0.03, 0.15, 0.05, 1)

        self.root.ids.details_lbl.text = "\\n".join([f"- {flag}" for flag in res["flags"]])

    def clear_input(self):
        self.root.ids.scan_input.text = ""

    def check_screenshots(self, dt):
        if not IS_ANDROID: return
        dirs = ["/sdcard/Pictures/Screenshots", "/sdcard/DCIM/Screenshots", "/storage/emulated/0/Pictures/Screenshots"]
        now = time.time()
        for folder in dirs:
            if os.path.exists(folder):
                try:
                    for f in os.listdir(folder):
                        fpath = os.path.join(folder, f)
                        if os.path.isfile(fpath) and os.path.getmtime(fpath) > self.last_screenshot_time:
                            self.last_screenshot_time = now
                            self.root.ids.sc_log_lbl.text = f"SCREENSHOT DETECTED: {f}"
                            self.speak("Screenshot detected! Verify confidential data is safe.")
                            return
                except Exception:
                    pass

    def check_clipboard(self, dt):
        if not PLYER_AVAILABLE: return
        try:
            content = clipboard.paste()
            if content and content != self.last_clipboard:
                self.last_clipboard = content
                if "http" in content.lower():
                    self.root.ids.cb_log_lbl.text = f"COPIED LINK: {content}"
                    self.root.ids.scan_input.text = content
                    self.show_toast("Link detected in clipboard!")
        except Exception:
            pass

    def call_1930(self):
        self.show_toast("Calling Helpline 1930...")
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

KV_LAYOUT = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "CYBER SHIELD PRO"
            elevation: 2
            md_bg_color: 0.05, 0.15, 0.08, 1
            specific_text_color: 0, 1, 0.4, 1

        MDBottomNavigation:
            panel_color: 0.04, 0.1, 0.06, 1
            selected_color_background: 0, 0.3, 0.1, 0.5
            text_color_active: 0, 1, 0.4, 1

            MDBottomNavigationItem:
                name: 'scan_tab'
                text: 'Scanner'
                icon: 'shield-search'

                MDScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: "16dp"
                        spacing: "14dp"
                        adaptive_height: True

                        MDCard:
                            orientation: 'vertical'
                            padding: "16dp"
                            spacing: "8dp"
                            radius: [12]
                            md_bg_color: 0.06, 0.14, 0.09, 1

                            MDLabel:
                                text: "CYBER SHIELD PRO"
                                font_style: "H5"
                                bold: True
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0, 1, 0.4, 1

                            MDLabel:
                                text: "PAUSE - CHECK - PROTECT"
                                font_style: "Subtitle2"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0, 0.8, 0.5, 1

                        MDTextField:
                            id: scan_input
                            hint_text: "Paste SMS, UPI request, or Web Link..."
                            mode: "rectangle"
                            multiline: True
                            max_height: "100dp"

                        MDBoxLayout:
                            spacing: "10dp"
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
                                on_release: app.clear_input()

                        MDCard:
                            id: result_card
                            orientation: 'vertical'
                            padding: "16dp"
                            spacing: "8dp"
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

            MDBottomNavigationItem:
                name: 'monitor_tab'
                text: 'Monitors & Helpline'
                icon: 'shield-alert'

                MDScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: "16dp"
                        spacing: "14dp"
                        adaptive_height: True

                        MDCard:
                            orientation: 'vertical'
                            padding: "16dp"
                            spacing: "10dp"
                            md_bg_color: 0.15, 0.04, 0.04, 1
                            radius: [12]

                            MDLabel:
                                text: "National Cybercrime Helpline 1930"
                                font_style: "H6"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 1, 0.3, 0.3, 1

                            MDLabel:
                                text: "Dial 1930 immediately if you lost money in a financial fraud."
                                font_style: "Body2"

                            MDFillRoundFlatButton:
                                text: "CALL 1930 NOW"
                                md_bg_color: 0.9, 0.1, 0.1, 1
                                pos_hint: {"center_x": .5}
                                on_release: app.call_1930()

                        MDCard:
                            orientation: 'vertical'
                            padding: "14dp"
                            spacing: "6dp"
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
                                text: "Monitoring active. No screenshots detected."
                                font_style: "Caption"

                        MDCard:
                            orientation: 'vertical'
                            padding: "14dp"
                            spacing: "6dp"
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
                                text: "Monitoring active. No copied links detected."
                                font_style: "Caption"

'''

if __name__ == '__main__':
    CyberShieldProApp().run()
"""

os.makedirs("mobile_app", exist_ok=True)
with open("mobile_app/main.py", "w", encoding="utf-8") as f:
    f.write(main_py)
print("SUCCESS: Updated mobile_app/main.py")

# 2. WRITE BUILDOZER.SPEC WITH PYJNIUS ADDED
spec = """[app]
title = Cyber Shield Pro
package.name = cybershieldpro
package.domain = org.cyphracodes
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.0.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,pyjnius,requests,urllib3,certifi,chardet,idna
orientation = portrait
osx.kivy_version = 2.3.0

fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET,POST_NOTIFICATIONS,VIBRATE,CALL_PHONE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
android.archs = arm64-v8a
android.release_artifact = apk
android.enable_androidx = True

android.presplash_color = #080F0A
"""

with open("mobile_app/buildozer.spec", "w", encoding="utf-8") as f:
    f.write(spec)
print("SUCCESS: Updated mobile_app/buildozer.spec with pyjnius requirement")

# 3. WRITE WORKFLOW FILE WITH VERBOSE LOGGING
workflow = """name: Build Cyber Shield Pro APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Install System Dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \\
          build-essential \\
          git \\
          python3-dev \\
          libsdl2-dev \\
          libsdl2-image-dev \\
          libsdl2-mixer-dev \\
          libsdl2-ttf-dev \\
          libportmidi-dev \\
          zlib1g-dev \\
          libsqlite3-dev \\
          sqlite3 \\
          bzip2 \\
          libbz2-dev \\
          libssl-dev \\
          openssl \\
          libgdbm-dev \\
          libgdbm-compat-dev \\
          liblzma-dev \\
          libffi-dev \\
          libncurses-dev \\
          zip \\
          unzip \\
          autoconf \\
          libtool \\
          cmake \\
          pkg-config

    - name: Install Buildozer & Dependencies
      run: |
        pip install --upgrade pip
        pip install buildozer==1.5.0 cython==0.29.33 kivy==2.3.0 virtualenv

    - name: Build APK with Buildozer
      env:
        APP_ANDROID_ACCEPT_SDK_LICENSES: '1'
      run: |
        mkdir -p ~/.android
        touch ~/.android/repositories.cfg
        cd mobile_app
        buildozer -v android debug

    - name: Upload Cyber Shield Pro Matrix APK
      uses: actions/upload-artifact@v4
      with:
        name: CyberShield-Pro-Matrix-APK
        path: mobile_app/bin/*.apk
        retention-days: 30
"""

os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/build.yml", "w", encoding="utf-8") as f:
    f.write(workflow)
print("SUCCESS: Updated .github/workflows/build.yml")