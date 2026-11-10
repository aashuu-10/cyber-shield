import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Alert, Keyboard
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { scanText } from '../services/ThreatDetector';
import { speak, stop } from '../services/TextToSpeech';
import { saveScanRecord } from '../services/HistoryService'; // ADDED: History Service
import GlowCard from '../components/GlowCard';

const SAMPLE_TEXTS = [
  {
    label: '🏦 Bank OTP Scam',
    text: 'Dear customer, your SBI account will be blocked. Click http://sbi-verify.xyz to update KYC immediately. Call 9876543210 for help.'
  },
  {
    label: '🎁 Lottery Scam',
    text: 'Congratulations! You won ₹50,00,000 in the KBC lottery. Send your bank details and ₹5000 processing fee to claim your prize now!'
  },
  {
    label: '✅ Safe Message',
    text: 'Hi Rahul, are we still meeting for lunch at 1pm tomorrow at the office cafeteria? Let me know if the time works for you.'
  }
];

const ScannerScreen = () => {
  const { colors, isDark } = useTheme();
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleScan = () => {
    if (!inputText.trim()) {
      Alert.alert('Empty Input', 'Please paste or type a message to scan.');
      return;
    }
    Keyboard.dismiss();
    setIsScanning(true);
    setTimeout(() => {
      const scanResult = scanText(inputText);
      setResult(scanResult);
      
      // AUTO-SAVE TO HISTORY TAB
      saveScanRecord('TEXT', inputText, scanResult); 
      
      setIsScanning(false);
    }, 500);
  };

  const handleSample = (text) => {
    stop();
    setIsSpeaking(false);
    setInputText(text);
    setResult(null);
  };

  const handleSpeak = () => {
    if (!result) return;
    if (isSpeaking) {
      stop();
      setIsSpeaking(false);
      return;
    }
    const msg = result.isThreat
      ? `Warning! Threat detected. Risk level is ${result.riskLevel}. ${result.threats.map(t => t.description).join('. ')}`
      : 'This message appears to be safe. No threats detected.';
    
    setIsSpeaking(true);
    speak(
      msg,
      () => setIsSpeaking(false),
      () => setIsSpeaking(false)
    );
  };

  const getRiskColor = (level) => {
    if (level === 'HIGH') return colors.accent;
    if (level === 'MEDIUM') return colors.warning;
    return colors.success;
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={styles.content}>
      <Text style={[styles.title, { color: colors.text }]}>🔍 Text Scanner</Text>
      <Text style={[styles.subtitle, { color: colors.textMuted }]}>Paste any suspicious message to check for scams</Text>

      <GlowCard>
        <Text style={[styles.label, { color: colors.text }]}>Paste or type message:</Text>
        <TextInput
          style={[
            styles.input,
            { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }
          ]}
          placeholder="Paste SMS, email, or WhatsApp message here..."
          placeholderTextColor={colors.textMuted}
          multiline
          numberOfLines={5}
          value={inputText}
          onChangeText={setInputText}
          textAlignVertical="top"
        />
        <TouchableOpacity
          style={[styles.scanBtn, { backgroundColor: colors.primary }, isScanning && { opacity: 0.6 }]}
          onPress={handleScan}
          disabled={isScanning}
        >
          <Text style={[styles.scanBtnText, { color: isDark ? '#000' : '#FFF' }]}>
            {isScanning ? '⏳ Scanning...' : '🛡️ Scan for Threats'}
          </Text>
        </TouchableOpacity>
      </GlowCard>

      {result && (
        <GlowCard glowColor={getRiskColor(result.riskLevel)}>
          <View style={styles.resultHeader}>
            <Text style={styles.resultEmoji}>{result.isThreat ? '⚠️' : '✅'}</Text>
            <View style={styles.resultInfo}>
              <Text style={[styles.resultRisk, { color: getRiskColor(result.riskLevel) }]}>
                {result.isThreat ? `${result.riskLevel} RISK` : 'SAFE MESSAGE'}
              </Text>
              <Text style={[styles.resultScore, { color: colors.textMuted }]}>
                Threat Score: {result.score}/100
              </Text>
            </View>

            <TouchableOpacity
              style={[
                styles.speakBtn,
                { backgroundColor: colors.surfaceLight },
                isSpeaking && { backgroundColor: 'rgba(255, 107, 107, 0.25)', borderColor: colors.accent, borderWidth: 1 }
              ]}
              onPress={handleSpeak}
            >
              <Text style={styles.speakBtnText}>{isSpeaking ? '⏹️' : '🔊'}</Text>
            </TouchableOpacity>
          </View>

          {result.isThreat && result.threats.length > 0 && (
            <View style={styles.threatsList}>
              {result.threats.map((threat, i) => (
                <View key={i} style={[styles.threatItem, { backgroundColor: isDark ? 'rgba(255,107,107,0.08)' : '#FEE2E2', borderLeftColor: colors.accent }]}>
                  <Text style={[styles.threatType, { color: colors.accent }]}>⚡ {threat.type}</Text>
                  <Text style={[styles.threatDesc, { color: colors.text }]}>{threat.description}</Text>
                </View>
              ))}
            </View>
          )}

          {!result.isThreat && (
            <Text style={[styles.safeText, { color: colors.success }]}>
              No known scam patterns were found in this message. Stay alert!
            </Text>
          )}
        </GlowCard>
      )}

      <Text style={[styles.sectionTitle, { color: colors.text }]}>Try Sample Messages</Text>
      {SAMPLE_TEXTS.map((sample, i) => (
        <TouchableOpacity key={i} onPress={() => handleSample(sample.text)}>
          <GlowCard glowColor={colors.secondary}>
            <Text style={[styles.sampleLabel, { color: colors.text }]}>{sample.label}</Text>
            <Text style={[styles.sampleText, { color: colors.textMuted }]} numberOfLines={2}>
              {sample.text}
            </Text>
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
  input: { borderRadius: 12, padding: 14, fontSize: 14, height: 110, borderWidth: 1, marginBottom: 14 },
  scanBtn: { padding: 14, borderRadius: 12, alignItems: 'center' },
  scanBtnText: { fontSize: 16, fontWeight: 'bold' },
  sectionTitle: { fontSize: 17, fontWeight: '700', marginTop: 15, marginBottom: 10 },
  sampleLabel: { fontSize: 15, fontWeight: '700', marginBottom: 4 },
  sampleText: { fontSize: 13, lineHeight: 18 },
  resultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  resultEmoji: { fontSize: 36, marginRight: 12 },
  resultInfo: { flex: 1 },
  resultRisk: { fontSize: 18, fontWeight: 'bold' },
  resultScore: { fontSize: 13, marginTop: 2 },
  speakBtn: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
  speakBtnText: { fontSize: 22 },
  threatsList: { marginTop: 6 },
  threatItem: { padding: 12, borderRadius: 10, marginBottom: 8, borderLeftWidth: 3 },
  threatType: { fontSize: 13, fontWeight: '700', marginBottom: 3 },
  threatDesc: { fontSize: 13, lineHeight: 18 },
  safeText: { fontSize: 14, lineHeight: 20 },
});

export default ScannerScreen;