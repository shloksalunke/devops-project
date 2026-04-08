import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/api/auth';
import { useToastNotify } from '@/components/ToastNotify';
import { CheckCircle, AlertCircle, FileUp, Clock } from 'lucide-react';

const DriverRegister: React.FC = () => {
  const [form, setForm] = useState({ name: '', phone: '', email: '', password: '', confirm: '', vehicle_type: 'auto', vehicle_details: '', service_area: '' });
  const [idFile, setIdFile] = useState<File | null>(null);
  const [licenseFile, setLicenseFile] = useState<File | null>(null);
  const [rcFile, setRcFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [driverEmail, setDriverEmail] = useState('');
  const { showToast } = useToastNotify();
  const nav = useNavigate();

  const set = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirm) return showToast('Passwords do not match', 'error');
    if (!idFile || !licenseFile) return showToast('ID and License documents are required', 'error');
    
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('name', form.name);
      fd.append('phone', form.phone);
      fd.append('email', form.email);
      fd.append('password', form.password);
      fd.append('vehicle_type', form.vehicle_type);
      if (form.vehicle_details) fd.append('vehicle_details', form.vehicle_details);
      if (form.service_area) fd.append('service_area', form.service_area);
      fd.append('id_document', idFile);
      fd.append('license_document', licenseFile);
      if (rcFile) fd.append('rc_document', rcFile);

      await authApi.registerDriver(fd);
      setDriverEmail(form.email);
      setRegistered(true);
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (registered) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="w-full max-w-md">
          {/* Success Message */}
          <div className="rounded-lg border-2 border-green-200 bg-green-50 p-6 text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-600" />
            <h1 className="mt-4 text-2xl font-bold text-green-900">Registration Submitted!</h1>
            <p className="mt-2 text-sm text-green-800">
              Your driver profile has been created and is awaiting admin verification.
            </p>
          </div>

          {/* Verification Status */}
          <div className="mt-6 space-y-4">
            <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
              <div className="flex items-center gap-3">
                <Clock className="h-5 w-5 text-yellow-600" />
                <div>
                  <h3 className="font-semibold text-yellow-900">Verification Status: PENDING</h3>
                  <p className="text-sm text-yellow-800">Our admin team will review your documents within 24 hours</p>
                </div>
              </div>
            </div>

            {/* Required Documents */}
            <div className="rounded-lg border border-border bg-card p-4">
              <h3 className="font-semibold text-foreground">Documents Submitted</h3>
              <div className="mt-3 space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-foreground">Government ID</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-foreground">Driving License (Valid per RTO)</span>
                </div>
                <div className="flex items-center gap-2">
                  {rcFile ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm text-foreground">Vehicle Registration Certificate (RC)</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-5 w-5 text-orange-500" />
                      <span className="text-sm text-muted-foreground">Vehicle RC (Optional but recommended)</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* What Happens Next */}
            <div className="rounded-lg border border-border bg-card p-4">
              <h3 className="font-semibold text-foreground">What Happens Next?</h3>
              <ol className="mt-3 space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="font-semibold text-foreground">1.</span>
                  <span>Admin verifies your documents for authenticity</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-foreground">2.</span>
                  <span>RTO compliance check on driving license & RC</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-foreground">3.</span>
                  <span>Your profile becomes visible to students</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-foreground">4.</span>
                  <span>You can start accepting ride requests</span>
                </li>
              </ol>
            </div>

            {/* Contact Info */}
            <div className="rounded-lg border border-border bg-card p-4">
              <p className="text-xs text-muted-foreground">
                A verification notification will be sent to <span className="font-semibold">{driverEmail}</span>
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                Questions? Contact our support team. In the meantime, complete your profile and add profile photo.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4">
              <button
                onClick={() => nav('/driver-login')}
                className="flex-1 rounded-md bg-primary px-4 py-2.5 text-white font-medium hover:opacity-90"
              >
                Back to Login
              </button>
              <button
                onClick={() => nav('/')}
                className="flex-1 rounded-md border border-border px-4 py-2.5 font-medium hover:bg-secondary"
              >
                Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold">Driver Registration</h1>
        <p className="mt-1 text-sm text-muted-foreground">Join our platform as a verified RTO-compliant driver</p>
        
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {/* Personal Info */}
          <div>
            <label className="block text-sm font-medium mb-1">Full Name *</label>
            <input
              placeholder="Enter your full name"
              value={form.name}
              onChange={e => set('name', e.target.value)}
              required
              className="w-full rounded-md border px-3 py-2 text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium mb-1">Phone *</label>
              <input
                placeholder="10-digit number"
                value={form.phone}
                onChange={e => set('phone', e.target.value)}
                required
                className="w-full rounded-md border px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email *</label>
              <input
                type="email"
                placeholder="your@email.com"
                value={form.email}
                onChange={e => set('email', e.target.value)}
                required
                className="w-full rounded-md border px-3 py-2 text-sm"
              />
            </div>
          </div>

          {/* Password */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium mb-1">Password *</label>
              <input
                type="password"
                placeholder="Min 8 characters"
                value={form.password}
                onChange={e => set('password', e.target.value)}
                required
                className="w-full rounded-md border px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Confirm *</label>
              <input
                type="password"
                placeholder="Confirm password"
                value={form.confirm}
                onChange={e => set('confirm', e.target.value)}
                required
                className="w-full rounded-md border px-3 py-2 text-sm"
              />
            </div>
          </div>

          {/* Vehicle Info */}
          <div>
            <label className="block text-sm font-medium mb-1">Vehicle Type *</label>
            <select
              value={form.vehicle_type}
              onChange={e => set('vehicle_type', e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="auto">Auto (3-wheeler)</option>
              <option value="taxi">Taxi (4-wheeler)</option>
              <option value="car">Car (Personal)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Vehicle Details</label>
            <input
              placeholder="e.g., Maruti Swift, Toyota Innova"
              value={form.vehicle_details}
              onChange={e => set('vehicle_details', e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Service Area</label>
            <input
              placeholder="e.g., SawalDe, Nardana Railway Station, Shirpur"
              value={form.service_area}
              onChange={e => set('service_area', e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            />
          </div>

          {/* Documents */}
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
            <p className="text-xs font-medium text-yellow-900">Required Documents for RTO Verification</p>
            <p className="mt-1 text-xs text-yellow-800">All documents must be clear, valid, and not expired</p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Government ID (Aadhar/Passport) * {idFile && <CheckCircle className="inline h-4 w-4 text-green-600" />}</label>
            <div className="rounded-md border-2 border-dashed border-border bg-secondary/50 p-3 text-center">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={e => setIdFile(e.target.files?.[0] ?? null)}
                className="block w-full text-xs text-muted-foreground file:mr-2 file:px-3 file:py-1 file:rounded file:border-0 file:bg-primary file:text-white file:cursor-pointer"
              />
              {idFile && <p className="mt-1 text-xs text-green-600 font-medium">✓ {idFile.name}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Driving License (Valid per RTO) * {licenseFile && <CheckCircle className="inline h-4 w-4 text-green-600" />}</label>
            <div className="rounded-md border-2 border-dashed border-border bg-secondary/50 p-3 text-center">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={e => setLicenseFile(e.target.files?.[0] ?? null)}
                className="block w-full text-xs text-muted-foreground file:mr-2 file:px-3 file:py-1 file:rounded file:border-0 file:bg-primary file:text-white file:cursor-pointer"
              />
              {licenseFile && <p className="mt-1 text-xs text-green-600 font-medium">✓ {licenseFile.name}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Vehicle Registration Certificate (RC) {rcFile && <CheckCircle className="inline h-4 w-4 text-green-600" />}</label>
            <p className="text-xs text-muted-foreground mb-2">Upload your vehicle's RC for additional verification points</p>
            <div className="rounded-md border-2 border-dashed border-border bg-secondary/50 p-3 text-center">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={e => setRcFile(e.target.files?.[0] ?? null)}
                className="block w-full text-xs text-muted-foreground file:mr-2 file:px-3 file:py-1 file:rounded file:border-0 file:bg-primary file:text-white file:cursor-pointer"
              />
              {rcFile && <p className="mt-1 text-xs text-green-600 font-medium">✓ {rcFile.name}</p>}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary py-2.5 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {loading ? 'Submitting Documents...' : 'Submit Registration for Verification'}
          </button>

          <p className="text-center text-xs text-muted-foreground">
            Already have an account?{' '}
            <button type="button" onClick={() => nav('/driver-login')} className="font-semibold text-primary hover:underline">
              Login here
            </button>
          </p>
        </form>
      </div>
    </div>
  );
};

export default DriverRegister;
