import { motion, AnimatePresence } from 'framer-motion'
import { useInventoryFeed } from '../hooks/useWebSocket'

export interface InventoryEvent {
  product_name:  string
  store_code:    string
  quantity:      number
  reorder_point: number
  updated_at:    string | null
}

interface Props {
  events:     InventoryEvent[]
  connected:  boolean
  standalone?: boolean
}

function Feed({ events, connected }: { events: InventoryEvent[]; connected: boolean }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Live Feed</h2>
          <p style={{ fontSize:12, color:'var(--muted)', marginTop:3 }}>
            Real-time inventory updates via WebSocket
          </p>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:6 }}>
          <span style={{
            width:6, height:6, borderRadius:'50%', flexShrink:0,
            background: connected ? 'var(--green)' : 'var(--amber)',
          }} />
          <span style={{ fontSize:12, color: connected ? 'var(--green)' : 'var(--amber)' }}>
            {connected ? 'Live' : 'Reconnecting'}
          </span>
        </div>
      </div>

      <div style={{ background:'var(--surface)', border:'1px solid var(--border)' }}>
        {events.length === 0 ? (
          <div style={{ padding:'40px 24px', textAlign:'center', color:'var(--muted)', fontSize:13 }}>
            Waiting for events
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Product</th><th>Store</th>
                <th className="r">Quantity</th><th className="r">Reorder</th>
                <th className="r">Updated</th>
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {events.slice(0,20).map((e, i) => {
                  const isLow = e.quantity <= e.reorder_point
                  const c     = e.quantity === 0 ? 'var(--red)' : isLow ? 'var(--amber)' : 'transparent'
                  return (
                    <motion.tr key={`${e.store_code}-${e.product_name}-${i}`}
                      initial={{ opacity:0, x:-6 }}
                      animate={{ opacity:1, x:0 }}
                      exit={{ opacity:0 }}
                      transition={{ duration:0.18 }}
                      style={{ borderLeft:`3px solid ${c}` }}>
                      <td style={{ fontWeight:500 }}>{e.product_name}</td>
                      <td style={{ color:'var(--muted)', fontSize:12 }}>{e.store_code}</td>
                      <td className="r mono" style={{
                        fontWeight:600,
                        color: e.quantity === 0 ? 'var(--red)' : isLow ? 'var(--amber)' : 'var(--fg)',
                      }}>{e.quantity}</td>
                      <td className="r mono" style={{ color:'var(--muted)' }}>{e.reorder_point}</td>
                      <td className="r" style={{ fontSize:11, color:'var(--muted)' }}>
                        {e.updated_at ? new Date(e.updated_at).toLocaleTimeString() : '—'}
                      </td>
                    </motion.tr>
                  )
                })}
              </AnimatePresence>
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default function LiveFeed(_props: Props & { standalone?: boolean }) {
  const { events, connected } = useInventoryFeed('ws://localhost:8000/ws/inventory')
  return <Feed events={events} connected={connected} />
}
