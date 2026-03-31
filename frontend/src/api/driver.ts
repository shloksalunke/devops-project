import client from './client';

export interface DriverProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  vehicle_type: string;
  vehicle_details: string | null;
  service_area: string | null;
  is_active: boolean;
  is_available: boolean;
  avg_rating: number;
  total_ratings: number;
}

export interface Rating {
  id: string;
  rating: number;
  comment: string;
  created_at: string;
}

export const driverApi = {
  getProfile: () => client.get<DriverProfile>('/driver/me'),
  updateAvailability: (is_available: boolean) =>
    client.put('/driver/me/availability', { is_available }),
  getRatings: () => client.get<Rating[]>('/driver/me/ratings'),
};
