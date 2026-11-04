package com.cybershield;

import android.app.Application;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.os.Build;

public class CyberShieldApp extends Application {
    public static final String CHANNEL_SERVICE = "cyber_shield_service_channel";
    public static final String CHANNEL_ALERTS = "cyber_shield_alert_channel";

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannels();
    }

    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel serviceChannel = new NotificationChannel(
                    CHANNEL_SERVICE,
                    "Cyber Shield Active Protection",
                    NotificationManager.IMPORTANCE_LOW
            );
            serviceChannel.setDescription("Monitors screenshots and links in real-time.");

            NotificationChannel alertChannel = new NotificationChannel(
                    CHANNEL_ALERTS,
                    "Cyber Shield Security Alerts",
                    NotificationManager.IMPORTANCE_HIGH
            );
            alertChannel.setDescription("Notifications for detected security threats.");

            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(serviceChannel);
                manager.createNotificationChannel(alertChannel);
            }
        }
    }
}
