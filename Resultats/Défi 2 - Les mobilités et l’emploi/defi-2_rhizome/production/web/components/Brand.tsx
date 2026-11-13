export function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`wordmark ${className}`}>
      <span>Eclo</span>
      <span>Work</span>
    </span>
  );
}

export function Flower() {
  return (
    <svg
      className="flower"
      viewBox="0 0 40 40"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M17 1h6v10l7-7 4 4-7 9h12v6H27l7 9-4 4-7-7v10h-6V29l-9 7-4-4 7-9H1v-6h10L4 8l4-4 9 7V1Z" />
    </svg>
  );
}
