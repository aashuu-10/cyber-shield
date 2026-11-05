import threading
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
