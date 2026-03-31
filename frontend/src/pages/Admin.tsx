import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { driversApi, type Driver } from '@/api/drivers';
import { adminApi, type CreateDriverPayload, type PendingDriver, type VerificationStatus } from '@/api/admin';
import { useToastNotify } from '@/components/ToastNotify';
import Modal from '@/components/Modal';
import Badge from '@/components/Badge';
import { LayoutDashboard, Car, Users, Plus, Pencil, Trash2, LogOut, FileText, CheckCircle, XCircle, Download, Eye } from 'lucide-react';

type Tab = 'dashboard' | 'pending-verification' | 'drivers' | 'users';

const Admin: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToastNotify();
  
  // Tabs and UI state
  const [tab, setTab] = useState<Tab>('dashboard');
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [docViewerOpen, setDocViewerOpen] = useState(false);
  const [verificationModalOpen, setVerificationModalOpen] = useState(false);
  
  // Data states
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [pendingDrivers, setPendingDrivers] = useState<PendingDriver[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<PendingDriver | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus | null>(null);
  
  // Form states
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
  const [form, setForm] = useState<CreateDriverPayload>({
    name: '', phone: '', vehicle_type: 'auto', vehicle_details: '', service_area: '', password: '',
  });
  const [rejectionReason, setRejectionReason] = useState('');
  const [approvalNotes, setApprovalNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  // Load data
  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true);
        const [driversRes, pendingRes] = await Promise.all([
          driversApi.getAll(),
          adminApi.getPendingDrivers()
        ]);
        setDrivers(driversRes.data);
        setPendingDrivers(pendingRes.data);
      } catch {
        showToast('Failed to load data', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [showToast]);

  // View verification details
  const handleViewVerification = async (driver: PendingDriver) => {
    try {
      const { data } = await adminApi.getVerificationStatus(driver.id);
      setVerificationStatus(data);
      setSelectedDriver(driver);
      setDocViewerOpen(true);
    } catch {
      showToast('Failed to load verification details', 'error');
    }
  };

  // Approve driver
  const handleApprove = async () => {
    if (!selectedDriver) return;
    setSubmitting(true);
    try {
      await adminApi.approveDriver(selectedDriver.id, approvalNotes);
      showToast('Driver approved successfully!', 'success');
      setDocViewerOpen(false);
      setPendingDrivers(prev => prev.filter(d => d.id !== selectedDriver.id));
      setApprovalNotes('');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to approve driver', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  // Reject driver
  const handleReject = async () => {
    if (!selectedDriver || !rejectionReason.trim()) {
      showToast('Please provide a rejection reason', 'error');
      return;
    }
    setSubmitting(true);
    try {
      await adminApi.rejectDriver(selectedDriver.id, rejectionReason);
      showToast('Driver rejected', 'success');
      setVerificationModalOpen(false);
      setPendingDrivers(prev => prev.filter(d => d.id !== selectedDriver.id));
      setRejectionReason('');
    } catch {
      showToast('Failed to reject driver', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  // Driver CRUD
  const openAdd = () => {
    setEditingDriver(null);
    setForm({ name: '', phone: '', vehicle_type: 'auto', vehicle_details: '', service_area: '', password: '' });
    setModalOpen(true);
  };

  const openEdit = (d: Driver) => {
    setEditingDriver(d);
    setForm({ name: d.name, phone: d.phone, vehicle_type: d.vehicle_type, vehicle_details: d.vehicle_details, service_area: d.service_area, password: '' });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (editingDriver) {
        await adminApi.updateDriver(editingDriver.id, form);
        showToast('Driver updated', 'success');
      } else {
        await adminApi.addDriver(form);
        showToast('Driver added', 'success');
      }
      const { data } = await driversApi.getAll();
      setDrivers(data);
      setModalOpen(false);
    } catch {
      showToast('Operation failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeactivate = async (id: string) => {
    try {
      await adminApi.deactivateDriver(id);
      setDrivers(prev => prev.filter(d => d.id !== id));
      showToast('Driver deactivated', 'success');
    } catch {
      showToast('Failed to deactivate', 'error');
    }
  };

  const handleLogout = () => { logout(); navigate('/login'); };

  // Download document handler
  const handleDownloadDocument = async (docId: string, fileName: string) => {
    try {
      if (!selectedDriver) return;
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `http://localhost:8000/admin/drivers/${selectedDriver.id}/documents/${docId}/download`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (!response.ok) {
        showToast('Failed to download document', 'error');
        return;
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      showToast('Error downloading document', 'error');
    }
  };

  const stats = {
    totalDrivers: drivers.length,
    activeDrivers: drivers.filter(d => d.is_active).length,
    pendingVerification: pendingDrivers.length,
    totalRatings: drivers.reduce((s, d) => s + d.total_ratings, 0),
  };

  const sidebarLinks: { key: Tab; label: string; icon: React.ReactNode; badge?: number }[] = [
    { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
    { key: 'pending-verification', label: 'Pending Verification', icon: <FileText size={18} />, badge: pendingDrivers.length },
    { key: 'drivers', label: 'All Drivers', icon: <Car size={18} /> },
    { key: 'users', label: 'Users', icon: <Users size={18} /> },
  ];

  const set = (key: string, val: string) => setForm(p => ({ ...p, [key]: val }));

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-56 border-r border-border bg-card">
        <div className="flex h-14 items-center gap-2 border-b border-border px-4">
          <span className="text-lg font-bold text-foreground">Admin Panel</span>
        </div>
        <nav className="mt-2 space-y-1 px-2">
          {sidebarLinks.map(l => (
            <div key={l.key} className="relative">
              <button
                onClick={() => setTab(l.key)}
                className={`flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150 ${
                  tab === l.key ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                {l.icon}
                <span className="flex-1 text-left">{l.label}</span>
                {l.badge ? <span className="rounded-full bg-destructive px-2 py-0.5 text-xs font-bold text-white">{l.badge}</span> : null}
              </button>
            </div>
          ))}
        </nav>
        <div className="mt-auto border-t border-border p-2">
          <button onClick={handleLogout} className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-destructive hover:bg-secondary">
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Content */}
      <main className="flex-1 p-8">
        {tab === 'dashboard' && (
          <>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <div className="mt-6 grid gap-4 sm:grid-cols-4">
              {[
                { label: 'Total Drivers', value: stats.totalDrivers, color: 'bg-blue-100 text-blue-900 border-blue-200', icon: '🚗' },
                { label: 'Active & Approved', value: stats.activeDrivers, color: 'bg-green-100 text-green-900 border-green-200', icon: '✅' },
                { label: 'Pending Verification', value: stats.pendingVerification, color: 'bg-yellow-100 text-yellow-900 border-yellow-200', icon: '⏳' },
                { label: 'Total Ratings', value: stats.totalRatings, color: 'bg-purple-100 text-purple-900 border-purple-200', icon: '⭐' },
              ].map(s => (
                <div key={s.label} className={`rounded-lg border-2 ${s.color} p-6 transition hover:shadow-md`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium opacity-80">{s.label}</p>
                      <p className="mt-3 text-4xl font-bold">{s.value}</p>
                    </div>
                    <span className="text-3xl">{s.icon}</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {tab === 'pending-verification' && (
          <>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-foreground">Pending Driver Verification</h1>
              <p className="mt-1 text-sm text-muted-foreground">Review driver registration applications and verify documents</p>
            </div>

            {pendingDrivers.length === 0 ? (
              <div className="rounded-lg border-2 border-dashed border-border bg-card p-12 text-center">
                <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
                <p className="mt-4 text-lg font-medium text-foreground">All caught up! ✅</p>
                <p className="text-muted-foreground">No pending driver applications</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingDrivers.map((driver, idx) => (
                  <div key={driver.id} className="group rounded-lg border border-border bg-card p-5 hover:border-primary hover:bg-secondary/30 transition">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {/* Header */}
                        <div className="flex items-center gap-3 mb-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-semibold">
                            {idx + 1}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-foreground">{driver.name}</h3>
                            <p className="text-sm text-muted-foreground">{driver.email}</p>
                          </div>
                        </div>

                        {/* Details Grid */}
                        <div className="grid gap-4 sm:grid-cols-3 mb-3">
                          <div>
                            <p className="text-xs font-medium text-muted-foreground uppercase">Phone</p>
                            <p className="text-sm font-medium text-foreground">{driver.phone}</p>
                          </div>
                          <div>
                            <p className="text-xs font-medium text-muted-foreground uppercase">Vehicle Type</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <Badge variant={driver.vehicle_type} />
                              <span className="text-xs text-muted-foreground">{driver.vehicle_details}</span>
                            </div>
                          </div>
                          <div>
                            <p className="text-xs font-medium text-muted-foreground uppercase">Applied</p>
                            <p className="text-sm font-medium text-foreground">{new Date(driver.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>

                        {/* Documents Status */}
                        <div className="mb-3 flex items-center gap-2">
                          {driver.documents_uploaded ? (
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800">
                              <span className="text-sm">📄</span> {driver.documents_count} documents submitted
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-800">
                              <span className="text-sm">⚠️</span> No documents uploaded
                            </span>
                          )}
                        </div>

                        {/* Service Area */}
                        {driver.service_area && (
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium">Service Area:</span> {driver.service_area}
                          </p>
                        )}
                      </div>

                      {/* Review Button */}
                      <button
                        onClick={() => handleViewVerification(driver)}
                        className="ml-4 rounded-md bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90 transition whitespace-nowrap"
                      >
                        Review Request
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {tab === 'drivers' && (
          <>
            <div className="mb-6 flex items-center justify-between">
              <h1 className="text-3xl font-bold text-foreground">All Drivers</h1>
              <button
                onClick={openAdd}
                className="flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
              >
                <Plus size={16} /> Add Driver
              </button>
            </div>
            <div className="overflow-x-auto rounded-lg border border-border bg-card">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-secondary">
                  <tr>
                    <th className="px-4 py-3 font-medium">Name</th>
                    <th className="px-4 py-3 font-medium">Vehicle</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Verification</th>
                    <th className="px-4 py-3 font-medium">Rating</th>
                    <th className="px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {drivers.map(d => (
                    <tr key={d.id} className="border-b border-border last:border-0 hover:bg-secondary/50">
                      <td className="px-4 py-3 font-medium">{d.name}</td>
                      <td className="px-4 py-3"><Badge variant={d.vehicle_type} /></td>
                      <td className="px-4 py-3">
                        <Badge variant={d.is_available ? 'available' : 'busy'} dot />
                      </td>
                      <td className="px-4 py-3 text-sm">{d.verification_status || 'N/A'}</td>
                      <td className="px-4 py-3 text-muted-foreground">⭐ {d.avg_rating.toFixed(1)}</td>
                      <td className="flex gap-2 px-4 py-3">
                        <button onClick={() => openEdit(d)} className="rounded p-1 hover:bg-secondary" title="Edit">
                          <Pencil size={14} />
                        </button>
                        <button onClick={() => handleDeactivate(d.id)} className="rounded p-1 text-destructive hover:bg-secondary" title="Deactivate">
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {drivers.length === 0 && (
                <div className="px-4 py-8 text-center text-muted-foreground">No drivers found</div>
              )}
            </div>
          </>
        )}

        {tab === 'users' && (
          <>
            <h1 className="text-3xl font-bold text-foreground">Users Management</h1>
            <div className="mt-6 rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
              Users management coming soon...
            </div>
          </>
        )}
      </main>

      {/* Add/Edit Driver Modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingDriver ? 'Edit Driver' : 'Add Driver'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            placeholder="Name"
            value={form.name}
            onChange={e => set('name', e.target.value)}
            required
            className="w-full rounded-md border px-3 py-2"
          />
          <input
            placeholder="Phone"
            value={form.phone}
            onChange={e => set('phone', e.target.value)}
            required
            className="w-full rounded-md border px-3 py-2"
          />
          {!editingDriver && (
            <input
              placeholder="Password"
              type="password"
              onChange={e => set('password', e.target.value)}
              required
              className="w-full rounded-md border px-3 py-2"
            />
          )}
          <select
            value={form.vehicle_type}
            onChange={e => set('vehicle_type', e.target.value)}
            className="w-full rounded-md border px-3 py-2"
          >
            <option value="auto">Auto</option>
            <option value="taxi">Taxi</option>
            <option value="car">Car</option>
          </select>
          <input
            placeholder="Vehicle details"
            value={form.vehicle_details}
            onChange={e => set('vehicle_details', e.target.value)}
            className="w-full rounded-md border px-3 py-2"
          />
          <input
            placeholder="Service area"
            value={form.service_area}
            onChange={e => set('service_area', e.target.value)}
            className="w-full rounded-md border px-3 py-2"
          />
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-primary py-2 text-white disabled:opacity-50"
          >
            {submitting ? 'Saving...' : 'Save'}
          </button>
        </form>
      </Modal>

      {/* Document Viewer & Verification Modal */}
      <Modal
        open={docViewerOpen}
        onClose={() => setDocViewerOpen(false)}
        title={`Review: ${selectedDriver?.name}`}
      >
        {verificationStatus && (
          <div className="space-y-4">
            {/* Driver Info Card - Compact */}
            <div className="rounded-lg border border-border bg-secondary/50 p-3">
              <div className="grid gap-2 text-sm">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase">Name</p>
                    <p className="font-medium text-foreground">{selectedDriver?.name}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase">Phone</p>
                    <p className="font-medium text-foreground">{selectedDriver?.phone}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase">Email</p>
                    <p className="font-medium text-foreground text-xs break-all">{selectedDriver?.email}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase">Vehicle</p>
                    <p className="font-medium text-foreground">{selectedDriver?.vehicle_type}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Documents Section - Scrollable */}
            <div>
              <h3 className="mb-2 text-sm font-semibold text-foreground">📄 Documents ({verificationStatus.documents.length})</h3>
              {verificationStatus.documents.length === 0 ? (
                <div className="rounded-lg border-2 border-dashed border-border bg-secondary/30 p-4 text-center">
                  <p className="text-sm text-muted-foreground">No documents submitted</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                  {verificationStatus.documents.map(doc => {
                    const docTypeIcons: { [key: string]: string } = {
                      'ID': '🆔',
                      'LICENSE': '📜',
                      'RC': '🚗',
                      'INSURANCE': '🛡️'
                    };
                    const icon = docTypeIcons[doc.document_type] || '📄';
                    
                    return (
                      <div key={doc.id} className="rounded-lg border border-border bg-card p-3 hover:bg-secondary/50 transition">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-lg flex-shrink-0">{icon}</span>
                              <p className="font-medium text-foreground text-sm">{doc.document_type}</p>
                            </div>
                            <p className="text-xs text-muted-foreground truncate">{doc.file_name}</p>
                            <p className="text-xs text-muted-foreground">{(doc.file_size / 1024).toFixed(1)} KB • {doc.file_type}</p>
                          </div>
                          <div className="flex items-center gap-1 flex-shrink-0">
                            <button
                              onClick={() => handleDownloadDocument(doc.id, doc.file_name)}
                              className="p-1.5 rounded-md bg-blue-100 text-blue-600 hover:bg-blue-200 transition"
                              title={`${doc.file_type === 'pdf' ? 'View' : 'Download'} document`}
                            >
                              {doc.file_type === 'pdf' ? <Eye size={14} /> : <Download size={14} />}
                            </button>
                            <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium flex-shrink-0 whitespace-nowrap ${
                              doc.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                              doc.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {doc.status === 'APPROVED' ? '✓' : 
                               doc.status === 'REJECTED' ? '✗' : 
                               '⏳'}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Verification Summary - Compact */}
            <div className="rounded-lg border-l-4 border-l-blue-500 bg-blue-50 p-3">
              <p className="text-xs font-semibold text-blue-900 mb-1">Verification Status</p>
              <div className="text-xs text-blue-800 space-y-0.5">
                <p>Documents: {verificationStatus.documents.length} submitted</p>
                <p>Status: {verificationStatus.all_required_approved ? '✅ Ready to Approve' : '❌ Incomplete'}</p>
              </div>
            </div>

            {/* Admin Actions - Fixed */}
            <div className="space-y-3 border-t border-border pt-3">
              <div>
                <label className="text-xs font-medium text-foreground">Admin Notes (Optional)</label>
                <textarea
                  placeholder="Add brief notes..."
                  value={approvalNotes}
                  onChange={e => setApprovalNotes(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-background px-2 py-1.5 text-xs"
                  rows={2}
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleApprove}
                  disabled={submitting || !verificationStatus.all_required_approved}
                  className="flex-1 flex items-center justify-center gap-1 rounded-md bg-green-600 px-3 py-2 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <CheckCircle size={14} />
                  Accept
                </button>
                <button
                  onClick={() => setVerificationModalOpen(true)}
                  className="flex-1 flex items-center justify-center gap-1 rounded-md bg-red-600 px-3 py-2 text-xs font-medium text-white hover:bg-red-700 transition"
                >
                  <XCircle size={14} />
                  Reject
                </button>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Rejection Reason Modal */}
      <Modal
        open={verificationModalOpen}
        onClose={() => {
          setVerificationModalOpen(false);
          setRejectionReason('');
        }}
        title="Reject Driver Application"
      >
        <div className="space-y-3">
          <div className="rounded-lg border-l-4 border-l-red-500 bg-red-50 p-2.5">
            <p className="text-xs text-red-800">
              ⚠️ Driver <strong>{selectedDriver?.name}</strong> will be notified and can reapply.
            </p>
          </div>

          <div>
            <label className="text-xs font-semibold text-foreground">Reason for Rejection *</label>
            <p className="mt-0.5 text-xs text-muted-foreground">Be specific so driver knows what to fix.</p>
            <textarea
              placeholder="Example: RC document unclear - registration number not visible. Resubmit clearer image."
              value={rejectionReason}
              onChange={e => setRejectionReason(e.target.value)}
              className="mt-1.5 w-full rounded-md border border-border bg-background px-2 py-1.5 text-xs font-normal focus:outline-none focus:ring-2 focus:ring-destructive"
              rows={4}
              minLength={15}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              {rejectionReason.length < 15 ? `${15 - rejectionReason.length} more chars needed` : '✓ Ready'}
            </p>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleReject}
              disabled={submitting || rejectionReason.trim().length < 15}
              className="flex-1 rounded-md bg-destructive px-3 py-2 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {submitting ? 'Rejecting...' : 'Reject'}
            </button>
            <button
              onClick={() => {
                setVerificationModalOpen(false);
                setRejectionReason('');
              }}
              className="flex-1 rounded-md border border-border px-3 py-2 text-xs font-medium text-foreground hover:bg-secondary transition"
            >
              Back
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Admin;
