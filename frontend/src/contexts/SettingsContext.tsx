import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';

interface UserSettings {
  notifications: boolean;
  privacy: 'public' | 'private';
  show_ea_statistics: boolean;
}

interface SettingsContextType {
  settings: UserSettings | null;
  loading: boolean;
  error: string;
  updateSettings: (newSettings: Partial<UserSettings>) => Promise<void>;
  refreshSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

interface SettingsProviderProps {
  children: React.ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchSettings = useCallback(async () => {
    if (!token || !isAuthenticated) {
      setSettings(null);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/settings/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      } else {
        setError('Failed to fetch settings');
        // Set default settings if fetch fails
        setSettings({
          notifications: true,
          privacy: 'public',
          show_ea_statistics: true,
        });
      }
    } catch (err) {
      setError('Network error while fetching settings');
      // Set default settings on error
      setSettings({
        notifications: true,
        privacy: 'public',
        show_ea_statistics: true,
      });
    } finally {
      setLoading(false);
    }
  }, [token, isAuthenticated]);

  const updateSettings = useCallback(async (newSettings: Partial<UserSettings>) => {
    if (!token || !settings) {
      throw new Error('Cannot update settings: not authenticated or settings not loaded');
    }

    const updatedSettings = { ...settings, ...newSettings };

    try {
      const response = await fetch('http://localhost:8000/api/settings/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedSettings),
      });

      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      } else {
        throw new Error('Failed to update settings');
      }
    } catch (err) {
      throw err;
    }
  }, [token, settings]);

  const refreshSettings = useCallback(async () => {
    await fetchSettings();
  }, [fetchSettings]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchSettings();
    } else {
      setSettings(null);
    }
  }, [isAuthenticated, fetchSettings]);

  const value: SettingsContextType = {
    settings,
    loading,
    error,
    updateSettings,
    refreshSettings,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};
