export const getThreatColor = (level) => {
  const colors = { safe: '#00E676', low: '#76FF03', medium: '#FFD600', high: '#FF6D00', critical: '#FF1744' };
  return colors[level] || '#A0A3BD';
};

export const getThreatEmoji = (level) => {
  const emojis = { safe: '✅', low: '🟡', medium: '🟠', high: '🔴', critical: '🚨' };
  return emojis[level] || '❓';
};

export const isValidURL = (str) => {
  return /^(https?:\/\/|www\.)[^\s]+/i.test(str) || /^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}/i.test(str);
};

export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};

export const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);