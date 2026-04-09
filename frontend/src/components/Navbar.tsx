import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Bus, ChevronDown, LogOut, User } from 'lucide-react';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <nav className="sticky top-0 z-40 border-b border-border bg-card">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-lg font-bold text-foreground">
            <Bus size={22} className="text-accent" />
            CampusRide
          </Link>
          {/* Quick nav links based on role */}
          {user?.role === 'admin' && (
            <Link to="/admin" className="ml-4 text-sm font-medium text-muted-foreground hover:text-foreground">Admin</Link>
          )}
          {user?.role === 'driver' && (
            <Link to="/driver/dashboard" className="ml-4 text-sm font-medium text-muted-foreground hover:text-foreground">Driver Dashboard</Link>
          )}
          {user?.role === 'student' && (
            <Link to="/home" className="ml-4 text-sm font-medium text-muted-foreground hover:text-foreground">Home</Link>
          )}
        </div>

        {user && (
          <div className="relative" ref={ref}>
            <button
              onClick={() => setOpen(!open)}
              className="flex items-center gap-2 rounded-md px-2 py-1 transition-colors duration-150 hover:bg-secondary"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-xs font-semibold text-accent-foreground">
                {initials}
              </div>
              <span className="hidden text-sm font-medium text-foreground sm:block">{user.name}</span>
              <ChevronDown size={14} className="text-muted-foreground" />
            </button>

            {open && (
              <div className="absolute right-0 mt-1 w-44 rounded-lg border border-border bg-card py-1 shadow-md">
                <Link
                  to="/profile"
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-foreground transition-colors duration-150 hover:bg-secondary"
                >
                  <User size={14} /> Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 px-4 py-2 text-sm text-destructive transition-colors duration-150 hover:bg-secondary"
                >
                  <LogOut size={14} /> Logout
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
