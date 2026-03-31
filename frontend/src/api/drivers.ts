import client from './client';

export interface Rating {
  id: string;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface Driver {
  id: string;
  name: string;
  phone?: string;
  vehicle_type: 'auto' | 'taxi' | 'car';
  vehicle_details: string;
  service_area: string;
  is_available: boolean;
  avg_rating: number;
  total_ratings: number;
  ratings?: Rating[];
}

export const driversApi = {
  getAll: () => client.get<Driver[]>('/drivers'),
  getById: (id: string) => client.get<Driver>('/drivers/' + id),
  rate: (id: string, data: { rating: number; comment: string }) =>
    client.post('/drivers/' + id + '/ratings', data),
};
