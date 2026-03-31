import React from 'react';

type BadgeVariant = 'auto' | 'taxi' | 'car' | 'available' | 'busy';

const styles: Record<BadgeVariant, string> = {
  auto: 'bg-orange-100 text-orange-700',
  taxi: 'bg-blue-100 text-blue-700',
  car: 'bg-green-100 text-green-700',
  available: 'bg-green-100 text-green-700',
  busy: 'bg-red-100 text-red-700',
};

const labels: Record<BadgeVariant, string> = {
  auto: 'Auto',
  taxi: 'Taxi',
  car: 'Car',
  available: 'Available',
  busy: 'Busy',
};

interface BadgeProps {
  variant: BadgeVariant;
  dot?: boolean;
}

const Badge: React.FC<BadgeProps> = ({ variant, dot }) => {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[variant]}`}>
      {dot && (
        <span className={`h-1.5 w-1.5 rounded-full ${variant === 'available' ? 'bg-green-500' : 'bg-red-500'}`} />
      )}
      {labels[variant]}
    </span>
  );
};

export default Badge;
