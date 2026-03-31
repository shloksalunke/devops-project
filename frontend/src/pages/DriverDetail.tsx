import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { driversApi, type Driver } from '@/api/drivers';
import Navbar from '@/components/Navbar';
import Badge from '@/components/Badge';
import StarRating from '@/components/StarRating';
import { useToastNotify } from '@/components/ToastNotify';
import { ArrowLeft, Phone, Car, MapPin, Star } from 'lucide-react';

const DriverDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [driver, setDriver] = useState<Driver | null>(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [hasRated, setHasRated] = useState(false);
  const { showToast } = useToastNotify();

  useEffect(() => {
    const fetch = async () => {
      try {
        const { data } = await driversApi.getById(id!);
        setDriver(data);
      } catch {
        showToast('Failed to load driver', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [id, showToast]);

  const handleRate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) return;
    setSubmitting(true);
    try {
      await driversApi.rate(id!, { rating, comment });
      showToast('Rating submitted!', 'success');
      setHasRated(true);
    } catch {
      showToast('Failed to submit rating', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const initials = driver?.name?.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <Link to="/home" className="mb-6 inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors duration-150 hover:text-foreground">
          <ArrowLeft size={16} /> Back to Drivers
        </Link>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          </div>
        ) : !driver ? (
          <p className="py-16 text-center text-muted-foreground">Driver not found.</p>
        ) : (
          <>
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="flex items-center gap-4">
                <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-full bg-accent text-xl font-bold text-accent-foreground">
                  {initials}
                </div>
                <div>
                  <h1 className="text-xl font-bold text-foreground">{driver.name}</h1>
                  <div className="mt-1 flex items-center gap-2">
                    <Badge variant={driver.vehicle_type} />
                    <Badge variant={driver.is_available ? 'available' : 'busy'} dot />
                  </div>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Phone size={16} className="text-muted-foreground" />
                  <span className="text-foreground">{driver.phone}</span>
                  <a href={`tel:${driver.phone}`} className="ml-auto rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-accent-foreground transition-colors duration-150 hover:opacity-90">
                    Call Driver
                  </a>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Car size={16} className="text-muted-foreground" />
                  <span className="text-foreground">{driver.vehicle_details}</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <MapPin size={16} className="text-muted-foreground" />
                  <span className="text-foreground">{driver.service_area}</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Star size={16} className="text-muted-foreground" />
                  <span className="text-foreground">{driver.avg_rating.toFixed(1)} out of 5 ({driver.total_ratings} ratings)</span>
                </div>
              </div>
            </div>

            {/* Ratings */}
            <div className="mt-6 rounded-lg border border-border bg-card p-6">
              <h2 className="text-lg font-semibold text-foreground">Ratings</h2>

              {driver.ratings && driver.ratings.length > 0 ? (
                <div className="mt-4 space-y-3">
                  {driver.ratings.slice(0, 5).map((r) => (
                    <div key={r.id} className="border-b border-border pb-3 last:border-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-foreground">{r.user_name}</span>
                        <span className="text-xs text-muted-foreground">{new Date(r.created_at).toLocaleDateString()}</span>
                      </div>
                      <StarRating value={r.rating} readonly size={14} />
                      {r.comment && <p className="mt-1 text-sm text-muted-foreground">{r.comment}</p>}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-3 text-sm text-muted-foreground">No ratings yet.</p>
              )}

              {/* Rate form */}
              {hasRated ? (
                <p className="mt-4 text-sm text-muted-foreground">You rated this driver ★ {rating}</p>
              ) : (
                <form onSubmit={handleRate} className="mt-6 border-t border-border pt-4">
                  <h3 className="text-sm font-medium text-foreground">Rate this driver</h3>
                  <div className="mt-2">
                    <StarRating value={rating} onChange={setRating} size={24} />
                  </div>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Leave a comment (optional)"
                    rows={3}
                    className="mt-3 w-full rounded-md border border-input bg-card px-3 py-2 text-sm text-foreground outline-none transition-colors duration-150 focus:border-accent"
                  />
                  <button
                    type="submit"
                    disabled={submitting || rating === 0}
                    className="mt-3 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors duration-150 hover:opacity-90 disabled:opacity-50"
                  >
                    {submitting ? 'Submitting…' : 'Submit Rating'}
                  </button>
                </form>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default DriverDetail;
