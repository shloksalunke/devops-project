import React from 'react';

interface StarRatingProps {
  value: number;
  onChange?: (val: number) => void;
  size?: number;
  readonly?: boolean;
}

const StarRating: React.FC<StarRatingProps> = ({ value, onChange, size = 18, readonly = false }) => {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readonly}
          onClick={() => onChange?.(star)}
          className={`transition-colors duration-150 ${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'}`}
          style={{ fontSize: size }}
        >
          <span className={star <= value ? 'text-yellow-400' : 'text-muted'}>★</span>
        </button>
      ))}
    </div>
  );
};

export default StarRating;
