import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { getInventory } from '../api/client'

function Sk() {
  return (
    <tr>
      {[60,120,60,60,60,60].map((w,i) => (
        <td key={i}><div className="sk" style={{ height:13, width:w }} /></td>
      ))}
    </tr>
  )
}

function Spark({ qty, reorder }: { qty: number; reorder: number }) {
  const pts = Array.from({length:8}, (_,i) => {
    const base = Math.max(0, qty + Math.sin(i*1.8 + qty*0.05) * qty * 0.12 + (7-i)*qty*0.025)
    return i === 7 ? qty : base
  })
  const hi = Math.max(...pts), lo = Math.min(...pts), r = hi - lo || 1
  const W = 56, H = 22
  const d = pts.map((p,i) => {
    const x = ((i/7)*W).toFixed(1)
    const y = (H - ((p-lo)/r)*(H-4) - 2).toFixed(1)
    return (i===0?'M':'L')+x+','+y
  }).join(' ')
  const c = qty === 0 ? 'var(--red)' : qty <= reorder ? 'var(--amber)' : 'var(--green)'
  return (
    <svg width={W} height={H} style={{ display:'block', overflow:'visible' }}>
      <path d={d} fill="none" stroke={c} strokeWidth={1.4} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={W} cy={H - ((qty-lo)/r)*(H-4) - 2} r={2} fill={c} />
    </svg>
  )
}

export default function InventoryPage() {
  const [search, setSearch] = useState('')
  const { data, isLoading } = useQuery({
    queryKey:['inventory'], queryFn:() => getInventory({ limit:200 }), staleTime:30000,
  })
  const items: any[] = Array.isArray(data) ? data : ((data as any)?.items ?? [])
  const filtered = useMemo(() =>
    items.filter(r =>
      (r.product_name ?? '').toLowerCase().includes(search.toLowerCase()) ||
      (r.store_name   ?? '').toLowerCase().includes(search.toLowerCase())
    ), [items, search])

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Inventory</h2>
          <p style={{ fontSize:12, color:'var(--muted)', marginTop:3 }}>
            {filtered.length} records across all stores
          </p>
        </div>
        <input value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Filter by product or store"
          style={{
            padding:'7px 12px', width:240, fontSize:13,
            background:'var(--surface)', border:'1px solid var(--border)',
            borderRadius:'var(--radius)', color:'var(--fg)', outline:'none',
            fontFamily:'inherit', transition:'border-color 0.15s',
          }}
          onFocus={e => { e.target.style.borderColor = 'var(--accent)' }}
          onBlur={e  => { e.target.style.borderColor = 'var(--border)' }}
        />
      </div>

      <div style={{ background:'var(--surface)', border:'1px solid var(--border)' }}>
        <table>
          <thead>
            <tr>
              <th>Product</th><th>Store</th>
              <th className="r">Quantity</th><th className="r">Reorder</th>
              <th>Trend</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({length:8}).map((_,i) => <Sk key={i} />)
              : filtered.map((it:any, i:number) => {
                  const isOut = it.quantity === 0
                  const isLow = !isOut && it.quantity <= it.reorder_point
                  const bl    = isOut ? 'var(--red)' : isLow ? 'var(--amber)' : 'transparent'
                  return (
                    <motion.tr key={i}
                      initial={{ opacity:0 }}
                      animate={{ opacity:1 }}
                      transition={{ delay: Math.min(i*0.012, 0.3) }}
                      style={{ borderLeft:`3px solid ${bl}` }}>
                      <td style={{ fontWeight:500 }}>{it.product_name}</td>
                      <td style={{ color:'var(--muted)', fontSize:12 }}>{it.store_name}</td>
                      <td className="r mono" style={{
                        fontWeight:600,
                        color: isOut ? 'var(--red)' : isLow ? 'var(--amber)' : 'var(--fg)',
                      }}>{it.quantity}</td>
                      <td className="r mono" style={{ color:'var(--muted)' }}>{it.reorder_point}</td>
                      <td><Spark qty={it.quantity} reorder={it.reorder_point} /></td>
                      <td style={{ fontSize:11,
                        color: isOut ? 'var(--red)' : isLow ? 'var(--amber)' : 'var(--muted)' }}>
                        {isOut ? 'Out of stock' : isLow ? 'Low' : 'Healthy'}
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
