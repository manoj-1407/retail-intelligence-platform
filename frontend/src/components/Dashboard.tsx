import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { getSummary, getInventory } from '../api/client'
import { useCountUp } from '../hooks/useCountUp'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid,
} from 'recharts'

const TIP = {
  background:'#0d1525', border:'1px solid #15243a',
  borderRadius:4, color:'#e2ecff', fontSize:12, padding:'6px 10px',
}
const COLORS = ['#2563eb','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4']

function Sk({ h=16, w='100%' }: { h?: number; w?: string|number }) {
  return <div className="sk" style={{ height:h, width:w, borderRadius:3 }} />
}

function KpiBox({ label, value, delta, color }: { label:string; value:number; delta?:string; color:string }) {
  const n = useCountUp(value)
  return (
    <div style={{
      padding:'18px 20px', background:'var(--surface)',
      border:'1px solid var(--border)', borderTop:`3px solid ${color}`,
    }}>
      <div className="label" style={{ marginBottom:10 }}>{label}</div>
      <div style={{ fontSize:28, fontWeight:700, fontFamily:'var(--mono)', color:'var(--fg)', letterSpacing:'-1px' }}>
        {n.toLocaleString()}
      </div>
      {delta && <div style={{ fontSize:11, color:'var(--muted)', marginTop:6 }}>{delta}</div>}
    </div>
  )
}

