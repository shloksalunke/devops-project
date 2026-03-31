import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/Navbar';
import { LogOut } from 'lucide-react';

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const initials = user?.name?.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-accent text-xl font-bold text-accent-foreground">
              {initials}
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">{user?.name}</h1>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-lg border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-foreground">Ride History</h2>
          <p className="mt-3 text-sm text-muted-foreground">No ride history yet.</p>
        </div>

        <button
          onClick={handleLogout}
          className="mt-6 flex items-center gap-2 rounded-md border border-destructive px-4 py-2 text-sm font-medium text-destructive transition-colors duration-150 hover:bg-destructive hover:text-destructive-foreground"
        >
          <LogOut size={16} /> Logout
        </button>
      </main>
    </div>
  );
};

export default Profile;
