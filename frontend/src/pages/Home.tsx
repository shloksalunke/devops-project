import React, { useEffect, useState } from 'react';
import { driversApi, type Driver } from '@/api/drivers';
import Navbar from '@/components/Navbar';
import DriverCard from '@/components/DriverCard';
import SkeletonCard from '@/components/SkeletonCard';
import { useToastNotify } from '@/components/ToastNotify';
import { MapPin, Navigation } from 'lucide-react';

const vehicleFilters = ['All', 'Auto', 'Taxi', 'Car'] as const;

// Common service areas
const serviceAreas = [
  'Nashik Road',
  'CBS to College Road',
  'Panchvati',
  'Gangapur Road',
  'Dwarka Circle',
  'College Road',
  'Trimbak Road',
  'Satpur MIDC',
  'Nashik City',
  'Old Town',
] as const;

const Home: React.FC = () => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('All');
  const [pickupArea, setPickupArea] = useState<string>('');
  const [destinationArea, setDestinationArea] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const { showToast } = useToastNotify();

  const fetchDrivers = async (pickup?: string, destination?: string) => {
    try {
      setLoading(true);
      const { data } = await driversApi.getAll();
      
      // Filter by service area if pickup area is selected
      let filtered = data;
      if (pickup) {
        filtered = filtered.filter(d => 
          d.service_area?.toLowerCase().includes(pickup.toLowerCase()) ||
          pickup.toLowerCase().includes(d.service_area?.toLowerCase() || '')
        );
      }
      
      setDrivers(filtered);
    } catch (error) {
      showToast('Failed to load drivers', 'error');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrivers(pickupArea, destinationArea);
  }, [pickupArea, destinationArea, showToast]);

  // Auto-refresh every 3 seconds for real-time availability
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchDrivers(pickupArea, destinationArea);
    }, 3000);
    
    return () => clearInterval(interval);
  }, [autoRefresh, pickupArea, destinationArea]);

  const filtered = filter === 'All' 
    ? drivers 
    : drivers.filter((d) => d.vehicle_type === filter.toLowerCase());

  const availableDrivers = filtered.filter(d => d.is_available);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Find a Ride</h1>
          <p className="mt-1 text-sm text-muted-foreground">Book a ride to your destination</p>
        </div>

        {/* Location Selection */}
        <div className="mb-6 rounded-lg border border-border bg-card p-6 shadow-sm">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="mb-2 block text-sm font-medium text-foreground">Pickup Point</label>
              <div className="relative">
                <MapPin size={16} className="absolute left-3 top-3 text-muted-foreground" />
                <select
                  value={pickupArea}
                  onChange={(e) => setPickupArea(e.target.value)}
                  className="w-full rounded-md border border-input bg-card py-2 pl-9 pr-3 text-sm text-foreground outline-none transition-colors duration-150 focus:border-accent"
                >
                  <option value="">Select pickup area...</option>
                  {serviceAreas.map((area) => (
                    <option key={area} value={area}>
                      {area}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-foreground">Going To</label>
              <div className="relative">
                <Navigation size={16} className="absolute left-3 top-3 text-muted-foreground" />
                <select
                  value={destinationArea}
                  onChange={(e) => setDestinationArea(e.target.value)}
                  className="w-full rounded-md border border-input bg-card py-2 pl-9 pr-3 text-sm text-foreground outline-none transition-colors duration-150 focus:border-accent"
                >
                  <option value="">Select destination...</option>
                  {serviceAreas.map((area) => (
                    <option key={area} value={area}>
                      {area}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex flex-col justify-end gap-2">
              <button
                onClick={() => setPickupArea('')}
                className="rounded-md border border-border bg-secondary px-4 py-2 text-sm font-medium text-foreground transition-colors duration-150 hover:bg-muted"
              >
                Clear
              </button>
              <label className="flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded border border-input"
                />
                <span>Auto-refresh (Real-time)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6 flex items-center justify-between gap-4">
          <div className="flex gap-1">
            {vehicleFilters.map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded-md px-3 py-2 text-xs font-medium transition-colors duration-150 ${
                  filter === f
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-muted'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
          <div className="text-sm text-muted-foreground">
            <span className="font-medium text-foreground">{availableDrivers.length}</span> available drivers
          </div>
        </div>

        {/* Drivers List */}
        <div>
          {loading ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : availableDrivers.length === 0 ? (
            <div className="rounded-lg border border-border bg-card p-12 text-center">
              <p className="text-muted-foreground">No drivers available for this route right now.</p>
              <p className="mt-2 text-xs text-muted-foreground">Try selecting different pickup/drop points</p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {availableDrivers.map((d) => (
                <DriverCard key={d.id} driver={d} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Home;
