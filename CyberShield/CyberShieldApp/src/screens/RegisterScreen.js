import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Alert, Keyboard
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import GlowCard from '../components/GlowCard';

const RegisterScreen = ({ navigation }) => {
  const { colors, isDark } = useTheme();
  const { register } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    Keyboard.dismiss();
    setLoading(true);
    const res = await register(name.trim(), email.trim(), password);
    setLoading(false);

    if (!res.success) {
      Alert.alert('Registration Failed', res.message);
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <Text style={styles.shieldLogo}>🛡️</Text>
        <Text style={[styles.title, { color: colors.text }]}>Create Account</Text>
        <Text style={[styles.subtitle, { color: colors.textMuted }]}>
          Join Cyber Shield to secure your device and links
        </Text>
      </View>

      <GlowCard glowColor={colors.secondary}>
        <Text style={[styles.label, { color: colors.text }]}>Full Name</Text>
        <TextInput
          style={[
            styles.input,
            { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }
          ]}
          placeholder="e.g. Rahul Sharma"
          placeholderTextColor={colors.textMuted}
          value={name}
          onChangeText={setName}
        />

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
          placeholder="Create password"
          placeholderTextColor={colors.textMuted}
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <TouchableOpacity
          style={[styles.registerBtn, { backgroundColor: colors.secondary }, loading && { opacity: 0.6 }]}
          onPress={handleRegister}
          disabled={loading}
        >
          <Text style={[styles.registerBtnText, { color: '#FFF' }]}>
            {loading ? '⏳ Creating Account...' : '🚀 Register Now'}
          </Text>
        </TouchableOpacity>
      </GlowCard>

      <View style={styles.footer}>
        <Text style={{ color: colors.textMuted }}>Already have an account? </Text>
        <TouchableOpacity onPress={() => navigation.navigate('Login')}>
          <Text style={{ color: colors.secondary, fontWeight: 'bold' }}>Login Here</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 24, justifyContent: 'center', minHeight: '100%' },
  header: { alignItems: 'center', marginBottom: 24 },
  shieldLogo: { fontSize: 60, marginBottom: 8 },
  title: { fontSize: 26, fontWeight: 'bold' },
  subtitle: { fontSize: 14, marginTop: 4, textAlign: 'center' },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8 },
  input: {
    borderRadius: 12, padding: 14, fontSize: 15, borderWidth: 1, marginBottom: 14,
  },
  registerBtn: {
    padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 10,
  },
  registerBtnText: { fontSize: 16, fontWeight: 'bold' },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: 24 },
});

export default RegisterScreen;