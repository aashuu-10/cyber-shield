import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { useTheme } from '../context/ThemeContext';

const GlowCard = ({ children, style, onPress, glowColor }) => {
  const { colors, isDark } = useTheme();
  const borderGlow = glowColor || colors.primary;

  const content = (
    <View
      style={[
        styles.card,
        {
          backgroundColor: colors.card,
          borderColor: isDark ? borderGlow : colors.border,
          borderWidth: isDark ? 1 : 1,
          shadowColor: isDark ? borderGlow : '#000',
          shadowOpacity: isDark ? 0.25 : 0.08,
          shadowRadius: isDark ? 8 : 4,
          shadowOffset: { width: 0, height: 2 },
          elevation: isDark ? 4 : 2,
        },
        style,
      ]}
    >
      {children}
    </View>
  );

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.8}>
        {content}
      </TouchableOpacity>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 18,
    marginBottom: 14,
  },
});

export default GlowCard;