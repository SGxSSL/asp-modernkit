import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { settingsService } from '../services/settingsService';

interface AppContextType {
  settings: Record<string, string>;
  loading: boolean;
  error: string | null;
}

const AppContext = createContext<AppContextType>({
  settings: {},
  loading: true,
  error: null,
});

export const useAppContext = () => useContext(AppContext);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    settingsService
      .getAllSettings()
      .then((data) => {
        setSettings(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <AppContext.Provider value={{ settings, loading, error }}>
      {children}
    </AppContext.Provider>
  );
};
