import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { getShipments } from '../api/client'

const STATUS_COLOR: Record<string, string> = {
  pending:    'var(--amber)',
  in_transit: 'var(--accent)',
  delivered:  'var(--green)',
  cancelled:  'var(--red)',
}

function Sk() {
  return <tr>{[80,80,60,80,80,100].map((w,i) => <td key={i}><div className="sk" style={{ height:13, width:w }} /></td>)}</tr>
}

export default function ShipmentsPage() {
  const [status, setStatus] = useState('')
  const { data, isLoading } = useQuery({
    queryKey: ['shipments', status],
    queryFn: () => getShipments(status ? { status, limit:100 } : { limit:100 }),
    staleTime: 20000,
  })
  const rows: any[] = Array.isArray(data) ? data : ((data as any)?.items ?? [])

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Shipments</h2>
          <p style={{ fontSize:12, color:'var(--muted)', marginTop:3 }}>{rows.length} records</p>
        </div>
        <select value={status} onChange={e => setStatus(e.target.value)}
          style={{
            padding:'7px 10px', fontSize:12,
            background:'var(--surface)', border:'1px solid var(--border)',
            borderRadius:'var(--radius)', color: status ? 'var(--fg)' : 'var(--muted)',
            cursor:'pointer', outline:'none', fontFamily:'inherit',
          }}>
          <option value="">All statuses</option>
          {['pending','in_transit','delivered','cancelled'].map(s => (
            <option key={s} value={s}>{s.replace('_',' ')}</option>
          ))}
        </select>
      </div>

      <div style={{ background:'var(--surface)', border:'1px solid var(--border)' }}>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Product</th><th>Store</th>
              <th className="r">Qty</th><th>Status</th><th className="r">Created</th>
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({length:8}).map((_,i) => <Sk key={i} />)
              : rows.map((s:any, i:number) => {
                  const sc = STATUS_COLOR[s.status] ?? 'var(--muted)'
                  return (
                    <motion.tr key={s.id ?? i}
                      initial={{ opacity:0 }}
                      animate={{ opacity:1 }}
                      transition={{ delay: Math.min(i*0.012, 0.3) }}
                      style={{ borderLeft:`3px solid ${sc}` }}>
                      <td style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--muted)' }}>#{s.id}</td>
                      <td style={{ fontWeight:500 }}>{s.product_name ?? `Product ${s.product_id}`}</td>
                      <td style={{ color:'var(--muted)', fontSize:12 }}>{s.store_name ?? `Store ${s.store_id}`}</td>
                      <td className="r mono" style={{ fontWeight:600 }}>{s.quantity}</td>
                      <td style={{ display:'flex', alignItems:'center', gap:6, border:'none' }}>
                        <span style={{ width:6, height:6, borderRadius:'50%', background:sc, flexShrink:0 }} />
                        <span style={{ fontSize:12, color:sc }}>{s.status?.replace('_',' ')}</span>
                      </td>
                      <td className="r mono" style={{ fontSize:11, color:'var(--muted)' }}>
                        {s.created_at ? new Date(s.created_at).toLocaleDateString() : '—'}
                      </td>
                    </motion.tr>
                  )
                })
            }
          </tbody>
        </table>
      </div>
    </div>
  )
}
