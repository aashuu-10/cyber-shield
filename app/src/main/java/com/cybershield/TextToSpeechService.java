package com.cybershield;

import android.content.Context;
import android.speech.tts.TextToSpeech;
import java.util.Locale;

public class TextToSpeechService implements TextToSpeech.OnInitListener {
    private TextToSpeech tts;
    private boolean isInitialized = false;

    public TextToSpeechService(Context context) {
        tts = new TextToSpeech(context.getApplicationContext(), this);
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            int result = tts.setLanguage(Locale.US);
            if (result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED) {
                isInitialized = true;
            }
        }
    }

    public void speak(String text) {
        if (isInitialized && tts != null) {
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "CyberShieldTTS");
        }
    }

    public void shutdown() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
        }
    }
}
