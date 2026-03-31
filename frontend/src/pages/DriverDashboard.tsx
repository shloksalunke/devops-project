import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { driverApi } from '@/api/driver';
import Navbar from '@/components/Navbar';
import { useToastNotify } from '@/components/ToastNotify';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';
import Badge from '@/components/Badge';

interface DriverStats {
  total_rides: number;
  avg_rating: number;
  total_ratings: number;
  total_earnings: number;
}

interface Rating {
  id: string;
  rating: number;
  comment: string;
  created_at: string;
}

const DriverDashboard: React.FC = () => {
  const { user } = useAuth();
  const [available, setAvailable] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [stats, setStats] = useState<DriverStats | null>(null);
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [loadingStats, setLoadingStats] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const { showToast } = useToastNotify();

  const toggle = async () => {
    setToggling(true);
    try {
      await driverApi.updateAvailability(!available);
      setAvailable(!available);
      showToast(
        `You are now ${!available ? 'available for bookings' : 'offline'}`,
        'success'
      );
    } catch {
      showToast('Failed to update availability', 'error');
    } finally {
      setToggling(false);
    }
  };

  const fetchStats = async () => {
    try {
      const { data } = await driverApi.getRatings();
      setRatings(data);
      
      // Calculate stats from ratings
      if (data.length > 0) {
        const avgRating = (data.reduce((sum, r) => sum + r.rating, 0) / data.length).toFixed(1);
        setStats({
          total_rides: data.length,
          avg_rating: parseFloat(avgRating),
          total_ratings: data.length,
          total_earnings: data.length * 150, // Dummy calculation
        });
      } else {
        setStats({
          total_rides: 0,
          avg_rating: 5.0,
          total_ratings: 0,
          total_earnings: 0,
        });
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoadingStats(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // Auto-refresh every 5 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchStats();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [autoRefresh]);

  if (loadingStats) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="mx-auto max-w-4xl px-4 py-8">
          <div className="text-center text-muted-foreground">Loading dashboard...</div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Welcome back, {user?.name}</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage your availability and view your stats</p>
        </div>

        {/* Availability Toggle */}
        <div className={`mb-6 rounded-lg border-2 p-6 transition-colors duration-150 ${
          available
            ? 'border-success/50 bg-success/5'
            : 'border-muted bg-muted/30'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {available ? (
                <CheckCircle size={24} className="text-success" />
              ) : (
                <Clock size={24} className="text-muted-foreground" />
              )}
              <div>
                <h2 className="text-sm font-medium text-muted-foreground">Online Status</h2>
                <p className={`text-2xl font-bold ${available ? 'text-success' : 'text-muted-foreground'}`}>
                  {available ? 'Online & Available' : 'Offline'}
                </p>
              </div>
            </div>
            <button
              onClick={toggle}
              disabled={toggling}
              className={`relative h-12 w-20 rounded-full transition-all duration-150 ${
                available ? 'bg-success' : 'bg-muted'
              } ${toggling ? 'opacity-50' : 'hover:shadow-md'}`}
            >
              <span
                className={`absolute top-1 h-10 w-10 rounded-full bg-white shadow-sm transition-transform duration-150 ${
                  available ? 'translate-x-9' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            {available
              ? 'You are visible to students searching for rides in your service area'
              : 'You are offline. Turn on availability to accept ride requests'}
          </p>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="mb-6 grid gap-4 md:grid-cols-4">
            <div className="rounded-lg border border-border bg-card p-4">
              <p className="text-xs text-muted-foreground">Total Rides</p>
              <p className="mt-2 text-2xl font-bold text-foreground">{stats.total_rides}</p>
            </div>
            <div className="rounded-lg border border-border bg-card p-4">
              <p className="text-xs text-muted-foreground">Average Rating</p>
              <p className="mt-2 flex items-center gap-1">
                <span className="text-2xl font-bold text-foreground">{stats.avg_rating.toFixed(1)}</span>
                <span className="text-sm text-muted-foreground">/ 5</span>
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-4">
              <p className="text-xs text-muted-foreground">Ratings Count</p>
              <p className="mt-2 text-2xl font-bold text-foreground">{stats.total_ratings}</p>
            </div>
            <div className="rounded-lg border border-border bg-card p-4">
              <p className="text-xs text-muted-foreground">Total Earnings</p>
              <p className="mt-2 text-2xl font-bold text-foreground">₹{stats.total_earnings}</p>
            </div>
          </div>
        )}

        {/* Profile Card */}
        <div className="mb-6 rounded-lg border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-foreground">Your Profile</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-xs text-muted-foreground">Full Name</p>
              <p className="mt-1 font-medium text-foreground">{user?.name}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Email</p>
              <p className="mt-1 font-medium text-foreground">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Recent Ratings */}
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">Recent Ratings</h2>
            <label className="flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border border-input"
              />
              <span>Auto-refresh</span>
            </label>
          </div>

          {ratings.length > 0 ? (
            <div className="space-y-3">
              {ratings.slice(0, 5).map((rating) => (
                <div key={rating.id} className="border-b border-border pb-3 last:border-0">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <span
                          key={i}
                          className={`text-sm ${i < rating.rating ? 'text-yellow-400' : 'text-muted-foreground'}`}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                    <span className="text-sm font-medium text-foreground">{rating.rating.toFixed(1)}</span>
                  </div>
                  {rating.comment && (
                    <p className="mt-1 text-sm text-muted-foreground italic">"{rating.comment}"</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {new Date(rating.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center">
              <AlertCircle size={24} className="mx-auto text-muted-foreground" />
              <p className="mt-2 text-sm text-muted-foreground">No ratings yet. Complete rides to get ratings!</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DriverDashboard;
