package com.cybershield;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

public class AccessibilityShieldService extends AccessibilityService {
    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        AccessibilityNodeInfo rootNode = getRootInActiveWindow();
        if (rootNode != null) {
            scanNode(rootNode);
        }
    }

    private void scanNode(AccessibilityNodeInfo node) {
        if (node == null) return;

        if (node.getText() != null) {
            String text = node.getText().toString();
            if (LinkAnalyzer.isSuspiciousUrl(text)) {
                // Suspicious link detected on screen
            }
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            scanNode(node.getChild(i));
        }
    }

    @Override
    public void onInterrupt() {}
}
