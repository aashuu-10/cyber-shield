import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AuthContext = createContext({
  user: null,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkLoggedInUser();
  }, []);

  const checkLoggedInUser = async () => {
    try {
      const activeUser = await AsyncStorage.getItem('@active_user');
      if (activeUser) {
        setUser(JSON.parse(activeUser));
      }
    } catch (e) {
      console.log('Error loading auth user', e);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name, email, password) => {
    try {
      if (!name || !email || !password) {
        return { success: false, message: 'Please fill in all fields.' };
      }

      // Read registered users
      const usersData = await AsyncStorage.getItem('@users_db');
      const users = usersData ? JSON.parse(usersData) : [];

      // Check if email exists
      const existing = users.find(u => u.email.toLowerCase() === email.toLowerCase());
      if (existing) {
        return { success: false, message: 'Account with this email already exists!' };
      }

      const newUser = { id: Date.now().toString(), name, email, password };
      users.push(newUser);

      await AsyncStorage.setItem('@users_db', JSON.stringify(users));

      // Auto login
      const sessionUser = { id: newUser.id, name: newUser.name, email: newUser.email };
      await AsyncStorage.setItem('@active_user', JSON.stringify(sessionUser));
      setUser(sessionUser);

      return { success: true };
    } catch (e) {
      return { success: false, message: 'Registration failed. Try again.' };
    }
  };

  const login = async (email, password) => {
    try {
      if (!email || !password) {
        return { success: false, message: 'Please enter email and password.' };
      }

      const usersData = await AsyncStorage.getItem('@users_db');
      const users = usersData ? JSON.parse(usersData) : [];

      const found = users.find(
        u => u.email.toLowerCase() === email.toLowerCase() && u.password === password
      );

      if (!found) {
        return { success: false, message: 'Invalid email or password.' };
      }

      const sessionUser = { id: found.id, name: found.name, email: found.email };
      await AsyncStorage.setItem('@active_user', JSON.stringify(sessionUser));
      setUser(sessionUser);

      return { success: true };
    } catch (e) {
      return { success: false, message: 'Login failed. Try again.' };
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('@active_user');
      setUser(null);
    } catch (e) {
      console.log('Logout error', e);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
export default AuthContext;