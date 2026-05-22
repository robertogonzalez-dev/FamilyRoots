import api from "./api";
import type { User, UserCreate, UserUpdate } from "../types/user";

interface DashboardStats {
  total_people: number;
  total_relationships: number;
  total_users: number;
  living_people: number;
}

export const adminService = {
  async getDashboard(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>("/admin/dashboard");
    return data;
  },

  async listUsers(): Promise<User[]> {
    const { data } = await api.get<User[]>("/admin/users");
    return data;
  },

  async createUser(user: UserCreate): Promise<User> {
    const { data } = await api.post<User>("/admin/users", user);
    return data;
  },

  async updateUser(id: number, update: UserUpdate): Promise<User> {
    const { data } = await api.patch<User>(`/admin/users/${id}`, update);
    return data;
  },

  async deleteUser(id: number): Promise<void> {
    await api.delete(`/admin/users/${id}`);
  },
};
