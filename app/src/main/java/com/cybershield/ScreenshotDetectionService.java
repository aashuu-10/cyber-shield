package com.cybershield;

import android.app.Notification;
import android.app.Service;
import android.content.Intent;
import android.database.ContentObserver;
import android.net.Uri;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.provider.MediaStore;
import androidx.core.app.NotificationCompat;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;

public class ScreenshotDetectionService extends Service {
    private ContentObserver contentObserver;

    @Override
    public void onCreate() {
        super.onCreate();
        startForegroundService();
        registerContentObserver();
    }

    private void startForegroundService() {
        Notification notification = new NotificationCompat.Builder(this, CyberShieldApp.CHANNEL_SERVICE)
                .setContentTitle("Cyber Shield Active")
                .setContentText("Monitoring system for scam screenshots...")
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
        startForeground(1001, notification);
    }

    private void registerContentObserver() {
        contentObserver = new ContentObserver(new Handler(Looper.getMainLooper())) {
            @Override
            public void onChange(boolean selfChange, Uri uri) {
                super.onChange(selfChange, uri);
                if (uri != null && uri.toString().contains(MediaStore.Images.Media.EXTERNAL_CONTENT_URI.toString())) {
                    analyzeImage(uri);
                }
            }
        };
        getContentResolver().registerContentObserver(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                true,
                contentObserver
        );
    }

    private void analyzeImage(Uri uri) {
        try {
            InputImage image = InputImage.fromFilePath(this, uri);
            TextRecognizer recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
            recognizer.process(image)
                    .addOnSuccessListener(visionText -> {
                        String text = visionText.getText();
                        if (ScamPatternDetector.containsScamPattern(text)) {
                            launchAlert(ScamPatternDetector.getDetectedThreatType(text), text);
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void launchAlert(String title, String text) {
        Intent alertIntent = new Intent(this, ScanResultActivity.class);
        alertIntent.putExtra("threat_title", title);
        alertIntent.putExtra("threat_text", text);
        alertIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(alertIntent);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (contentObserver != null) {
            getContentResolver().unregisterContentObserver(contentObserver);
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
