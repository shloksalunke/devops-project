import React from 'react';
import { Link } from 'react-router-dom';
import type { Driver } from '@/api/drivers';
import Badge from './Badge';
import StarRating from './StarRating';

const DriverCard: React.FC<{ driver: Driver }> = ({ driver }) => {
  const initials = driver.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className={`rounded-lg border-2 p-5 shadow-sm transition-all duration-150 hover:shadow-lg ${
      driver.is_available
        ? 'border-success/30 bg-card'
        : 'border-muted/30 bg-muted/20 opacity-60'
    }`}>
      <div className="flex items-start gap-4">
        <div className={`relative flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold ${
          driver.is_available
            ? 'bg-accent text-accent-foreground'
            : 'bg-muted text-muted-foreground'
        }`}>
          {initials}
          {driver.is_available && (
            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-card bg-success"></span>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate text-base font-semibold text-foreground">{driver.name}</h3>
            <Badge variant={driver.is_available ? 'available' : 'busy'} dot />
          </div>
          <div className="mt-1 flex items-center gap-2">
            <Badge variant={driver.vehicle_type} />
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <StarRating value={Math.round(driver.avg_rating)} readonly size={12} />
              <span>{driver.avg_rating.toFixed(1)} · {driver.total_ratings} ratings</span>
            </span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">{driver.service_area}</p>
          {driver.vehicle_details && (
            <p className="text-xs text-muted-foreground">{driver.vehicle_details}</p>
          )}
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        <Link
          to={driver.is_available ? `/drivers/${driver.id}` : '#'}
          className={`flex-1 rounded-md border text-center text-sm font-medium py-2 transition-all duration-150 ${
            driver.is_available
              ? 'border-border bg-secondary text-foreground hover:bg-muted'
              : 'border-muted/50 bg-muted/30 text-muted-foreground cursor-not-allowed'
          }`}
        >
          {driver.is_available ? 'View Details' : 'Driver Offline'}
        </Link>

        {driver.phone ? (
          // Use a tel: link so clicking initiates a phone call on capable systems
          <a
            href={`tel:${driver.phone}`}
            className="inline-flex items-center gap-2 rounded-md border border-transparent bg-accent px-3 py-2 text-xs font-medium text-accent-foreground transition-colors duration-150 hover:opacity-90"
            aria-label={`Call ${driver.name}`}
          >
            Call
          </a>
        ) : (
          <button
            disabled
            className="inline-flex items-center gap-2 rounded-md border border-muted/50 bg-muted/30 px-3 py-2 text-xs font-medium text-muted-foreground"
          >
            No Phone
          </button>
        )}
      </div>
    </div>
  );
};

export default DriverCard;
