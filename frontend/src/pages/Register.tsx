import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bus } from 'lucide-react';
import { authApi } from '@/api/auth';
import { useToastNotify } from '@/components/ToastNotify';

const Register: React.FC = () => {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useToastNotify();

  const set = (key: string, val: string) => setForm((p) => ({ ...p, [key]: val }));

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.name.trim()) e.name = 'Name is required';
    if (!form.email.trim()) e.email = 'Email is required';
    if (form.password.length < 6) e.password = 'Min 6 characters';
    if (form.password !== form.confirm) e.confirm = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await authApi.register({ name: form.name, email: form.email, password: form.password, role: 'student' });
      showToast('Account created! Please login.', 'success');
      navigate('/login');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { key: 'name', label: 'Full Name', type: 'text', placeholder: 'John Doe' },
    { key: 'email', label: 'College Email', type: 'email', placeholder: 'you@college.edu' },
    { key: 'password', label: 'Password', type: 'password', placeholder: '••••••••' },
    { key: 'confirm', label: 'Confirm Password', type: 'password', placeholder: '••••••••' },
  ];

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mb-3 flex items-center justify-center gap-2">
            <Bus size={28} className="text-accent" />
            <h1 className="text-2xl font-bold text-foreground">CampusRide</h1>
          </div>
          <p className="text-sm text-muted-foreground">Create your student account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {fields.map((f) => (
            <div key={f.key}>
              <label className="mb-1 block text-sm font-medium text-foreground">{f.label}</label>
              <input
                type={f.type}
                value={form[f.key as keyof typeof form]}
                onChange={(e) => set(f.key, e.target.value)}
                className="w-full rounded-md border border-input bg-card px-3 py-2 text-sm text-foreground outline-none transition-colors duration-150 focus:border-accent focus:ring-1 focus:ring-accent"
                placeholder={f.placeholder}
              />
              {errors[f.key] && <p className="mt-1 text-xs text-destructive">{errors[f.key]}</p>}
            </div>
          ))}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary py-2.5 text-sm font-semibold text-primary-foreground transition-colors duration-150 hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'Creating…' : 'Create Account'}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-accent hover:underline">Back to login</Link>
        </p>
        <p className="mt-2 text-center text-sm text-muted-foreground">
          Are you a driver? <Link to="/register-driver" className="font-medium text-accent hover:underline">Register as Driver</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
