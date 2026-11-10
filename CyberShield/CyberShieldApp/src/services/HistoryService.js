import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEY = '@cyber_shield_scan_history';

export const saveScanRecord = async (type, queryText, result) => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEY);
    const history = existing ? JSON.parse(existing) : [];

    const newRecord = {
      id: Date.now().toString(),
      type: type, // 'TEXT', 'URL', or 'SCREENSHOT'
      query: queryText.substring(0, 100),
      isThreat: result.isThreat,
      riskLevel: result.riskLevel,
      score: result.score,
      threatCount: result.threats ? result.threats.length : 0,
      timestamp: new Date().toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      }),
    };

    // Prepend to array (newest first)
    const updated = [newRecord, ...history];
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(updated.slice(0, 50))); // Keep last 50
    return true;
  } catch (e) {
    console.log('Error saving history record', e);
    return false;
  }
};

export const getScanHistory = async () => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEY);
    return existing ? JSON.parse(existing) : [];
  } catch (e) {
    console.log('Error fetching history', e);
    return [];
  }
};

export const deleteScanRecord = async (id) => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEY);
    if (!existing) return [];
    const history = JSON.parse(existing);
    const updated = history.filter(item => item.id !== id);
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch (e) {
    console.log('Error deleting record', e);
    return [];
  }
};

export const clearScanHistory = async () => {
  try {
    await AsyncStorage.removeItem(STORAGE_KEY);
    return true;
  } catch (e) {
    console.log('Error clearing history', e);
    return false;
  }
};