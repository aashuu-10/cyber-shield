import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Alert, Keyboard
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import GlowCard from '../components/GlowCard';

const LoginScreen = ({ navigation }) => {
  const { colors, isDark } = useTheme();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    Keyboard.dismiss();
    setLoading(true);
    const res = await login(email.trim(), password);
    setLoading(false);

    if (!res.success) {
      Alert.alert('Login Failed', res.message);
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <Text style={styles.shieldLogo}>🛡️</Text>
        <Text style={[styles.title, { color: colors.text }]}>CYBER SHIELD</Text>
        <Text style={[styles.subtitle, { color: colors.textMuted }]}>
          Sign in to protect your digital identity
        </Text>
      </View>

      <GlowCard>
        <Text style={[styles.label, { color: colors.text }]}>Email Address</Text>
        <TextInput
          style={[
            styles.input,
            { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }
          ]}
          placeholder="name@example.com"
          placeholderTextColor={colors.textMuted}
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />

        <Text style={[styles.label, { color: colors.text }]}>Password</Text>
        <TextInput
          style={[
            styles.input,
            { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }
          ]}
          placeholder="Enter password"
          placeholderTextColor={colors.textMuted}
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <TouchableOpacity
          style={[styles.loginBtn, { backgroundColor: colors.primary }, loading && { opacity: 0.6 }]}
          onPress={handleLogin}
          disabled={loading}
        >
          <Text style={[styles.loginBtnText, { color: isDark ? '#000' : '#FFF' }]}>
            {loading ? '⏳ Signing In...' : '🔐 Login'}
          </Text>
        </TouchableOpacity>
      </GlowCard>

      <View style={styles.footer}>
        <Text style={{ color: colors.textMuted }}>Don't have an account? </Text>
        <TouchableOpacity onPress={() => navigation.navigate('Register')}>
          <Text style={{ color: colors.primary, fontWeight: 'bold' }}>Register Here</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 24, justifyContent: 'center', minHeight: '100%' },
  header: { alignItems: 'center', marginBottom: 30 },
  shieldLogo: { fontSize: 70, marginBottom: 10 },
  title: { fontSize: 28, fontWeight: 'bold', letterSpacing: 2 },
  subtitle: { fontSize: 14, marginTop: 6, textAlign: 'center' },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8 },
  input: {
    borderRadius: 12, padding: 14, fontSize: 15, borderWidth: 1, marginBottom: 16,
  },
  loginBtn: {
    padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 10,
  },
  loginBtnText: { fontSize: 16, fontWeight: 'bold' },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: 24 },
});

export default LoginScreen;