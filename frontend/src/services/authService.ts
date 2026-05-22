import api from "./api";
import type { Token, User } from "../types/user";

export const authService = {
  async login(email: string, password: string): Promise<Token> {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const { data } = await api.post<Token>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data;
  },

  async register(email: string, password: string, full_name: string): Promise<User> {
    const { data } = await api.post<User>("/auth/register", { email, password, full_name });
    return data;
  },

  async me(): Promise<User> {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },
};
