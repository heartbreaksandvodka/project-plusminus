import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthContextType, User, AuthTokens, LoginCredentials, RegisterCredentials } from '../types/auth';
import { authService } from '../services';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedTokens = localStorage.getItem('tokens');
        const storedUser = localStorage.getItem('user');
        
        if (storedTokens && storedUser) {
          const parsedTokens = JSON.parse(storedTokens);
          const parsedUser = JSON.parse(storedUser);
          
          setTokens(parsedTokens);
          setUser(parsedUser);
          
          // Verify token is still valid by fetching profile
          try {
            const profile = await authService.getProfile();
            setUser(profile);
          } catch (error) {
            // Token invalid, clear storage
            localStorage.removeItem('tokens');
            localStorage.removeItem('user');
            setTokens(null);
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authService.login(credentials);
      const { user, tokens } = response;
      
      setUser(user);
      setTokens(tokens);
      
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('tokens', JSON.stringify(tokens));
    } catch (error) {
      throw error;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    try {
      const response = await authService.register(credentials);
      const { user, tokens } = response;
      
      setUser(user);
      setTokens(tokens);
      
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('tokens', JSON.stringify(tokens));
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (tokens?.refresh) {
        await authService.logout(tokens.refresh);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setTokens(null);
      localStorage.removeItem('user');
      localStorage.removeItem('tokens');
    }
  };

  const value: AuthContextType = {
    user,
    tokens,
    token: tokens?.access || null,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
