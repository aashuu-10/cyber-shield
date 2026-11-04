package com.cybershield;

import java.util.regex.Pattern;

public class LinkAnalyzer {
    private static final Pattern IP_PATTERN = Pattern.compile("https?://(?:\\d{1,3}\\.){3}\\d{1,3}(?:/.*)?");
    private static final String[] SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly", "goo.gl"};
    private static final String[] SUSPICIOUS_TLDS = {".xyz", ".top", ".tk", ".ml", ".cf", ".gq", ".zip", ".mov", ".work", ".click"};

    public static boolean isSuspiciousUrl(String url) {
        if (url == null || url.trim().isEmpty()) return false;
        String lower = url.toLowerCase();

        if (IP_PATTERN.matcher(lower).find()) return true;

        for (String shortener : SHORTENERS) {
            if (lower.contains(shortener)) return true;
        }

        for (String tld : SUSPICIOUS_TLDS) {
            if (lower.contains(tld + "/") || lower.endsWith(tld)) return true;
        }

        if (lower.contains("paytm") || lower.contains("sbi") || lower.contains("hdfc") || lower.contains("google")) {
            if (lower.contains("-") || lower.contains("secure-login") || lower.contains("verify-account")) {
                return true;
            }
        }

        return false;
    }

    public static String getRiskReason(String url) {
        String lower = url.toLowerCase();
        if (IP_PATTERN.matcher(lower).find()) return "Raw IP Address URL detected (High risk for phishing).";
        for (String s : SHORTENERS) {
            if (lower.contains(s)) return "Shortened URL detected (Hides true destination).";
        }
        for (String tld : SUSPICIOUS_TLDS) {
            if (lower.contains(tld)) return "Suspicious TLD (" + tld + ") often used in scams.";
        }
        return "Typosquatting or brand impersonation detected.";
    }
}
