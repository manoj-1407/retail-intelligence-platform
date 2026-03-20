import { useInventoryFeed } from '../hooks/useWebSocket'
import { motion, AnimatePresence } from 'framer-motion'

export default function AlertsPage() {
  const { events, connected } = useInventoryFeed('ws://localhost:8000/ws/inventory')
  const alerts = events.filter(e => e.quantity <= e.reorder_point)

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Live Alerts</h2>
          <p style={{ fontSize:12, color:'var(--muted)', marginTop:3 }}>
            Items at or below reorder threshold
          </p>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:6 }}>
          <span style={{
            width:6, height:6, borderRadius:'50%', flexShrink:0,
            background: connected ? 'var(--green)' : 'var(--muted)',
          }} />
          <span style={{ fontSize:12, color: connected ? 'var(--green)' : 'var(--muted)' }}>
            {connected ? 'WebSocket live' : 'Connecting'}
          </span>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div style={{
          padding:'48px 24px', background:'var(--surface)',
          border:'1px solid var(--border)', textAlign:'center',
        }}>
          <div style={{ fontSize:13, color:'var(--muted)' }}>
            {connected ? 'No items below reorder threshold' : 'Waiting for WebSocket connection'}
          </div>
        </div>
      ) : (
        <div style={{ background:'var(--surface)', border:'1px solid var(--border)' }}>
          <table>
            <thead>
              <tr>
                <th>Product</th><th>Store</th>
                <th className="r">Quantity</th><th className="r">Reorder Point</th>
                <th className="r">Updated</th>
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {alerts.map((a, i) => {
                  const isOut = a.quantity === 0
                  const c     = isOut ? 'var(--red)' : 'var(--amber)'
                  return (
                    <motion.tr key={`${a.store_code}-${a.product_name}`}
                      initial={{ opacity:0, x:-8 }}
                      animate={{ opacity:1, x:0 }}
                      exit={{ opacity:0 }}
                      transition={{ delay: i * 0.025 }}
                      style={{ borderLeft:`3px solid ${c}` }}>
                      <td style={{ fontWeight:500 }}>{a.product_name}</td>
                      <td style={{ color:'var(--muted)', fontSize:12 }}>{a.store_code}</td>
                      <td className="r mono" style={{ fontWeight:700, color:c }}>{a.quantity}</td>
                      <td className="r mono" style={{ color:'var(--muted)' }}>{a.reorder_point}</td>
                      <td className="r" style={{ fontSize:11, color:'var(--muted)' }}>
                        {a.updated_at ? new Date(a.updated_at).toLocaleTimeString() : '—'}
                      </td>
                    </motion.tr>
                  )
                })}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
