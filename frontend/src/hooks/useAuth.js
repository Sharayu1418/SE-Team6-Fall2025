/**
 * Authentication hook.
 * 
 * Provides convenient access to auth state and actions.
 */

import useAuthStore from '../store/authStore';

export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    fetchUser,
    login,
    register,
    logout,
    clearError,
  } = useAuthStore();

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    fetchUser,
    login,
    register,
    logout,
    clearError,
  };
}

