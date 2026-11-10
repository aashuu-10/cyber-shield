import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  TouchableOpacity, Alert
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../context/ThemeContext';
import { getScanHistory, deleteScanRecord, clearScanHistory } from '../services/HistoryService';
import GlowCard from '../components/GlowCard';

const HistoryScreen = () => {
  const { colors, isDark } = useTheme();
  const [history, setHistory] = useState([]);

  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, [])
  );

  const loadHistory = async () => {
    const data = await getScanHistory();
    setHistory(data);
  };

  const handleDeleteItem = async (id) => {
    const updated = await deleteScanRecord(id);
    setHistory(updated);
  };

  const handleClearAll = () => {
    Alert.alert('Clear History?', 'Are you sure you want to delete all work scan history?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Clear All', style: 'destructive',
        onPress: async () => {
          await clearScanHistory();
          setHistory([]);
        }
      }
    ]);
  };

  const getRiskColor = (level) => {
    if (level === 'HIGH') return colors.accent;
    if (level === 'MEDIUM') return colors.warning;
    return colors.success;
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View>
          <Text style={[styles.title, { color: colors.text }]}>📋 Work Scan History</Text>
          <Text style={[styles.subtitle, { color: colors.textMuted }]}>{history.length} scans recorded</Text>
        </View>
        {history.length > 0 && (
          <TouchableOpacity style={[styles.clearBtn, { backgroundColor: isDark ? 'rgba(255,107,107,0.15)' : '#FEE2E2' }]} onPress={handleClearAll}>
            <Text style={[styles.clearBtnText, { color: colors.accent }]}>🗑️ Clear</Text>
          </TouchableOpacity>
        )}
      </View>

      {history.length === 0 && (
        <GlowCard>
          <Text style={styles.emptyEmoji}>🔍</Text>
          <Text style={[styles.emptyText, { color: colors.text }]}>No Scans Saved Yet</Text>
          <Text style={[styles.emptySub, { color: colors.textMuted }]}>
            Any text, link, or screenshot you scan will be automatically stored in your history here.
          </Text>
        </GlowCard>
      )}

      {history.map((item) => (
        <GlowCard key={item.id} glowColor={getRiskColor(item.riskLevel)}>
          <View style={styles.itemHeader}>
            <Text style={[styles.itemType, { color: colors.text }]}>
              {item.type === 'TEXT' ? '📝 TEXT' : item.type === 'URL' ? '🔗 LINK' : '📸 SCREENSHOT'}
            </Text>
            <View style={styles.headerRight}>
              <Text style={[styles.riskBadge, { color: getRiskColor(item.riskLevel) }]}>
                {item.isThreat ? `⚠️ ${item.riskLevel}` : '✅ SAFE'}
              </Text>
              <TouchableOpacity onPress={() => handleDeleteItem(item.id)} style={{ marginLeft: 10 }}>
                <Text style={{ fontSize: 16 }}>❌</Text>
              </TouchableOpacity>
            </View>
          </View>

          <Text style={[styles.itemQuery, { color: colors.text }]} numberOfLines={2}>
            "{item.query}"
          </Text>

          <View style={styles.itemFooter}>
            <Text style={[styles.itemDate, { color: colors.textMuted }]}>📅 {item.timestamp}</Text>
            <Text style={[styles.itemScore, { color: colors.textMuted }]}>Score: {item.score}/100</Text>
          </View>
        </GlowCard>
      ))}

      <View style={{ height: 40 }} />
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
  title: { fontSize: 24, fontWeight: 'bold' },
  subtitle: { fontSize: 13, marginTop: 4 },
  clearBtn: { padding: 10, borderRadius: 10 },
  clearBtnText: { fontWeight: '700', fontSize: 13 },
  emptyEmoji: { fontSize: 48, textAlign: 'center', marginBottom: 10 },
  emptyText: { fontSize: 18, textAlign: 'center', fontWeight: '600' },
  emptySub: { fontSize: 13, textAlign: 'center', marginTop: 6, lineHeight: 18 },
  itemHeader: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: 8,
  },
  headerRight: { flexDirection: 'row', alignItems: 'center' },
  itemType: { fontSize: 14, fontWeight: 'bold' },
  riskBadge: { fontWeight: 'bold', fontSize: 13 },
  itemQuery: { fontSize: 14, fontStyle: 'italic', marginBottom: 10, lineHeight: 20 },
  itemFooter: { flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.08)', paddingTop: 8 },
  itemDate: { fontSize: 12 },
  itemScore: { fontSize: 12, fontWeight: '600' },
});

export default HistoryScreen;