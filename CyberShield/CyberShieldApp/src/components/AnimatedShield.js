import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withSequence,
  Easing,
} from 'react-native-reanimated';
import { COLORS } from '../utils/theme';

const AnimatedShield = ({ score, size }) => {
  const s = size || 160;
  const pulse = useSharedValue(1);
  const rotate = useSharedValue(0);
  const glowOpacity = useSharedValue(0.3);

  const color = score >= 80 ? COLORS.safe : score >= 50 ? COLORS.warning : COLORS.danger;
  const status = score >= 80 ? 'PROTECTED' : score >= 50 ? 'CAUTION' : 'DANGER';
  const emoji = score >= 80 ? '🛡️' : score >= 50 ? '⚠️' : '🚨';

  useEffect(() => {
    pulse.value = withRepeat(
      withSequence(
        withTiming(1.08, { duration: 1500, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 1500, easing: Easing.inOut(Easing.ease) })
      ),
      -1,
      false
    );
    rotate.value = withRepeat(
      withTiming(360, { duration: 8000, easing: Easing.linear }),
      -1,
      false
    );
    glowOpacity.value = withRepeat(
      withSequence(
        withTiming(0.7, { duration: 2000 }),
        withTiming(0.2, { duration: 2000 })
      ),
      -1,
      true
    );
  }, []);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }],
  }));

  const rotateStyle = useAnimatedStyle(() => ({
    transform: [{ rotate: rotate.value + 'deg' }],
  }));

  const glowStyle = useAnimatedStyle(() => ({
    opacity: glowOpacity.value,
  }));

  return (
    <View style={[styles.container, { width: s, height: s }]}>
      <Animated.View style={[styles.glowRing, { borderColor: color, width: s, height: s, borderRadius: s / 2 }, glowStyle]} />
      <Animated.View style={[styles.orbitRing, { width: s + 20, height: s + 20, borderRadius: (s + 20) / 2, borderColor: color + '30' }, rotateStyle]}>
        <View style={[styles.orbitDot, { backgroundColor: color }]} />
      </Animated.View>
      <Animated.View style={[styles.shield, { width: s - 20, height: s - 20, borderRadius: (s - 20) / 2, borderColor: color }, pulseStyle]}>
        <Text style={{ fontSize: s * 0.22 }}>{emoji}</Text>
        <Text style={[styles.score, { color: color, fontSize: s * 0.2 }]}>{score}</Text>
        <Text style={[styles.status, { color: color }]}>{status}</Text>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { justifyContent: 'center', alignItems: 'center', alignSelf: 'center' },
  glowRing: { position: 'absolute', borderWidth: 3 },
  orbitRing: { position: 'absolute', borderWidth: 1, borderStyle: 'dashed' },
  orbitDot: { width: 8, height: 8, borderRadius: 4, position: 'absolute', top: 0, left: '50%', marginLeft: -4 },
  shield: { backgroundColor: COLORS.backgroundCard, justifyContent: 'center', alignItems: 'center', borderWidth: 2 },
  score: { fontWeight: '900' },
  status: { fontSize: 10, fontWeight: '800', letterSpacing: 3, marginTop: 2 },
});

export default AnimatedShield;