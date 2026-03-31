import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bus } from 'lucide-react';
import { authApi } from '@/api/auth';
import { useAuth } from '@/contexts/AuthContext';
import { useToastNotify } from '@/components/ToastNotify';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToastNotify();

  const validate = () => {
    const e: Record<string, string> = {};
    if (!email.trim()) e.email = 'Email is required';
    if (!password) e.password = 'Password is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const { data } = await authApi.login({ email, password });
      await login(data.access_token);
      // Get the user data to check role
      const userRes = await authApi.getMe();
      const userRole = userRes.data.role;
      
      // Redirect based on role
      if (userRole === 'admin') {
        navigate('/admin');
      } else if (userRole === 'driver') {
        navigate('/driver/dashboard');
      } else {
        navigate('/home');
      }
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mb-3 flex items-center justify-center gap-2">
            <Bus size={28} className="text-accent" />
            <h1 className="text-2xl font-bold text-foreground">CampusRide</h1>
          </div>
          <p className="text-sm text-muted-foreground">Your campus transport, simplified.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-foreground">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-input bg-card px-3 py-2 text-sm text-foreground outline-none transition-colors duration-150 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder="you@college.edu"
            />
            {errors.email && <p className="mt-1 text-xs text-destructive">{errors.email}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-foreground">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-input bg-card px-3 py-2 text-sm text-foreground outline-none transition-colors duration-150 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder="••••••••"
            />
            {errors.password && <p className="mt-1 text-xs text-destructive">{errors.password}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary py-2.5 text-sm font-semibold text-primary-foreground transition-colors duration-150 hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'Logging in…' : 'Login'}
          </button>
        </form>

        {/* Demo Credentials */}
        <div className="mt-6 space-y-3 rounded-lg border border-border bg-secondary/30 p-3">
          <p className="text-xs font-semibold text-foreground">Demo Credentials</p>
          
          {/* Student */}
          <div className="text-xs">
            <p className="font-medium text-foreground">👤 Student</p>
            <p className="text-muted-foreground">Email: <span className="font-mono">aarav@student.edu</span></p>
            <p className="text-muted-foreground">Pass: <span className="font-mono">Student@123</span></p>
          </div>
          
          {/* Admin */}
          <div className="border-t border-border pt-2">
            <p className="font-medium text-foreground">🔐 Admin</p>
            <p className="text-muted-foreground">Email: <span className="font-mono">admin@campusride.com</span></p>
            <p className="text-muted-foreground">Pass: <span className="font-mono">Admin@123</span></p>
          </div>
        </div>

        <div className="mt-6 space-y-2 border-t border-border pt-4 text-center text-xs">
          <p className="text-muted-foreground">
            🎓 New student?{' '}
            <Link to="/register" className="font-medium text-accent hover:underline">
              Register here
            </Link>
          </p>
          <p className="text-muted-foreground">
            🚗 Driver?{' '}
            <span className="space-x-1">
              <Link to="/driver/login" className="font-medium text-accent hover:underline">Login</Link>
              /
              <Link to="/register-driver" className="font-medium text-accent hover:underline">Register</Link>
            </span>
          </p>
          <p className="text-muted-foreground">
            🔐 Admin user? Use <span className="font-medium text-foreground">"Admin"</span> credentials above to login
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
