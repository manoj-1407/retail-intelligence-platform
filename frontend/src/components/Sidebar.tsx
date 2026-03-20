import { useEffect } from 'react'

// Inline SVG icons — no emoji, no external icon library dependency
const Icons = {
  dashboard: 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
  inventory: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z',
  products:  'M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82zM7 7h.01',
  shipments: 'M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v3m-3 12H9m6 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0M9 17a2 2 0 1 0-4 0 2 2 0 0 0 4 0M9 17H5',
  alerts:    'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9zM13.73 21a2 2 0 0 1-3.46 0',
  benchmarks:'M18 20V10M12 20V4M6 20v-6',
  livefeed:  'M22 12h-4l-3 9L9 3l-3 9H2',
  logout:    'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9',
}

type IconName = keyof typeof Icons

function Ico({ name, size = 14 }: { name: IconName; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
         stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d={Icons[name]} />
    </svg>
  )
}

const NAV: { id: string; label: string; icon: IconName; key: string }[] = [
  { id:'dashboard',  label:'Dashboard',   icon:'dashboard',  key:'d' },
  { id:'inventory',  label:'Inventory',   icon:'inventory',  key:'i' },
  { id:'products',   label:'Products',    icon:'products',   key:'p' },
  { id:'shipments',  label:'Shipments',   icon:'shipments',  key:'s' },
  { id:'alerts',     label:'Alerts',      icon:'alerts',     key:'a' },
  { id:'benchmarks', label:'Benchmarks',  icon:'benchmarks', key:'b' },
  { id:'livefeed',   label:'Live Feed',   icon:'livefeed',   key:'l' },
]

interface Props { active: string; setActive: (s: string) => void; onLogout: () => void }

export default function Sidebar({ active, setActive, onLogout }: Props) {
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === 'INPUT') return
      const n = NAV.find(x => x.key === e.key)
      if (n) setActive(n.id)
    }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [setActive])

  return (
    <div style={{
      width:200, minHeight:'100vh', position:'fixed', top:0, left:0, zIndex:100,
      background:'rgba(5,10,18,0.97)',
      borderRight:'1px solid var(--border)',
      display:'flex', flexDirection:'column',
    }}>
      {/* Brand */}
      <div style={{ padding:'18px 16px 16px', borderBottom:'1px solid var(--border)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:9 }}>
          <div style={{
            width:26, height:26, borderRadius:4, flexShrink:0,
            background:'var(--accent)',
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                 stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div>
            <div style={{ fontSize:13, fontWeight:600, color:'var(--fg)', letterSpacing:'-0.2px' }}>
              Retail Intel
            </div>
            <div style={{ fontSize:10, color:'var(--muted)', letterSpacing:'0.06em', textTransform:'uppercase' }}>
              Platform v1
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex:1, padding:'10px 8px', display:'flex', flexDirection:'column', gap:1 }}>
        <div className="label" style={{ padding:'8px 8px 4px' }}>Navigation</div>
        {NAV.map(item => {
          const on = active === item.id
          return (
            <button key={item.id} onClick={() => setActive(item.id)}
              style={{
                display:'flex', alignItems:'center', gap:9,
                padding:'8px 10px', borderRadius:'var(--radius)', border:'none',
                background: on ? 'rgba(37,99,235,0.1)' : 'transparent',
                borderLeft: on ? '3px solid var(--accent)' : '3px solid transparent',
                color: on ? 'var(--fg)' : 'var(--muted)',
                fontWeight: on ? 500 : 400,
                cursor:'pointer', fontSize:13, textAlign:'left', width:'100%',
                fontFamily:'inherit', transition:'color 0.15s, background 0.15s',
                position:'relative',
              }}>
              <Ico name={item.icon} size={14} />
              <span style={{ flex:1 }}>{item.label}</span>
              <kbd style={{
                fontSize:9, padding:'1px 5px', borderRadius:3,
                background:'rgba(255,255,255,0.04)', border:'1px solid var(--border2)',
                color:'var(--muted)', fontFamily:'var(--mono)',
              }}>{item.key}</kbd>
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding:'10px 8px', borderTop:'1px solid var(--border)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:6, padding:'0 8px 10px' }}>
          <span style={{
            width:6, height:6, borderRadius:'50%', background:'var(--green)',
            display:'inline-block', flexShrink:0,
          }} />
          <span style={{ fontSize:11, color:'var(--muted)' }}>All systems online</span>
        </div>
        <button onClick={onLogout}
          style={{
            width:'100%', padding:'8px 10px', borderRadius:'var(--radius)',
            border:'1px solid rgba(239,68,68,0.15)',
            background:'rgba(239,68,68,0.06)',
            color:'rgba(239,68,68,0.8)', cursor:'pointer', fontSize:12, fontWeight:500,
            fontFamily:'inherit', display:'flex', alignItems:'center', gap:8,
            transition:'background 0.15s',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(239,68,68,0.1)' }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(239,68,68,0.06)' }}>
          <Ico name="logout" size={13} />
          Sign Out
        </button>
      </div>
    </div>
  )
}
