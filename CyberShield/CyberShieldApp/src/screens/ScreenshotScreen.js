import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Alert, Image, Keyboard, ActivityIndicator
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useTheme } from '../context/ThemeContext';
import { scanText } from '../services/ThreatDetector';
import { speak, stop } from '../services/TextToSpeech';
import GlowCard from '../components/GlowCard';

const SAMPLE_SCREENSHOTS = [
  {
    title: '💬 Fake Bank Alert Screenshot',
    text: 'SBI ALERT: Dear user your account 4912 has been suspended due to pending KYC. Click http://sbi-verify.xyz to update now.'
  },
  {
    title: '🎁 Telegram Task Scam Screenshot',
    text: 'Task Completed! Earn ₹5000 daily by liking YouTube videos. Deposit ₹1000 processing fee to release payment.'
  },
  {
    title: '✅ Genuine Payment Receipt',
    text: 'Transaction Successful. Paid ₹250 to Corner Cafe via UPI Ref 401928301. Transaction date 12 Oct 2024.'
  }
];

const ScreenshotScreen = () => {
  const { colors, isDark } = useTheme();
  const [image, setImage] = useState(null);
  const [base64Data, setBase64Data] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [result, setResult] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isScanning, setIsScanning] = useState(false);

  const performScan = (textToScan) => {
    Keyboard.dismiss();
    setIsScanning(true);
    setTimeout(() => {
      const scanResult = scanText(textToScan);
      setResult(scanResult);
      setIsScanning(false);
    }, 400);
  };

  const pickImage = async (useCamera) => {
    try {
      let permission;
      if (useCamera) {
        permission = await ImagePicker.requestCameraPermissionsAsync();
      } else {
        permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      }

      if (!permission.granted) {
        Alert.alert('Permission Needed', 'Please allow camera/gallery access in phone settings.');
        return;
      }

      const options = {
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 0.2, 
        base64: true,
      };

      const res = useCamera
        ? await ImagePicker.launchCameraAsync(options)
        : await ImagePicker.launchImageLibraryAsync(options);

      if (!res.canceled && res.assets && res.assets.length > 0) {
        const asset = res.assets[0];
        setImage(asset.uri);
        setBase64Data(asset.base64);
        setResult(null);
      }
    } catch (error) {
      Alert.alert('Error', 'Could not access camera or gallery.');
    }
  };

  const handleDirectImageScan = async () => {
    if (!image || !base64Data) {
      Alert.alert('No Image', 'Please pick a screenshot from Gallery or Camera first.');
      return;
    }

    setIsExtracting(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('base64Image', `data:image/jpeg;base64,${base64Data}`);
      formData.append('apikey', 'K88383838288957');
      formData.append('language', 'eng');
      formData.append('OCREngine', '2');
      formData.append('scale', 'true');

      const response = await fetch('https://api.ocr.space/parse/image', {
        method: 'POST',
        body: formData,
      });

      const json = await response.json();
      setIsExtracting(false);

      if (json && json.ParsedResults && json.ParsedResults.length > 0) {
        const parsed = json.ParsedResults[0].ParsedText || '';
        const cleanText = parsed.replace(/\r\n/g, ' ').replace(/\n/g, ' ').trim();

        if (cleanText) {
          setExtractedText(cleanText);
          performScan(cleanText);
        } else {
          Alert.alert('No Text Found', 'Could not find clear text in this screenshot.');
        }
      } else {
        Alert.alert('OCR Service Busy', 'Please type or edit the text manually into the box below.');
      }
    } catch (err) {
      setIsExtracting(false);
      Alert.alert('Scan Failed', 'Network timeout. You can manually type text into the box below.');
    }
  };

  const handleManualScan = () => {
    if (!extractedText.trim()) {
      Alert.alert('Empty Input', 'Type or paste message text into the box.');
      return;
    }
    performScan(extractedText.trim());
  };

  const handleSampleSelect = (sample) => {
    setImage(null);
    setBase64Data(null);
    setExtractedText(sample.text);
    performScan(sample.text);
  };

  const handleSpeak = () => {
    if (!result) return;
    stop();
    const msg = result.isThreat
      ? `Warning! ${result.riskLevel} risk detected in screenshot. ${result.threats.map(t => t.description).join('. ')}`
      : 'This screenshot text appears safe.';
    speak(msg);
  };

  const getRiskColor = (level) => {
    if (level === 'HIGH') return colors.accent;
    if (level === 'MEDIUM') return colors.warning;
    return colors.success;
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={styles.content}>
      <Text style={[styles.title, { color: colors.text }]}>📸 Screenshot Scanner</Text>
      <Text style={[styles.subtitle, { color: colors.textMuted }]}>Extract text from screenshots and detect scams instantly</Text>

      {/* 1. Image Upload & OCR Button */}
      <GlowCard>
        <Text style={[styles.label, { color: colors.text }]}>1. Select Screenshot:</Text>
        <View style={styles.btnRow}>
          <TouchableOpacity style={[styles.pickBtn, { backgroundColor: colors.surfaceLight, borderColor: colors.border }]} onPress={() => pickImage(false)}>
            <Text style={[styles.pickBtnText, { color: colors.text }]}>🖼️ Gallery</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.pickBtn, { backgroundColor: colors.surfaceLight, borderColor: colors.border }]} onPress={() => pickImage(true)}>
            <Text style={[styles.pickBtnText, { color: colors.text }]}>📷 Camera</Text>
          </TouchableOpacity>
        </View>

        {image && (
          <View style={styles.previewContainer}>
            <Image source={{ uri: image }} style={[styles.preview, { backgroundColor: colors.surface }]} resizeMode="contain" />
            
            <TouchableOpacity
              style={[styles.directScanBtn, { backgroundColor: colors.primary }, isExtracting && { opacity: 0.7 }]}
              onPress={handleDirectImageScan}
              disabled={isExtracting}
            >
              {isExtracting ? (
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <ActivityIndicator color={isDark ? '#000' : '#FFF'} style={{ marginRight: 8 }} />
                  <Text style={[styles.directScanText, { color: isDark ? '#000' : '#FFF' }]}>Scanning Image Pixels...</Text>
                </View>
              ) : (
                <Text style={[styles.directScanText, { color: isDark ? '#000' : '#FFF' }]}>⚡ Scan Text From Image</Text>
              )}
            </TouchableOpacity>
          </View>
        )}
      </GlowCard>

      {/* 2. Extracted Text Area */}
      <GlowCard>
        <Text style={[styles.label, { color: colors.text }]}>2. Extracted Screenshot Text:</Text>
        <TextInput
          style={[
            styles.input,
            {
              backgroundColor: colors.inputBg,
              color: colors.text,
              borderColor: colors.border,
            }
          ]}
          placeholder="Text extracted from image will appear here..."
          placeholderTextColor={colors.textMuted}
          multiline
          numberOfLines={4}
          value={extractedText}
          onChangeText={setExtractedText}
          textAlignVertical="top"
        />
        <TouchableOpacity
          style={[styles.scanBtn, { backgroundColor: colors.surfaceLight }, isScanning && { opacity: 0.6 }]}
          onPress={handleManualScan}
          disabled={isScanning}
        >
          <Text style={[styles.scanBtnText, { color: colors.text }]}>
            {isScanning ? '⏳ Analyzing...' : '🛡️ Scan Text Box'}
          </Text>
        </TouchableOpacity>
      </GlowCard>

      {/* 3. RESULT DISPLAYED DIRECTLY BELOW */}
      {result && (
        <GlowCard glowColor={getRiskColor(result.riskLevel)}>
          <View style={styles.resultHeader}>
            <Text style={styles.resultEmoji}>{result.isThreat ? '⚠️' : '✅'}</Text>
            <View style={styles.resultInfo}>
              <Text style={[styles.resultRisk, { color: getRiskColor(result.riskLevel) }]}>
                {result.isThreat ? `${result.riskLevel} RISK DETECTED` : 'SAFE SCREENSHOT'}
              </Text>
              <Text style={[styles.resultScore, { color: colors.textMuted }]}>Threat Score: {result.score}/100</Text>
            </View>
            <TouchableOpacity style={[styles.speakBtn, { backgroundColor: colors.surfaceLight }]} onPress={handleSpeak}>
              <Text style={styles.speakBtnText}>🔊</Text>
            </TouchableOpacity>
          </View>

          {result.isThreat && result.threats.length > 0 && (
            <View style={styles.threatsList}>
              {result.threats.map((t, i) => (
                <View key={i} style={[styles.threatItem, { backgroundColor: isDark ? 'rgba(255,107,107,0.08)' : '#FEE2E2', borderLeftColor: colors.accent }]}>
                  <Text style={[styles.threatType, { color: colors.accent }]}>⚡ {t.type}</Text>
                  <Text style={[styles.threatDesc, { color: colors.text }]}>{t.description}</Text>
                </View>
              ))}
            </View>
          )}

          {!result.isThreat && (
            <Text style={[styles.safeText, { color: colors.success }]}>No known scam or phishing patterns found in this screenshot.</Text>
          )}
        </GlowCard>
      )}

      {/* Try Sample Screenshots */}
      <Text style={[styles.sectionTitle, { color: colors.text }]}>Try Sample Screenshots</Text>
      {SAMPLE_SCREENSHOTS.map((sample, i) => (
        <TouchableOpacity key={i} onPress={() => handleSampleSelect(sample)}>
          <GlowCard glowColor={colors.secondary}>
            <Text style={[styles.sampleTitle, { color: colors.text }]}>{sample.title}</Text>
            <Text style={[styles.sampleText, { color: colors.textMuted }]} numberOfLines={2}>{sample.text}</Text>
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
  label: { fontSize: 15, fontWeight: '600', marginBottom: 10 },
  btnRow: { flexDirection: 'row', gap: 12 },
  pickBtn: {
    flex: 1, padding: 14, borderRadius: 12, alignItems: 'center', borderWidth: 1,
  },
  pickBtnText: { fontSize: 15, fontWeight: '600' },
  previewContainer: { marginTop: 14, alignItems: 'center' },
  preview: { width: '100%', height: 180, borderRadius: 12 },
  directScanBtn: {
    width: '100%', padding: 14, borderRadius: 12, alignItems: 'center', marginTop: 12,
  },
  directScanText: { fontSize: 14, fontWeight: 'bold' },
  input: {
    borderRadius: 12, padding: 14, fontSize: 14, height: 90, borderWidth: 1, marginBottom: 14,
  },
  scanBtn: { padding: 14, borderRadius: 12, alignItems: 'center' },
  scanBtnText: { fontSize: 15, fontWeight: 'bold' },
  sectionTitle: { fontSize: 17, fontWeight: '700', marginTop: 15, marginBottom: 10 },
  sampleTitle: { fontSize: 15, fontWeight: '700', marginBottom: 4 },
  sampleText: { fontSize: 13, lineHeight: 18 },
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
    padding: 12, borderRadius: 10, marginBottom: 8, borderLeftWidth: 3,
  },
  threatType: { fontSize: 13, fontWeight: '700', marginBottom: 3 },
  threatDesc: { fontSize: 13, lineHeight: 18 },
  safeText: { fontSize: 14, lineHeight: 20 },
});

export default ScreenshotScreen;