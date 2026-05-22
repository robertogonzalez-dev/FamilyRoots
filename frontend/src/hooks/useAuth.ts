import { useState, useEffect, useCallback } from "react";
import { authService } from "../services/authService";
import type { User } from "../types/user";

interface AuthState {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    isAuthenticated: false,
  });

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setState({ user: null, loading: false, isAuthenticated: false });
      return;
    }
    try {
      const user = await authService.me();
      setState({ user, loading: false, isAuthenticated: true });
    } catch {
      localStorage.removeItem("access_token");
      setState({ user: null, loading: false, isAuthenticated: false });
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    const token = await authService.login(email, password);
    localStorage.setItem("access_token", token.access_token);
    await loadUser();
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setState({ user: null, loading: false, isAuthenticated: false });
  };

  return { ...state, login, logout, reload: loadUser };
}