function HeatRow({ label, qty, max, reorder }: { label:string; qty:number; max:number; reorder:number }) {
  const pct = Math.max(2, (qty / (max || 1)) * 100)
  const c   = qty === 0 ? 'var(--red)' : qty <= reorder ? 'var(--amber)' : 'var(--green)'
  return (
    <div style={{ display:'flex', alignItems:'center', gap:12, padding:'5px 0', borderBottom:'1px solid var(--border)' }}>
      <div style={{ width:120, fontSize:12, color:'var(--muted2)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{label}</div>
      <div style={{ flex:1, height:6, background:'var(--border)', borderRadius:2, overflow:'hidden' }}>
        <div style={{ width:`${pct}%`, height:'100%', background:c, transition:'width 0.6s ease' }} />
      </div>
      <div style={{ width:40, fontFamily:'var(--mono)', fontSize:11, textAlign:'right', color:c }}>{qty}</div>
    </div>
  )
}

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey:['summary'], queryFn:getSummary, refetchInterval:30000 })
  const { data:inv } = useQuery({ queryKey:['inv-dash'], queryFn:() => getInventory({ limit:50 }), staleTime:60000 })
  const d   = (data as any) || {}
  const rows = Array.isArray(inv) ? inv : ((inv as any)?.items ?? [])
  const maxQ = rows.length ? Math.max(...rows.map((r:any) => r.quantity)) : 1

  const kpis = [
    { label:'Products',     value: d.total_products  ?? 0, color:'var(--accent)' },
    { label:'Stores',       value: d.total_stores    ?? 0, color:'var(--accent)' },
    { label:'Shipments',    value: d.total_shipments ?? 0, color:'#8b5cf6'       },
    { label:'Units in Stock', value: d.total_inventory ?? 0, color:'var(--green)' },
    { label:'Low Stock',    value: d.low_stock_count ?? 0, color:'var(--amber)'  },
  ]

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:24 }}>
      <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between' }}>
        <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Overview</h2>
        <span style={{ fontSize:11, color:'var(--muted)' }}>Auto-refreshes every 30s</span>
      </div>

      {/* KPI row */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:1, border:'1px solid var(--border)' }}>
        {isLoading
          ? Array.from({length:5}).map((_,i) => (
              <div key={i} style={{ padding:'18px 20px', background:'var(--surface)' }}>
                <Sk h={10} w="60%" /><div style={{marginTop:12}}><Sk h={28} w="50%" /></div>
              </div>
            ))
          : kpis.map(k => <KpiBox key={k.label} {...k} />)
        }
      </div>

      {/* Charts */}
      <div style={{ display:'grid', gridTemplateColumns:'1.6fr 1fr', gap:16 }}>
        <div style={{ background:'var(--surface)', border:'1px solid var(--border)', padding:'20px 20px 12px' }}>
          <div className="label" style={{ marginBottom:16 }}>Inventory by Category</div>
          {isLoading ? <Sk h={200} /> : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={d.categories ?? []} margin={{ top:4, right:4, left:-28, bottom:0 }}>
                <defs>
                  <linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#2563eb" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="category" tick={{ fill:'#4a6080', fontSize:10 }} />
                <YAxis tick={{ fill:'#4a6080', fontSize:10 }} />
                <Tooltip contentStyle={TIP} />
                <Area type="monotone" dataKey="total_inventory" stroke="#2563eb"
                  strokeWidth={1.5} fill="url(#ga)" name="Units" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
        <div style={{ background:'var(--surface)', border:'1px solid var(--border)', padding:'20px 20px 12px' }}>
          <div className="label" style={{ marginBottom:16 }}>Shipment Status</div>
          {isLoading ? <Sk h={200} /> : (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={d.shipment_stats ?? []} dataKey="count" nameKey="status"
                  cx="50%" cy="50%" outerRadius={70} innerRadius={36} paddingAngle={2}
                  label={({ name, percent }: any) => `${name} ${((percent??0)*100).toFixed(0)}%`}
                  labelLine={{ stroke:'#4a6080' }}>
                  {(d.shipment_stats ?? []).map((_:any, i:number) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={TIP} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Inventory bar heatmap */}
      {rows.length > 0 && (
        <div style={{ background:'var(--surface)', border:'1px solid var(--border)', padding:20 }}>
          <div className="label" style={{ marginBottom:14 }}>Stock Levels by Item</div>
          {rows.slice(0,15).map((r:any, i:number) => (
            <motion.div key={i} initial={{ opacity:0 }} animate={{ opacity:1 }}
              transition={{ delay: i * 0.015 }}>
              <HeatRow
                label={`${r.product_name ?? 'Product'} / ${r.store_name ?? 'Store'}`}
                qty={r.quantity} max={maxQ} reorder={r.reorder_point}
              />
            </motion.div>
          ))}
        </div>
      )}

      {/* Low stock table */}
      {(d.low_stock_items?.length > 0) && (
        <div style={{ background:'var(--surface)', border:'1px solid rgba(239,68,68,0.2)' }}>
          <div style={{ padding:'14px 16px', borderBottom:'1px solid var(--border)', display:'flex', alignItems:'center', gap:8 }}>
            <div style={{ width:8, height:8, borderRadius:'50%', background:'var(--red)', flexShrink:0 }} />
            <span style={{ fontSize:13, fontWeight:500 }}>Low Stock Alerts</span>
            <span style={{ marginLeft:'auto', fontFamily:'var(--mono)', fontSize:12, color:'var(--red)' }}>
              {d.low_stock_items.length}
            </span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Product</th><th>Store</th>
                <th className="r">Qty</th><th className="r">Reorder</th><th className="r">Status</th>
              </tr>
            </thead>
            <tbody>
              {d.low_stock_items.slice(0,10).map((it:any, i:number) => (
                <tr key={i} style={{ borderLeft: it.quantity === 0 ? '3px solid var(--red)' : '3px solid var(--amber)' }}>
                  <td style={{ fontWeight:500 }}>{it.product_name}</td>
                  <td style={{ color:'var(--muted)' }}>{it.store_name}</td>
                  <td className="r mono" style={{ color: it.quantity === 0 ? 'var(--red)' : 'var(--amber)', fontWeight:600 }}>
                    {it.quantity}
                  </td>
                  <td className="r mono" style={{ color:'var(--muted)' }}>{it.reorder_point}</td>
                  <td className="r" style={{ fontSize:11, color: it.quantity === 0 ? 'var(--red)' : 'var(--amber)' }}>
                    {it.quantity === 0 ? 'Out of stock' : 'Low'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
