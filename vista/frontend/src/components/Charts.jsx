/**
 * Lightweight CSS-only chart components (no external library).
 * Supports: BarChart, DonutChart, TrendLine
 */

export function BarChart({ data, labelKey = 'label', valueKey = 'value', color = 'var(--primary)' }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map(d => d[valueKey] || 0), 1);

  return (
    <div style={{display:'flex',flexDirection:'column',gap:'6px'}}>
      {data.map((d, i) => (
        <div key={i} style={{display:'flex',alignItems:'center',gap:'var(--s3)'}}>
          <span style={{fontSize:'11px',color:'var(--text-muted)',minWidth:'80px',textAlign:'right'}}>{d[labelKey]}</span>
          <div style={{flex:1,height:'18px',background:'var(--bg-secondary)',borderRadius:'3px',overflow:'hidden'}}>
            <div style={{
              height:'100%',width:`${(d[valueKey] / max) * 100}%`,
              background: color,borderRadius:'3px',
              transition:'width 0.6s ease',
            }} />
          </div>
          <span style={{fontSize:'11px',fontWeight:600,color:'var(--text-secondary)',minWidth:'36px'}}>{d[valueKey]}%</span>
        </div>
      ))}
    </div>
  );
}

export function DonutChart({ data, colors = ['var(--danger)', 'var(--warning)', 'var(--success)'] }) {
  if (!data || data.length === 0) return null;
  const total = data.reduce((sum, d) => sum + d.value, 0);
  if (total === 0) return null;

  let cumulative = 0;
  const segments = data.map((d, i) => {
    const pct = (d.value / total) * 100;
    const start = cumulative;
    cumulative += pct;
    return { ...d, pct, start, color: colors[i % colors.length] };
  });

  const gradient = segments.map(s => `${s.color} ${s.start}% ${s.start + s.pct}%`).join(', ');

  return (
    <div style={{display:'flex',alignItems:'center',gap:'var(--s4)'}}>
      <div style={{
        width:'80px',height:'80px',borderRadius:'50%',
        background: `conic-gradient(${gradient})`,
        position:'relative',
      }}>
        <div style={{
          position:'absolute',inset:'18px',borderRadius:'50%',
          background:'var(--surface)',display:'flex',alignItems:'center',justifyContent:'center',
          fontSize:'14px',fontWeight:700,color:'var(--text)',
        }}>{total}</div>
      </div>
      <div style={{display:'flex',flexDirection:'column',gap:'4px'}}>
        {segments.map((s, i) => (
          <div key={i} style={{display:'flex',alignItems:'center',gap:'6px',fontSize:'11px'}}>
            <div style={{width:'8px',height:'8px',borderRadius:'2px',background:s.color}} />
            <span style={{color:'var(--text-secondary)'}}>{s.label}: {s.value} ({s.pct.toFixed(0)}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function TrendLine({ data, valueKey = 'value', height = 60 }) {
  if (!data || data.length < 2) return null;
  const values = data.map(d => d[valueKey]);
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;

  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * 100;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div style={{position:'relative',height:`${height}px`,width:'100%'}}>
      <svg width="100%" height={height} viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" style={{overflow:'visible'}}>
        <polyline points={points} fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <div style={{display:'flex',justifyContent:'space-between',marginTop:'4px'}}>
        {data.map((d, i) => (
          <span key={i} style={{fontSize:'9px',color:'var(--text-muted)'}}>{d.label || ''}</span>
        ))}
      </div>
    </div>
  );
}
