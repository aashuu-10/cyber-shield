import os, sys, re
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
