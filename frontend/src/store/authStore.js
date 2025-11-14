/**
 * Zustand authentication store.
 * 
 * Manages user authentication state and actions.
 */

import { create } from 'zustand';
import api from '../api/client';

const useAuthStore = create((set, get) => ({
  // State
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  // Actions
  fetchUser: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await api.get('/auth/me/');
      set({
        user: response.data,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      // 401 means not authenticated, which is fine
      if (error.response?.status === 401) {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      } else {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: error.response?.data?.detail || 'Failed to fetch user',
        });
      }
    }
  },

  login: async (username, password) => {
    set({ isLoading: true, error: null });
    
    try {
      // First, make a GET request to get CSRF cookie (Django sets it automatically)
      try {
        await api.get('/sources/');
      } catch (e) {
        // Ignore errors, we just need the CSRF cookie
      }
      
      const response = await api.post('/auth/login/', {
        username,
        password,
      });
      
      // Fetch user data after successful login
      await get().fetchUser();
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.non_field_errors?.[0] ||
                          error.response?.data?.error ||
                          'Login failed. Please check your credentials.';
      
      set({
        isLoading: false,
        error: errorMessage,
      });
      
      return { success: false };
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    
    try {
      // First, make a GET request to get CSRF cookie (Django sets it automatically)
      try {
        await api.get('/sources/');
      } catch (e) {
        // Ignore errors, we just need the CSRF cookie
      }
      
      const response = await api.post('/auth/register/', userData);
      
      // Fetch user data after successful registration
      await get().fetchUser();
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.error ||
                          error.response?.data?.username?.[0] ||
                          error.response?.data?.password?.[0] ||
                          Object.values(error.response?.data || {}).flat()[0] ||
                          'Registration failed. Please try again.';
      
      set({
        isLoading: false,
        error: errorMessage,
      });
      
      return { success: false };
    }
  },

  logout: async () => {
    set({ isLoading: true, error: null });
    
    try {
      await api.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));

export default useAuthStore;
