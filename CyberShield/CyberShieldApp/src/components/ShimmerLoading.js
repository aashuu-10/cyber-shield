import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  Easing,
} from 'react-native-reanimated';
import { COLORS } from '../utils/theme';

const ShimmerLoading = ({ width, height, borderRadius }) => {
  const translateX = useSharedValue(-200);

  useEffect(() => {
    translateX.value = withRepeat(
      withTiming(400, { duration: 1200, easing: Easing.linear }),
      -1,
      false
    );
  }, []);

  const shimmerStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <View style={[styles.container, { width: width || '100%', height: height || 20, borderRadius: borderRadius || 8 }]}>
      <Animated.View style={[styles.shimmer, shimmerStyle]} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { backgroundColor: COLORS.backgroundCard, overflow: 'hidden' },
  shimmer: { width: 100, height: '100%', backgroundColor: COLORS.border, opacity: 0.5 },
});

export default ShimmerLoading;