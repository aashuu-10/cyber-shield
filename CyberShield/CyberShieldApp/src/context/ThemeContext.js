import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { darkColors, lightColors } from '../utils/theme';

const ThemeContext = createContext({
  isDark: true,
  colors: darkColors,
  toggleTheme: () => {},
  setDarkMode: () => {},
});

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem('@theme_mode');
        if (saved === 'light') setIsDark(false);
        if (saved === 'dark') setIsDark(true);
      } catch (e) {
        console.log('Theme load error', e);
      }
    })();
  }, []);

  const setDarkMode = async (value) => {
    setIsDark(value);
    try {
      await AsyncStorage.setItem('@theme_mode', value ? 'dark' : 'light');
    } catch (e) {
      console.log('Theme save error', e);
    }
  };

  const toggleTheme = () => setDarkMode(!isDark);

  const colors = isDark ? darkColors : lightColors;

  return (
    <ThemeContext.Provider value={{ isDark, colors, toggleTheme, setDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);

export default ThemeContext;