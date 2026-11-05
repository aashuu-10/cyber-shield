package com.cybershield;

import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class ScanResultActivity extends AppCompatActivity {
    private TextToSpeechService ttsService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_scan_result);

        ttsService = new TextToSpeechService(this);

        TextView tvTitle = findViewById(R.id.tvThreatTitle);
        TextView tvText = findViewById(R.id.tvThreatDetails);
        Button btnDismiss = findViewById(R.id.btnDismiss);

        String title = getIntent().getStringExtra("threat_title");
        String details = getIntent().getStringExtra("threat_text");

        tvTitle.setText(title != null ? title : "Security Warning!");
        tvText.setText(details != null ? details : "Suspicious content detected.");

        String speakMessage = "Warning! Cyber Shield detected a threat: " + (title != null ? title : "Suspicious content");
        ttsService.speak(speakMessage);

        btnDismiss.setOnClickListener(v -> finish());
    }

    @Override
    protected void onDestroy() {
        if (ttsService != null) {
            ttsService.shutdown();
        }
        super.onDestroy();
    }
}
