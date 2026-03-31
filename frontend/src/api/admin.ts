import client from './client';
import type { Driver } from './drivers';

export interface CreateDriverPayload {
  name: string;
  phone: string;
  vehicle_type: 'auto' | 'taxi' | 'car';
  vehicle_details: string;
  service_area: string;
  password: string;
}

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  created_at: string;
  rides_contacted: number;
}

export interface AdminStats {
  total_drivers: number;
  active_drivers: number;
  total_students: number;
  total_ratings: number;
  pending_verification: number;
}

export interface PendingDriver {
  id: string;
  name: string;
  email: string;
  phone: string;
  vehicle_type: string;
  vehicle_details: string;
  service_area: string;
  verification_status: string;
  created_at: string;
  documents_uploaded: boolean;
  documents_count: number;
}

export interface DriverDocument {
  id: string;
  document_type: string;
  file_name: string;
  file_size: number;
  file_type: string;
  status: string;
  uploaded_at: string;
  verified_at: string | null;
  expiry_date: string | null;
}

export interface VerificationStatus {
  driver_id: string;
  driver_name: string;
  verification_status: string;
  verification_notes: string | null;
  verified_at: string | null;
  verified_by: string | null;
  documents: DriverDocument[];
  all_required_approved: boolean;
}

export const adminApi = {
  // Stats
  getStats: () => client.get<AdminStats>('/admin/stats'),
  
  // Verification endpoints (NEW)
  getPendingDrivers: (page = 1, limit = 20) =>
    client.get<PendingDriver[]>(`/admin/drivers/pending?page=${page}&limit=${limit}`),
  
  getVerificationStatus: (driverId: string) =>
    client.get<VerificationStatus>(`/admin/drivers/${driverId}/verification-status`),
  
  getDriverDocuments: (driverId: string) =>
    client.get<DriverDocument[]>(`/admin/drivers/${driverId}/documents`),
  
  downloadDocument: (driverId: string, documentId: string) => {
    // Create download link
    return `http://localhost:8000/admin/drivers/${driverId}/documents/${documentId}/download`;
  },
  
  approveDriver: (driverId: string, notes?: string) =>
    client.put(`/admin/drivers/${driverId}/approve`, {
      notes: notes || null
    }),
  
  rejectDriver: (driverId: string, reason: string) =>
    client.put(`/admin/drivers/${driverId}/reject`, {
      reason
    }),
  
  suspendDriver: (driverId: string, reason: string) =>
    client.put(`/admin/drivers/${driverId}/suspend`, {
      reason
    }),
  
  // Standard driver management
  addDriver: (data: CreateDriverPayload) => client.post<Driver>('/admin/drivers', data),
  updateDriver: (id: string, data: Partial<CreateDriverPayload>) =>
    client.put<Driver>('/admin/drivers/' + id, data),
  deactivateDriver: (id: string) => client.delete('/admin/drivers/' + id),
};

