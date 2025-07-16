import api from './client';
import { AuthResponse, LoginCredentials, RegisterCredentials, User } from '../../types/auth';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/login/', credentials);
    return response.data;
  },

  register: async (credentials: RegisterCredentials): Promise<AuthResponse> => {
    const response = await api.post('/register/', credentials);
    return response.data;
  },

  logout: async (refreshToken: string): Promise<void> => {
    await api.post('/logout/', { refresh: refreshToken });
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/profile/');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await api.put('/update-profile/', userData);
    return response.data.user;
  },

  changePassword: async (passwordData: {
    current_password: string;
    new_password: string;
    new_password_confirm: string;
  }): Promise<any> => {
    const response = await api.post('/change-password/', passwordData);
    return response.data;
  },

  forgotPassword: async (email: string): Promise<any> => {
    const response = await api.post('/forgot-password/', { email });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string): Promise<any> => {
    const response = await api.post('/reset-password/', {
      token,
      new_password: newPassword,
      new_password_confirm: newPassword,
    });
    return response.data;
  },

  getDashboard: async (): Promise<any> => {
    const response = await api.get('/dashboard/');
    return response.data;
  },

  getSubscriptions: async (): Promise<any> => {
    const response = await api.get('/subscriptions/');
    return response.data;
  },
};
