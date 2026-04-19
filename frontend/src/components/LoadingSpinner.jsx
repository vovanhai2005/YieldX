const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  const sizes = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' };

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <div className={`${sizes[size]} relative`}>
        <div className="absolute inset-0 rounded-full border-2 border-blue-500/20" />
        <div
          className={`${sizes[size]} rounded-full border-2 border-transparent border-t-blue-500`}
          style={{ animation: 'spin 0.8s linear infinite' }}
        />
      </div>
      {text && <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{text}</p>}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default LoadingSpinner;
