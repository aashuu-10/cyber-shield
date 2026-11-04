package com.cybershield;

import android.app.Notification;
import android.app.Service;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;

public class ClipboardMonitorService extends Service {
    private ClipboardManager clipboardManager;
    private ClipboardManager.OnPrimaryClipChangedListener listener;

    @Override
    public void onCreate() {
        super.onCreate();
        startForegroundService();

        clipboardManager = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        listener = () -> {
            if (clipboardManager.hasPrimaryClip() && clipboardManager.getPrimaryClip().getItemCount() > 0) {
                CharSequence text = clipboardManager.getPrimaryClip().getItemAt(0).getText();
                if (text != null) {
                    checkClipboardContent(text.toString());
                }
            }
        };
        if (clipboardManager != null) {
            clipboardManager.addPrimaryClipChangedListener(listener);
        }
    }

    private void startForegroundService() {
        Notification notification = new NotificationCompat.Builder(this, CyberShieldApp.CHANNEL_SERVICE)
                .setContentTitle("Cyber Shield Clipboard Guard")
                .setContentText("Monitoring copied links for phishing threats...")
                .setSmallIcon(android.R.drawable.ic_menu_compass)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
        startForeground(1002, notification);
    }

    private void checkClipboardContent(String content) {
        if (LinkAnalyzer.isSuspiciousUrl(content)) {
            Intent alertIntent = new Intent(this, ScanResultActivity.class);
            alertIntent.putExtra("threat_title", "Phishing Link Detected in Clipboard");
            alertIntent.putExtra("threat_text", content + "\n\nReason: " + LinkAnalyzer.getRiskReason(content));
            alertIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(alertIntent);
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (clipboardManager != null && listener != null) {
            clipboardManager.removePrimaryClipChangedListener(listener);
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
