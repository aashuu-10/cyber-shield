import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Alert, Keyboard
} from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { useTheme } from '../context/ThemeContext';
import { scanURL } from '../services/ThreatDetector';
import { speak, stop } from '../services/TextToSpeech';
import GlowCard from '../components/GlowCard';

const SAMPLE_URLS = [
  { label: '🎣 Phishing Link', url: 'http://sbi-verify.xyz/login' },
  { label: '💰 Scam Link', url: 'https://free-iphone-winner.com/claim' },
  { label: '✅ Safe Link', url: 'https://www.google.com' },
];

const LinkCheckerScreen = () => {
  const { colors, isDark } = useTheme();
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);

  const handlePaste = async () => {
    try {
      const text = await Clipboard.getStringAsync();
      if (text) {
        setUrl(text);
        setResult(null);
      } else {
        Alert.alert('Clipboard Empty', 'No link found in clipboard.');
      }
    } catch (e) {
      Alert.alert('Paste Error', 'Could not read clipboard.');
    }
  };

  const handleScan = () => {
    if (!url.trim()) {
      Alert.alert('Empty', 'Please enter or paste a URL.');
      return;
    }
    Keyboard.dismiss();
    setIsScanning(true);
    setTimeout(() => {
      const scanResult = scanURL(url);
      setResult(scanResult);
      setIsScanning(false);
    }, 500);
  };

  const handleSpeak = () => {
    if (!result) return;
    stop();
    const msg = result.isThreat
      ? `Danger! This link is ${result.riskLevel} risk. ${result.threats.map(t => t.description).join('. ')}`
      : 'This link appears safe.';
    speak(msg);
  };

  const getRiskColor = (level) => {
    if (level === 'HIGH') return colors.accent;
    if (level === 'MEDIUM') return colors.warning;
    return colors.success;
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={styles.content}>
      <Text style={[styles.title, { color: colors.text }]}>🔗 Link Checker</Text>
      <Text style={[styles.subtitle, { color: colors.textMuted }]}>Paste any URL to verify if it is safe</Text>

      <GlowCard>
        <Text style={[styles.label, { color: colors.text }]}>Enter URL:</Text>
        <View style={styles.inputRow}>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: colors.inputBg,
                color: colors.text,
                borderColor: colors.border,
              }
            ]}
            placeholder="https://example.com"
            placeholderTextColor={colors.textMuted}
            value={url}
            onChangeText={setUrl}
            autoCapitalize="none"
            keyboardType="url"
          />
          <TouchableOpacity style={[styles.pasteBtn, { backgroundColor: colors.surfaceLight }]} onPress={handlePaste}>
            <Text style={styles.pasteBtnText}>📋</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity
          style={[styles.scanBtn, { backgroundColor: colors.primary }, isScanning && { opacity: 0.6 }]}
          onPress={handleScan}
          disabled={isScanning}
        >
          <Text style={[styles.scanBtnText, { color: isDark ? '#000' : '#FFF' }]}>
            {isScanning ? '⏳ Checking...' : '🛡️ Check Link'}
          </Text>
        </TouchableOpacity>
      </GlowCard>

      {/* RESULT CARDS */}
      {result && (
        <GlowCard glowColor={getRiskColor(result.riskLevel)}>
          <View style={styles.resultHeader}>
            <Text style={styles.resultEmoji}>{result.isThreat ? '🚨' : '✅'}</Text>
            <View style={styles.resultInfo}>
              <Text style={[styles.resultRisk, { color: getRiskColor(result.riskLevel) }]}>
                {result.isThreat ? `${result.riskLevel} RISK` : 'SAFE LINK'}
              </Text>
              <Text style={[styles.resultScore, { color: colors.textMuted }]}>Score: {result.score}/100</Text>
            </View>
            <TouchableOpacity style={[styles.speakBtn, { backgroundColor: colors.surfaceLight }]} onPress={handleSpeak}>
              <Text style={styles.speakBtnText}>🔊</Text>
            </TouchableOpacity>
          </View>
          {result.isThreat && result.threats.length > 0 && (
            <View style={styles.threatsList}>
              {result.threats.map((t, i) => (
                <View key={i} style={[styles.threatItem, { backgroundColor: isDark ? 'rgba(255,107,107,0.08)' : '#FEE2E2', borderLeftColor: colors.accent }]}>
                  <Text style={[styles.threatType, { color: colors.accent }]}>🔗 {t.type}</Text>
                  <Text style={[styles.threatDesc, { color: colors.text }]}>{t.description}</Text>
                </View>
              ))}
            </View>
          )}
          {!result.isThreat && (
            <Text style={[styles.safeText, { color: colors.success }]}>This URL does not match any known phishing or scam patterns.</Text>
          )}
        </GlowCard>
      )}

      {/* Sample Links */}
      <Text style={[styles.sectionTitle, { color: colors.text }]}>Try Sample Links</Text>
      {SAMPLE_URLS.map((s, i) => (
        <TouchableOpacity key={i} onPress={() => { setUrl(s.url); setResult(null); }}>
          <GlowCard glowColor={colors.secondary}>
            <Text style={[styles.sampleLabel, { color: colors.text }]}>{s.label}</Text>
            <Text style={[styles.sampleUrl, { color: colors.primary }]} numberOfLines={1}>{s.url}</Text>
          </GlowCard>
        </TouchableOpacity>
      ))}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 20 },
  title: { fontSize: 26, fontWeight: 'bold', marginTop: 10 },
  subtitle: { fontSize: 14, marginBottom: 20, marginTop: 4 },
  label: { fontSize: 15, fontWeight: '600', marginBottom: 8 },
  inputRow: { flexDirection: 'row', marginBottom: 14 },
  input: {
    flex: 1, borderRadius: 12, padding: 14, fontSize: 14,
    borderWidth: 1, marginRight: 8,
  },
  pasteBtn: {
    borderRadius: 12, width: 50, justifyContent: 'center', alignItems: 'center',
  },
  pasteBtnText: { fontSize: 22 },
  scanBtn: { padding: 14, borderRadius: 12, alignItems: 'center' },
  scanBtnText: { fontSize: 16, fontWeight: 'bold' },
  sectionTitle: { fontSize: 17, fontWeight: '700', marginTop: 15, marginBottom: 10 },
  sampleLabel: { fontSize: 15, fontWeight: '700', marginBottom: 4 },
  sampleUrl: { fontSize: 13 },
  resultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  resultEmoji: { fontSize: 36, marginRight: 12 },
  resultInfo: { flex: 1 },
  resultRisk: { fontSize: 18, fontWeight: 'bold' },
  resultScore: { fontSize: 13, marginTop: 2 },
  speakBtn: {
    width: 44, height: 44, borderRadius: 22,
    justifyContent: 'center', alignItems: 'center',
  },
  speakBtnText: { fontSize: 22 },
  threatsList: { marginTop: 6 },
  threatItem: {
    padding: 12, borderRadius: 10, marginBottom: 8,
    borderLeftWidth: 3,
  },
  threatType: { fontSize: 13, fontWeight: '700', marginBottom: 3 },
  threatDesc: { fontSize: 13, lineHeight: 18 },
  safeText: { fontSize: 14, lineHeight: 20 },
});

export default LinkCheckerScreen;