package com.cybershield;

import java.util.regex.Pattern;

public class ScamPatternDetector {
    private static final Pattern AADHAAR_PATTERN = Pattern.compile("\\b[2-9][0-9]{3}\\s[0-9]{4}\\s[0-9]{4}\\b");
    private static final Pattern PAN_PATTERN = Pattern.compile("[A-Z]{5}[0-9]{4}[A-Z]{1}");
    private static final Pattern CREDIT_CARD_PATTERN = Pattern.compile("\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\\b");

    private static final String[] SCAM_KEYWORDS = {
            "lottery winner", "account blocked", "kyc update", "urgent verification",
            "claim reward", "congratulations won", "share otp", "enter pin", "bank account suspended"
    };

    public static boolean containsScamPattern(String text) {
        if (text == null) return false;
        String lower = text.toLowerCase();

        for (String keyword : SCAM_KEYWORDS) {
            if (lower.contains(keyword)) return true;
        }

        return AADHAAR_PATTERN.matcher(text).find() ||
               PAN_PATTERN.matcher(text).find() ||
               CREDIT_CARD_PATTERN.matcher(text).find();
    }

    public static String getDetectedThreatType(String text) {
        if (text == null) return "Unknown";
        if (AADHAAR_PATTERN.matcher(text).find()) return "Aadhaar Card Number Exposed";
        if (PAN_PATTERN.matcher(text).find()) return "PAN Card Number Exposed";
        if (CREDIT_CARD_PATTERN.matcher(text).find()) return "Credit/Debit Card Data Exposed";
        return "Phishing / Scam Text Detected";
    }
}
