export type UserRole = "admin" | "editor" | "viewer";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface UserUpdate {
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface LoginRequest {
  username: string; // FastAPI OAuth2 uses "username" field
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}
