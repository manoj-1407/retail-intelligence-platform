import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'

interface Props { onLogin: (u: string, p: string) => Promise<void>; error: string }

export default function LoginPage({ onLogin, error }: Props) {
  const ref    = useRef<HTMLCanvasElement>(null)
  const [user, setUser]     = useState('')
  const [pass, setPass]     = useState('')
  const [busy, setBusy]     = useState(false)

  useEffect(() => {
    const cv = ref.current as HTMLCanvasElement
    if (!cv) return
    const ctx = cv.getContext('2d')!
    let id    = 0
    const resize = () => { cv.width = window.innerWidth; cv.height = window.innerHeight }
    resize()
    window.addEventListener('resize', resize)

    type P = { x:number; y:number; vx:number; vy:number; r:number }
    const pts: P[] = Array.from({length:70}, () => ({
      x: Math.random()*cv.width,  y: Math.random()*cv.height,
      vx:(Math.random()-0.5)*0.35, vy:(Math.random()-0.5)*0.35,
      r: Math.random()*1.2+0.5,
    }))

    function draw() {
      ctx.clearRect(0,0,cv.width,cv.height)
      const g = ctx.createRadialGradient(cv.width/2,cv.height/2,0,cv.width/2,cv.height/2,cv.width*0.7)
      g.addColorStop(0,'#0a1422'); g.addColorStop(1,'#050a0f')
      ctx.fillStyle = g; ctx.fillRect(0,0,cv.width,cv.height)
      for (let i=0; i<pts.length; i++) {
        for (let j=i+1; j<pts.length; j++) {
          const d = Math.hypot(pts[i].x-pts[j].x, pts[i].y-pts[j].y)
          if (d < 110) {
            ctx.beginPath()
            ctx.strokeStyle = `rgba(37,99,235,${0.10*(1-d/110)})`
            ctx.lineWidth = 0.5
            ctx.moveTo(pts[i].x,pts[i].y); ctx.lineTo(pts[j].x,pts[j].y)
            ctx.stroke()
          }
        }
        ctx.beginPath(); ctx.arc(pts[i].x,pts[i].y,pts[i].r,0,Math.PI*2)
        ctx.fillStyle = 'rgba(60,120,220,0.5)'; ctx.fill()
        pts[i].x += pts[i].vx; pts[i].y += pts[i].vy
        if (pts[i].x<0||pts[i].x>cv.width)  pts[i].vx *= -1
        if (pts[i].y<0||pts[i].y>cv.height) pts[i].vy *= -1
      }
      id = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(id); window.removeEventListener('resize',resize) }
  }, [])

  async function submit() {
    if (!user || !pass) return
    setBusy(true)
    try { await onLogin(user, pass) } finally { setBusy(false) }
  }

  return (
    <div style={{ position:'relative', width:'100vw', height:'100vh', overflow:'hidden' }}>
      <canvas ref={ref} style={{ position:'absolute', inset:0 }} />
      <div style={{ position:'relative', zIndex:10, display:'flex', alignItems:'center', justifyContent:'center', width:'100%', height:'100%' }}>
        <motion.div
          initial={{ opacity:0, y:24, scale:0.97 }}
          animate={{ opacity:1, y:0,  scale:1 }}
          transition={{ duration:0.45, ease:[0.16,1,0.3,1] }}
          style={{
            width:380, padding:'40px 36px',
            background:'rgba(8,14,24,0.9)',
            backdropFilter:'blur(20px)',
            border:'1px solid var(--border)',
            boxShadow:'0 8px 48px rgba(0,0,0,0.7)',
          }}>
          <div style={{ marginBottom:28 }}>
            <div style={{
              width:32, height:32, marginBottom:16,
              background:'var(--accent)',
              display:'flex', alignItems:'center', justifyContent:'center',
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div style={{ fontSize:17, fontWeight:600, color:'var(--fg)', letterSpacing:'-0.4px' }}>
              Retail Intelligence Platform
            </div>
            <div style={{ fontSize:12, color:'var(--muted)', marginTop:4 }}>
              Sign in to continue
            </div>
          </div>

          {[
            { label:'Username', val:user, set:setUser, type:'text',     ph:'Enter username', ac:'username'         },
            { label:'Password', val:pass, set:setPass, type:'password', ph:'Enter password', ac:'current-password' },
          ].map(({label,val,set,type,ph,ac}) => (
            <div key={label} style={{ marginBottom:14 }}>
              <label className="label" style={{ display:'block', marginBottom:6 }}>{label}</label>
              <input type={type} value={val} placeholder={ph}
                autoComplete={ac}
                onChange={e => set(e.target.value)}
                onKeyDown={e => e.key==='Enter' && submit()}
                style={{
                  width:'100%', padding:'9px 12px',
                  background:'rgba(255,255,255,0.03)',
                  border:'1px solid var(--border)', color:'var(--fg)',
                  fontSize:13, outline:'none', fontFamily:'inherit',
                  transition:'border-color 0.15s',
                }}
                onFocus={e => { e.target.style.borderColor = 'var(--accent)' }}
                onBlur={e  => { e.target.style.borderColor = 'var(--border)' }}
              />
            </div>
          ))}

          {error && (
            <motion.div initial={{ opacity:0, y:-4 }} animate={{ opacity:1, y:0 }}
              style={{
                padding:'8px 12px', marginBottom:12, fontSize:12,
                background:'rgba(239,68,68,0.08)', border:'1px solid rgba(239,68,68,0.2)',
                color:'rgba(239,68,68,0.9)',
              }}>{error}</motion.div>
          )}

          <button onClick={submit} disabled={busy || !user || !pass}
            style={{
              width:'100%', padding:'10px', marginTop:4,
              background: busy || !user || !pass ? 'var(--surface)' : 'var(--accent)',
              border:'1px solid var(--border)', color: busy || !user || !pass ? 'var(--muted)' : '#fff',
              fontWeight:600, fontSize:13, cursor: busy || !user || !pass ? 'not-allowed' : 'pointer',
              fontFamily:'inherit', transition:'background 0.15s',
            }}>
            {busy ? 'Authenticating...' : 'Continue'}
          </button>
        </motion.div>
      </div>
    </div>
  )
}
