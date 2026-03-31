import client from './client';

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role: 'student';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'student' | 'driver' | 'admin';
}

export const authApi = {
  login: (data: LoginPayload) => client.post<AuthResponse>('/auth/login', data),
  register: (data: RegisterPayload) => client.post('/auth/register', data),
  // register driver with documents (multipart)
  registerDriver: (formData: FormData) => client.post('/auth/register-driver', formData),
  getMe: () => client.get<User>('/users/me'),
};
