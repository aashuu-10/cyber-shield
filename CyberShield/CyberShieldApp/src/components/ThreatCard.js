import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { colors } from '../utils/theme';

const ThreatCard = ({ threat, onSpeak }) => {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>⚠️ {threat?.type || 'THREAT DETECTED'}</Text>
        {onSpeak && (
          <TouchableOpacity onPress={onSpeak} style={styles.speakBtn}>
            <Text style={{ fontSize: 18 }}>🔊</Text>
          </TouchableOpacity>
        )}
      </View>
      <Text style={styles.desc}>{threat?.description || 'Suspicious pattern identified.'}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(255, 107, 107, 0.1)',
    borderRadius: 12, padding: 16, marginBottom: 12,
    borderLeftWidth: 4, borderLeftColor: colors.accent,
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  title: { color: colors.accent, fontWeight: 'bold', fontSize: 15 },
  desc: { color: colors.text, fontSize: 13, lineHeight: 18 },
  speakBtn: { padding: 4 },
});

export default ThreatCard;