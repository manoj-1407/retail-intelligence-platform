import { useCountUp } from '../hooks/useCountUp'

interface Props { label:string; value:number|string; icon?:string; color:string; delay?:number; suffix?:string }

export default function StatCard({ label, value, color, suffix='' }: Props) {
  const raw      = typeof value === 'number' ? value : parseInt(String(value).replace(/,/g,''),10)||0
  const animated = useCountUp(raw)
  return (
    <div style={{
      padding:'18px 20px', background:'var(--surface)',
      border:'1px solid var(--border)', borderTop:`3px solid ${color}`,
    }}>
      <div className="label" style={{ marginBottom:8 }}>{label}</div>
      <div style={{ fontSize:26, fontWeight:700, fontFamily:'var(--mono)', letterSpacing:'-0.8px' }}>
        {animated.toLocaleString()}{suffix}
      </div>
    </div>
  )
}
