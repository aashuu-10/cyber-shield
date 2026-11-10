import * as Speech from 'expo-speech';

export const speak = (text, onDone, onStopped) => {
  try {
    if (Speech && typeof Speech.stop === 'function') {
      Speech.stop();
    }
    if (Speech && typeof Speech.speak === 'function') {
      Speech.speak(text, {
        language: 'en-IN',
        rate: 0.9,
        pitch: 1.0,
        onDone: () => { if (onDone) onDone(); },
        onStopped: () => { if (onStopped) onStopped(); },
        onError: () => { if (onStopped) onStopped(); },
      });
    }
  } catch (e) {
    console.log('Speech error:', e);
    if (onStopped) onStopped();
  }
};

export const stop = () => {
  try {
    if (Speech && typeof Speech.stop === 'function') {
      Speech.stop();
    }
  } catch (e) {
    console.log('Speech stop error:', e);
  }
};

export default { speak, stop };