import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, type User } from '@/api/auth';
import { driverApi } from '@/api/driver';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  type JwtPayload = { type?: 'user' | 'driver'; sub?: string };

  const decodeJwtPayload = (token: string): JwtPayload | null => {
    // Token is created server-side and includes `type` and `sub` claims.
    // We only need `type` to decide which "me" endpoint to call.
    try {
      const parts = token.split('.');
      if (parts.length < 2) return null;
      const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=');
      const json = atob(padded);
      return JSON.parse(json) as JwtPayload;
    } catch {
      return null;
    }
  };

  const fetchUser = useCallback(async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('campusride_token');
      if (!token) {
        setUser(null);
        return;
      }

      const payload = decodeJwtPayload(token);

      if (payload?.type === 'driver') {
        const { data } = await driverApi.getProfile();
        setUser({
          id: data.id,
          name: data.name,
          email: data.email,
          role: 'driver',
          is_active: data.is_active,
        });
      } else {
        const { data } = await authApi.getMe();
        setUser(data);
      }
    } catch {
      localStorage.removeItem('campusride_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('campusride_token');
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const login = async (token: string) => {
    localStorage.setItem('campusride_token', token);
    await fetchUser();
  };

  const logout = () => {
    localStorage.removeItem('campusride_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
