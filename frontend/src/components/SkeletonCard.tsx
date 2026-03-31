import React from 'react';

const SkeletonCard: React.FC = () => (
  <div className="animate-pulse rounded-lg border border-border bg-card p-5">
    <div className="flex items-start gap-4">
      <div className="h-12 w-12 rounded-full bg-muted" />
      <div className="flex-1 space-y-2">
        <div className="h-4 w-32 rounded bg-muted" />
        <div className="h-3 w-48 rounded bg-muted" />
      </div>
    </div>
    <div className="mt-4 h-9 w-full rounded-md bg-muted" />
  </div>
);

export default SkeletonCard;
