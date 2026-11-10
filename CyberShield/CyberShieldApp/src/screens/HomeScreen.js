import React from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert
} from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { useTheme } from '../context/ThemeContext';
import { scanText, scanURL } from '../services/ThreatDetector';
import GlowCard from '../components/GlowCard';

const HomeScreen = ({ navigation }) => {
  const { colors, isDark, toggleTheme } = useTheme();

  const handleQuickScan = async () => {
    try {
      let text = '';
      if (Clipboard && typeof Clipboard.getStringAsync === 'function') {
        text = await Clipboard.getStringAsync();
      }
      if (!text || !text.trim()) {
        Alert.alert('Clipboard Empty', 'No text found in clipboard.');
        return;
      }
      const isUrl = text.startsWith('http://') || text.startsWith('https://');
      const result = isUrl ? scanURL(text) : scanText(text);
      Alert.alert(
        result.isThreat ? '⚠️ THREAT DETECTED!' : '✅ SAFE',
        `Risk Level: ${result.riskLevel}\nScore: ${result.score}/100`,
        [{ text: 'OK' }]
      );
    } catch (err) {
      Alert.alert('Scan Error', 'Could not read clipboard text.');
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <View>
          <Text style={[styles.greeting, { color: colors.primary }]}>CYBER SHIELD</Text>
          <Text style={[styles.subGreeting, { color: colors.textMuted }]}>
            AI Scam & Threat Protection
          </Text>
        </View>
        <View style={styles.headerBtns}>
          <TouchableOpacity
            style={[styles.iconBtn, { backgroundColor: colors.surfaceLight }]}
            onPress={toggleTheme}
          >
            <Text style={styles.iconBtnText}>{isDark ? '☀️' : '🌙'}</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.iconBtn, { backgroundColor: colors.surfaceLight }]}
            onPress={() => navigation.navigate('Settings')}
          >
            <Text style={styles.iconBtnText}>⚙️</Text>
          </TouchableOpacity>
        </View>
      </View>

      <GlowCard style={styles.shieldCard} glowColor={colors.primary}>
        <Text style={styles.shieldEmoji}>🛡️</Text>
        <Text style={[styles.shieldTitle, { color: colors.text }]}>System Protected</Text>
        <Text style={[styles.shieldSubtitle, { color: colors.success }]}>
          Real-time monitoring active
        </Text>
        <TouchableOpacity
          style={[styles.quickScanBtn, { backgroundColor: colors.primary }]}
          onPress={handleQuickScan}
        >
          <Text style={[styles.quickScanText, { color: isDark ? '#000' : '#fff' }]}>
            📋 Quick Scan Clipboard
          </Text>
        </TouchableOpacity>
      </GlowCard>

      <Text style={[styles.sectionTitle, { color: colors.text }]}>Security Features</Text>

      <View style={styles.grid}>
        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Scanner')}>
          <GlowCard glowColor={colors.primary} style={styles.gridCard}>
            <Text style={styles.gridEmoji}>🔍</Text>
            <Text style={[styles.gridTitle, { color: colors.text }]}>Text Scanner</Text>
            <Text style={[styles.gridSub, { color: colors.textMuted }]}>Check SMS & Messages</Text>
          </GlowCard>
        </TouchableOpacity>

        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Links')}>
          <GlowCard glowColor={colors.secondary} style={styles.gridCard}>
            <Text style={styles.gridEmoji}>🔗</Text>
            <Text style={[styles.gridTitle, { color: colors.text }]}>Link Checker</Text>
            <Text style={[styles.gridSub, { color: colors.textMuted }]}>Verify URLs & Phishing</Text>
          </GlowCard>
        </TouchableOpacity>

        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Screenshot')}>
          <GlowCard glowColor={colors.accent} style={styles.gridCard}>
            <Text style={styles.gridEmoji}>📸</Text>
            <Text style={[styles.gridTitle, { color: colors.text }]}>Screenshot</Text>
            <Text style={[styles.gridSub, { color: colors.textMuted }]}>Scan Image Text</Text>
          </GlowCard>
        </TouchableOpacity>

        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Guide')}>
          <GlowCard glowColor={colors.success} style={styles.gridCard}>
            <Text style={styles.gridEmoji}>📖</Text>
            <Text style={[styles.gridTitle, { color: colors.text }]}>Safety Guide</Text>
            <Text style={[styles.gridSub, { color: colors.textMuted }]}>Tips & Helpline</Text>
          </GlowCard>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 20 },
  header: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginTop: 10, marginBottom: 20,
  },
  greeting: { fontSize: 24, fontWeight: 'bold', letterSpacing: 1.5 },
  subGreeting: { fontSize: 13, marginTop: 2 },
  headerBtns: { flexDirection: 'row', gap: 10 },
  iconBtn: {
    width: 42, height: 42, borderRadius: 21,
    justifyContent: 'center', alignItems: 'center',
  },
  iconBtnText: { fontSize: 20 },
  shieldCard: { alignItems: 'center', paddingVertical: 24 },
  shieldEmoji: { fontSize: 60, marginBottom: 10 },
  shieldTitle: { fontSize: 22, fontWeight: 'bold' },
  shieldSubtitle: { fontSize: 13, marginTop: 4, marginBottom: 16 },
  quickScanBtn: {
    paddingHorizontal: 20, paddingVertical: 12, borderRadius: 25,
  },
  quickScanText: { fontWeight: 'bold', fontSize: 14 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', marginTop: 10, marginBottom: 14 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -6 },
  gridItem: { width: '50%', paddingHorizontal: 6 },
  gridCard: { padding: 16, alignItems: 'center' },
  gridEmoji: { fontSize: 32, marginBottom: 8 },
  gridTitle: { fontSize: 15, fontWeight: 'bold', textAlign: 'center' },
  gridSub: { fontSize: 11, textAlign: 'center', marginTop: 4 },
});

export default HomeScreen;