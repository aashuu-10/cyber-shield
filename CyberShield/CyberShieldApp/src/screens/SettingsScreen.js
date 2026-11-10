import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Switch, Alert, Linking
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext'; // ADDED: Auth Context for user info
import GlowCard from '../components/GlowCard';

const SettingsScreen = () => {
  const { isDark, colors, setDarkMode } = useTheme();
  const { user, logout } = useAuth(); // ADDED: Get user and logout function

  const [notifications, setNotifications] = useState(true);
  const [autoScan, setAutoScan] = useState(true);
  const [sound, setSound] = useState(true);

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <Text style={[styles.title, { color: colors.text }]}>⚙️ Settings</Text>
      <Text style={[styles.subtitle, { color: colors.textMuted }]}>
        Customize your Cyber Shield experience
      </Text>

      {/* USER PROFILE CARD - LOGOUT */}
      {user && (
        <GlowCard glowColor={colors.primary}>
          <Text style={[styles.sectionLabel, { color: colors.textMuted }]}>Logged In User</Text>
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: colors.text }}>👤 {user.name}</Text>
          <Text style={{ fontSize: 13, color: colors.textMuted, marginTop: 2 }}>{user.email}</Text>
          <TouchableOpacity
            style={{
              marginTop: 12, backgroundColor: isDark ? 'rgba(255,107,107,0.2)' : '#FEE2E2',
              padding: 10, borderRadius: 8, alignItems: 'center',
            }}
            onPress={logout}
          >
            <Text style={{ color: colors.accent, fontWeight: 'bold' }}>🚪 Logout Account</Text>
          </TouchableOpacity>
        </GlowCard>
      )}

      {/* Appearance */}
      <GlowCard>
        <Text style={[styles.sectionLabel, { color: colors.textMuted }]}>Appearance</Text>

        <View style={[styles.row, { borderBottomColor: colors.border }]}>
          <Text style={styles.rowIcon}>{isDark ? '🌙' : '☀️'}</Text>
          <View style={{ flex: 1 }}>
            <Text style={[styles.rowText, { color: colors.text }]}>Dark Mode</Text>
            <Text style={[styles.rowSub, { color: colors.textMuted }]}>
              {isDark ? 'Dark theme is on' : 'Light theme is on'}
            </Text>
          </View>
          <Switch
            value={isDark}
            onValueChange={setDarkMode}
            trackColor={{ true: colors.primary, false: '#CCC' }}
            thumbColor="#fff"
          />
        </View>

        <View style={styles.themePreviewRow}>
          <TouchableOpacity
            style={[
              styles.themeBox,
              {
                backgroundColor: '#050A1A',
                borderColor: isDark ? colors.primary : 'transparent',
                borderWidth: isDark ? 2 : 1,
              },
            ]}
            onPress={() => setDarkMode(true)}
          >
            <Text style={{ color: '#00F5D4', fontWeight: '700' }}>🌙 Dark</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.themeBox,
              {
                backgroundColor: '#F4F7FB',
                borderColor: !isDark ? colors.primary : 'rgba(0,0,0,0.1)',
                borderWidth: !isDark ? 2 : 1,
              },
            ]}
            onPress={() => setDarkMode(false)}
          >
            <Text style={{ color: '#0D1B2A', fontWeight: '700' }}>☀️ Light</Text>
          </TouchableOpacity>
        </View>
      </GlowCard>

      {/* General */}
      <GlowCard>
        <Text style={[styles.sectionLabel, { color: colors.textMuted }]}>General</Text>

        <View style={[styles.row, { borderBottomColor: colors.border }]}>
          <Text style={styles.rowIcon}>🔔</Text>
          <Text style={[styles.rowText, { color: colors.text }]}>Notifications</Text>
          <Switch value={notifications} onValueChange={setNotifications} trackColor={{ true: colors.primary, false: '#CCC' }} thumbColor="#fff" />
        </View>

        <View style={[styles.row, { borderBottomColor: colors.border }]}>
          <Text style={styles.rowIcon}>🔍</Text>
          <Text style={[styles.rowText, { color: colors.text }]}>Auto-scan Clipboard</Text>
          <Switch value={autoScan} onValueChange={setAutoScan} trackColor={{ true: colors.primary, false: '#CCC' }} thumbColor="#fff" />
        </View>

        <View style={[styles.row, { borderBottomColor: colors.border }]}>
          <Text style={styles.rowIcon}>🔊</Text>
          <Text style={[styles.rowText, { color: colors.text }]}>Sound Alerts</Text>
          <Switch value={sound} onValueChange={setSound} trackColor={{ true: colors.primary, false: '#CCC' }} thumbColor="#fff" />
        </View>
      </GlowCard>

      {/* About */}
      <GlowCard glowColor={colors.secondary}>
        <Text style={[styles.sectionLabel, { color: colors.textMuted }]}>About</Text>
        <View style={[styles.aboutRow, { borderBottomColor: colors.border }]}>
          <Text style={[styles.aboutLabel, { color: colors.textMuted }]}>App Name</Text>
          <Text style={[styles.aboutValue, { color: colors.text }]}>Cyber Shield</Text>
        </View>
        <View style={[styles.aboutRow, { borderBottomColor: colors.border }]}>
          <Text style={[styles.aboutLabel, { color: colors.textMuted }]}>Version</Text>
          <Text style={[styles.aboutValue, { color: colors.text }]}>1.0.0</Text>
        </View>
        <View style={[styles.aboutRow, { borderBottomColor: colors.border }]}>
          <Text style={[styles.aboutLabel, { color: colors.textMuted }]}>Developer</Text>
          <Text style={[styles.aboutValue, { color: colors.text }]}>Cyphra Codes</Text>
        </View>
      </GlowCard>

      {/* Support */}
      <GlowCard glowColor={colors.accent}>
        <Text style={[styles.sectionLabel, { color: colors.textMuted }]}>Support</Text>
        <TouchableOpacity
          style={[styles.linkBtn, { backgroundColor: colors.surfaceLight }]}
          onPress={() => Linking.openURL('https://cybercrime.gov.in')}
        >
          <Text style={[styles.linkBtnText, { color: colors.text }]}>🌐 Report Cyber Crime</Text>
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
  sectionLabel: { fontSize: 13, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1 },
  rowIcon: { fontSize: 22, marginRight: 12 },
  rowText: { flex: 1, fontSize: 16 },
  rowSub: { fontSize: 12, marginTop: 2 },
  themePreviewRow: { flexDirection: 'row', gap: 12, marginTop: 14 },
  themeBox: { flex: 1, padding: 16, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  aboutRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1 },
  aboutLabel: { fontSize: 15 },
  aboutValue: { fontSize: 15, fontWeight: '600' },
  linkBtn: { padding: 14, borderRadius: 10, marginBottom: 10, alignItems: 'center' },
  linkBtnText: { fontSize: 15, fontWeight: '600' },
});

export default SettingsScreen;