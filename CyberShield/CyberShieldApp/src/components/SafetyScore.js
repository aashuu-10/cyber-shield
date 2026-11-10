import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../utils/theme';

const SafetyScore = ({ score = 100 }) => {
  const getScoreColor = () => {
    if (score >= 80) return colors.success;
    if (score >= 50) return colors.warning;
    return colors.accent;
  };

  return (
    <View style={styles.container}>
      <View style={[styles.circle, { borderColor: getScoreColor() }]}>
        <Text style={[styles.scoreText, { color: getScoreColor() }]}>{score}</Text>
        <Text style={styles.labelText}>SAFETY SCORE</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { alignItems: 'center', marginVertical: 15 },
  circle: {
    width: 120, height: 120, borderRadius: 60, borderWidth: 6,
    justifyContent: 'center', alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)',
  },
  scoreText: { fontSize: 36, fontWeight: 'bold' },
  labelText: { fontSize: 10, color: '#8F9BBA', fontWeight: '700', marginTop: 2 },
});

export default SafetyScore;