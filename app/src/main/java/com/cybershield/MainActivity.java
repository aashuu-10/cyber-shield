package com.cybershield;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private TextView tvStatus;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvStatus = findViewById(R.id.tvStatus);
        Button btnStartService = findViewById(R.id.btnStartService);

        btnStartService.setOnClickListener(v -> startShieldServices());

        updateStatus();
    }

    private void startShieldServices() {
        Intent screenshotIntent = new Intent(this, ScreenshotDetectionService.class);
        Intent clipboardIntent = new Intent(this, ClipboardMonitorService.class);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(screenshotIntent);
            startForegroundService(clipboardIntent);
        } else {
            startService(screenshotIntent);
            startService(clipboardIntent);
        }
        updateStatus();
    }

    private void updateStatus() {
        tvStatus.setText("Cyber Shield Protection: ACTIVE");
    }
}
