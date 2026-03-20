import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { getProducts } from '../api/client'

function Sk() {
  return <tr>{[180,80,70,70,70,60].map((w,i) => <td key={i}><div className="sk" style={{ height:13, width:w }} /></td>)}</tr>
}

export default function ProductsPage() {
  const [search, setSearch] = useState('')
  const [cat, setCat]       = useState<string|null>(null)
  const { data, isLoading } = useQuery({ queryKey:['products'], queryFn:() => getProducts({ limit:200 }), staleTime:60000 })
  const all: any[]   = Array.isArray(data) ? data : ((data as any)?.items ?? [])
  const cats         = [...new Set(all.map(p => p.category).filter(Boolean))] as string[]
  const filtered     = useMemo(() => all.filter(p => {
    const q = search.toLowerCase()
    return (!q || (p.name??'').toLowerCase().includes(q) || (p.sku??'').toLowerCase().includes(q))
        && (!cat || p.category === cat)
  }), [all, search, cat])

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', flexWrap:'wrap', gap:12 }}>
        <div>
          <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Products</h2>
          <p style={{ fontSize:12, color:'var(--muted)', marginTop:3 }}>
            {filtered.length} of {all.length}
          </p>
        </div>
        <div style={{ display:'flex', gap:8, alignItems:'center', flexWrap:'wrap' }}>
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search name or SKU"
            style={{
              padding:'7px 12px', width:200, fontSize:13,
              background:'var(--surface)', border:'1px solid var(--border)',
              borderRadius:'var(--radius)', color:'var(--fg)', outline:'none',
              fontFamily:'inherit', transition:'border-color 0.15s',
            }}
            onFocus={e => { e.target.style.borderColor = 'var(--accent)' }}
            onBlur={e  => { e.target.style.borderColor = 'var(--border)' }} />
          <select value={cat ?? ''} onChange={e => setCat(e.target.value || null)}
            style={{
              padding:'7px 10px', fontSize:12,
              background:'var(--surface)', border:'1px solid var(--border)',
              borderRadius:'var(--radius)', color: cat ? 'var(--fg)' : 'var(--muted)',
              cursor:'pointer', outline:'none', fontFamily:'inherit',
            }}>
            <option value="">All categories</option>
            {cats.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
      </div>

      <div style={{ background:'var(--surface)', border:'1px solid var(--border)' }}>
        <table>
          <thead>
            <tr>
              <th>Name</th><th>SKU</th><th>Category</th>
              <th className="r">Unit Cost</th><th className="r">Unit Price</th><th className="r">Margin</th>
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({length:6}).map((_,i) => <Sk key={i} />)
              : filtered.map((p:any, i:number) => {
                  const cost   = parseFloat(p.unit_cost  ?? p.cost_price  ?? 0)
                  const price  = parseFloat(p.unit_price ?? p.price ?? 0)
                  const margin = price > 0 ? ((price - cost) / price * 100) : 0
                  const mc     = margin > 40 ? 'var(--green)' : margin > 20 ? 'var(--amber)' : 'var(--red)'
                  return (
                    <motion.tr key={p.id ?? i}
                      initial={{ opacity:0 }}
                      animate={{ opacity:1 }}
                      transition={{ delay: Math.min(i*0.012, 0.3) }}>
                      <td style={{ fontWeight:500 }}>{p.name}</td>
                      <td style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--muted)' }}>{p.sku}</td>
                      <td style={{ fontSize:12, color:'var(--muted2)' }}>{p.category}</td>
                      <td className="r mono" style={{ color:'var(--muted)' }}>${cost.toFixed(2)}</td>
                      <td className="r mono" style={{ fontWeight:600 }}>${price.toFixed(2)}</td>
                      <td className="r mono" style={{ color:mc, fontWeight:600 }}>{margin.toFixed(1)}%</td>
                    </motion.tr>
                  )
                })
            }
            {!isLoading && filtered.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign:'center', color:'var(--muted)', padding:'32px 0' }}>
                No products match your filter
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
