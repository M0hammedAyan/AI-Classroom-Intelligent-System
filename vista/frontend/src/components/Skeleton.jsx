/**
 * Loading skeleton components — shimmer placeholders.
 */

export function SkeletonLine({ width = '100%', height = '14px' }) {
  return <div className="v-skeleton" style={{ width, height, marginBottom: '8px' }} />;
}

export function SkeletonCard() {
  return (
    <div className="v-card" style={{ padding: 'var(--s5)' }}>
      <SkeletonLine width="40%" height="12px" />
      <SkeletonLine width="60%" height="24px" />
      <SkeletonLine width="30%" height="10px" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }) {
  return (
    <div className="v-table-container" style={{ padding: 'var(--s4)' }}>
      <SkeletonLine width="30%" height="16px" />
      <div style={{ marginTop: 'var(--s4)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} style={{ display: 'flex', gap: 'var(--s4)' }}>
            <SkeletonLine width="20%" height="14px" />
            <SkeletonLine width="35%" height="14px" />
            <SkeletonLine width="15%" height="14px" />
            <SkeletonLine width="20%" height="14px" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonDashboard() {
  return (
    <div>
      <SkeletonLine width="200px" height="22px" />
      <SkeletonLine width="150px" height="13px" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--s4)', marginTop: 'var(--s6)' }}>
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <div style={{ marginTop: 'var(--s6)' }}>
        <SkeletonTable rows={4} />
      </div>
    </div>
  );
}
