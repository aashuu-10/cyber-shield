import React, { useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet,
  ScrollView, Linking, Alert
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { speak, stop } from '../services/TextToSpeech';
import GlowCard from '../components/GlowCard';

const CATEGORIES = [
  {
    emoji: '🏦', title: 'Banking & UPI Safety',
    tips: [
      'Never share OTP, PIN, or CVV with anyone — not even bank staff.',
      'Always verify UPI payment requests before approving.',
      'Do not click links in SMS claiming your account is blocked.',
      'Use official bank apps only — never download from random links.',
      'Enable transaction alerts and set daily limits on UPI.',
    ]
  },
  {
    emoji: '📱', title: 'Phone & SMS Scams',
    tips: [
      'Do not answer calls from unknown numbers asking for personal info.',
      'Block numbers that send repeated spam or lottery messages.',
      'Never call back missed calls from unfamiliar international numbers.',
      'Verify caller identity by calling the official number yourself.',
      'Install Truecaller or similar apps to identify spam callers.',
    ]
  },
  {
    emoji: '🌐', title: 'Online & Social Media',
    tips: [
      'Check URLs carefully — scammers use lookalike domains.',
      'Never log in to accounts through links sent in messages.',
      'Enable Two-Factor Authentication (2FA) on all accounts.',
      'Be suspicious of "too good to be true" offers and giveaways.',
      'Do not share personal documents (Aadhaar, PAN) on social media.',
    ]
  },
  {
    emoji: '💼', title: 'Job & Investment Scams',
    tips: [
      'Legitimate jobs never ask you to pay money upfront.',
      'Verify company details on official websites before applying.',
      'Avoid "guaranteed returns" investment schemes — they are fraud.',
      'Research before investing in crypto or trading platforms.',
      'Report fake job offers to the cybercrime portal.',
    ]
  }
];

const EMERGENCY = [
  { name: 'Cyber Crime Helpline', number: '1930', emoji: '🚔' },
  { name: 'Police Emergency', number: '100', emoji: '👮' },
  { name: 'Women Helpline', number: '1091', emoji: '🛡️' },
  { name: 'RBI Complaint', number: '14448', emoji: '🏦' },
];

const PrecautionsScreen = () => {
  const { colors, isDark } = useTheme();
  const [expanded, setExpanded] = useState(null);
  const [speakingIndex, setSpeakingIndex] = useState(null);

  const handleCall = (number) => {
    Alert.alert(`Call ${number}?`, '', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Call', onPress: () => Linking.openURL(`tel:${number}`) }
    ]);
  };

  const handleSpeakCategory = (index, cat) => {
    if (speakingIndex === index) {
      stop();
      setSpeakingIndex(null);
      return;
    }
    stop();
    setSpeakingIndex(index);
    const textToRead = `${cat.title}. ${cat.tips.join('. ')}`;
    speak(
      textToRead,
      () => setSpeakingIndex(null),
      () => setSpeakingIndex(null)
    );
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={styles.content}>
      <Text style={[styles.title, { color: colors.text }]}>📖 Safety Guide</Text>
      <Text style={[styles.subtitle, { color: colors.textMuted }]}>Learn how to protect yourself from cyber scams</Text>

      {CATEGORIES.map((cat, i) => (
        <TouchableOpacity key={i} onPress={() => setExpanded(expanded === i ? null : i)}>
          <GlowCard glowColor={colors.secondary}>
            <View style={styles.catHeader}>
              <Text style={styles.catEmoji}>{cat.emoji}</Text>
              <Text style={[styles.catTitle, { color: colors.text }]}>{cat.title}</Text>
              <Text style={[styles.arrow, { color: colors.textMuted }]}>{expanded === i ? '▲' : '▼'}</Text>
            </View>
            {expanded === i && (
              <View style={[styles.tipsContainer, { borderTopColor: colors.border }]}>
                {cat.tips.map((tip, j) => (
                  <View key={j} style={styles.tipRow}>
                    <Text style={[styles.tipDot, { color: colors.primary }]}>•</Text>
                    <Text style={[styles.tipText, { color: colors.text }]}>{tip}</Text>
                  </View>
                ))}
                
                <TouchableOpacity
                  style={[
                    styles.readBtn,
                    { backgroundColor: isDark ? 'rgba(123,97,255,0.2)' : '#EDE9FE' },
                    speakingIndex === i && { backgroundColor: isDark ? 'rgba(255,107,107,0.25)' : '#FEE2E2', borderWidth: 1, borderColor: colors.accent }
                  ]}
                  onPress={() => handleSpeakCategory(i, cat)}
                >
                  <Text style={[
                    styles.readBtnText,
                    { color: colors.secondary },
                    speakingIndex === i && { color: colors.accent }
                  ]}>
                    {speakingIndex === i ? '⏹️ Stop Reading' : '🔊 Read Aloud'}
                  </Text>
                </TouchableOpacity>
              </View>
            )}
          </GlowCard>
        </TouchableOpacity>
      ))}

      <Text style={[styles.sectionTitle, { color: colors.text }]}>🚨 Emergency Contacts</Text>
      <GlowCard glowColor={colors.accent}>
        {EMERGENCY.map((e, i) => (
          <TouchableOpacity key={i} style={[styles.emRow, { borderBottomColor: colors.border }]} onPress={() => handleCall(e.number)}>
            <Text style={styles.emEmoji}>{e.emoji}</Text>
            <View style={styles.emInfo}>
              <Text style={[styles.emName, { color: colors.text }]}>{e.name}</Text>
              <Text style={[styles.emNumber, { color: colors.primary }]}>{e.number}</Text>
            </View>
            <Text style={styles.callIcon}>📞</Text>
          </TouchableOpacity>
        ))}
        <TouchableOpacity
          style={[styles.websiteBtn, { backgroundColor: colors.primary }]}
          onPress={() => Linking.openURL('https://cybercrime.gov.in')}
        >
          <Text style={[styles.websiteBtnText, { color: isDark ? '#000' : '#FFF' }]}>🌐 cybercrime.gov.in</Text>
        </TouchableOpacity>
      </GlowCard>
      <View style={{ height: 40 }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 20 },
  title: { fontSize: 26, fontWeight: 'bold', marginTop: 10 },
  subtitle: { fontSize: 14, marginBottom: 20, marginTop: 4 },
  catHeader: { flexDirection: 'row', alignItems: 'center' },
  catEmoji: { fontSize: 28, marginRight: 12 },
  catTitle: { flex: 1, fontSize: 17, fontWeight: '700' },
  arrow: { fontSize: 14 },
  tipsContainer: { marginTop: 14, paddingTop: 14, borderTopWidth: 1 },
  tipRow: { flexDirection: 'row', marginBottom: 10 },
  tipDot: { fontSize: 16, marginRight: 8, marginTop: 1 },
  tipText: { flex: 1, fontSize: 14, lineHeight: 20 },
  readBtn: {
    marginTop: 10, padding: 12, borderRadius: 10, alignItems: 'center',
  },
  readBtnText: { fontWeight: '700', fontSize: 14 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', marginTop: 10, marginBottom: 12 },
  emRow: {
    flexDirection: 'row', alignItems: 'center',
    paddingVertical: 12, borderBottomWidth: 1,
  },
  emEmoji: { fontSize: 28, marginRight: 12 },
  emInfo: { flex: 1 },
  emName: { fontSize: 15, fontWeight: '600' },
  emNumber: { fontSize: 18, fontWeight: 'bold', marginTop: 2 },
  callIcon: { fontSize: 24 },
  websiteBtn: {
    marginTop: 14, padding: 14, borderRadius: 12, alignItems: 'center',
  },
  websiteBtnText: { fontSize: 16, fontWeight: 'bold' },
});

export default PrecautionsScreen;