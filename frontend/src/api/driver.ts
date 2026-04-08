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

export interface DriverDocument {
  id: string;
  document_type: string;
  file_name: string;
  file_size: number;
  file_type: string;
  status: string;
  created_at: string | null;
  verified_at: string | null;
  rejection_reason: string | null;
  expiry_date: string | null;
}

export interface VerificationStatus {
  driver_id: string;
  verification_status: string;
  documents: DriverDocument[];
}

export const driverApi = {
  getProfile: () => client.get<DriverProfile>('/driver/me'),
  updateAvailability: (is_available: boolean) =>
    client.put('/driver/me/availability', { is_available }),
  getRatings: () => client.get<Rating[]>('/driver/me/ratings'),
  getVerificationStatus: () => client.get<VerificationStatus>('/driver/me/verification-status'),
  getMyDocuments: () => client.get<DriverDocument[]>('/driver/me/documents'),
  getDocumentDownloadUrl: (documentId: string) => {
    const baseUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    return `${baseUrl}/driver/me/documents/${documentId}/download`;
  },
};
