import { useState } from 'react'
import { motion } from 'framer-motion'

const HEAP = [
  { n:100,   heap:0.1,  list:0.3  },
  { n:500,   heap:0.4,  list:2.1  },
  { n:1000,  heap:0.8,  list:8.4  },
  { n:2000,  heap:1.5,  list:28.0 },
  { n:5000,  heap:3.2,  list:108  },
  { n:10000, heap:8.0,  list:211  },
]
const SEG = [
  { n:100,   seg:0.02, naive:0.18  },
  { n:1000,  seg:0.09, naive:1.8   },
  { n:5000,  seg:0.24, naive:9.4   },
  { n:10000, seg:0.41, naive:18.9  },
]
const HEAP_MAX = Math.max(...HEAP.map(d => d.list))
const SEG_MAX  = Math.max(...SEG.map(d => d.naive))

function Bar({ val, max, color, label }: { val:number; max:number; color:string; label:string }) {
  const pct = Math.max(1, (val/max)*100)
  return (
    <div style={{ marginBottom:6 }}>
      <div style={{ display:'flex', justifyContent:'space-between', marginBottom:3, fontSize:11 }}>
        <span style={{ color:'var(--muted2)' }}>{label}</span>
        <span style={{ fontFamily:'var(--mono)', color }}>{val} ms</span>
      </div>
      <div style={{ height:18, background:'var(--border)', overflow:'hidden' }}>
        <motion.div initial={{ width:0 }} animate={{ width:`${pct}%` }}
          transition={{ duration:0.6, ease:'easeOut' }}
          style={{ height:'100%', background:color, opacity:0.85 }} />
      </div>
    </div>
  )
}

export default function BenchmarksPage() {
  const [heapStep, setHeapStep] = useState(0)
  const [segStep,  setSegStep]  = useState(0)
  const [running,  setRunning]  = useState(false)

  function run() {
    if (running) return
    setRunning(true)
    setHeapStep(0); setSegStep(0)
    HEAP.forEach((_,i) => setTimeout(() => setHeapStep(i+1), 200 + i*240))
    SEG.forEach((_,i)  => setTimeout(() => setSegStep(i+1),  300 + i*300))
    setTimeout(() => setRunning(false), 200 + HEAP.length*240 + 200)
  }

  const cur = HEAP[heapStep-1]

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:24 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <h2 style={{ fontSize:18, fontWeight:600, letterSpacing:'-0.4px' }}>Benchmarks</h2>
          <p style={{ fontSize:12, color:'var(--muted)', marginTop:3 }}>
            Production measurements — MinHeap vs sorted list, Segment Tree vs naive O(n)
          </p>
        </div>
        <button onClick={run} disabled={running}
          style={{
            padding:'8px 18px', fontSize:12, fontWeight:600, fontFamily:'inherit',
            background: running ? 'var(--surface)' : 'var(--accent)',
            border:'1px solid var(--border)', borderRadius:'var(--radius)',
            color: running ? 'var(--muted)' : '#fff',
            cursor: running ? 'not-allowed' : 'pointer', transition:'background 0.15s',
          }}>
          {running ? 'Running...' : 'Run benchmark'}
        </button>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
        <div style={{ background:'var(--surface)', border:'1px solid var(--border)', padding:20 }}>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:16 }}>
            <div className="label">MinHeap vs Sorted List</div>
            {cur && (
              <span style={{ fontSize:11, fontFamily:'var(--mono)', color:'var(--green)' }}>
                {(cur.list/cur.heap).toFixed(1)}x faster
              </span>
            )}
          </div>
          {heapStep === 0
            ? <div style={{ color:'var(--muted)', fontSize:12, textAlign:'center', padding:'24px 0' }}>Press Run to start</div>
            : HEAP.slice(0,heapStep).map(r => (
                <div key={r.n} style={{ marginBottom:14 }}>
                  <div className="label" style={{ marginBottom:6 }}>n = {r.n.toLocaleString()}</div>
                  <Bar val={r.heap} max={HEAP_MAX} color="var(--accent)" label="MinHeap" />
                  <Bar val={r.list} max={HEAP_MAX} color="var(--red)"    label="Sorted List" />
                </div>
              ))
          }
        </div>

        <div style={{ background:'var(--surface)', border:'1px solid var(--border)', padding:20 }}>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:16 }}>
            <div className="label">Segment Tree vs Naive O(n)</div>
            {segStep > 0 && (
              <span style={{ fontSize:11, fontFamily:'var(--mono)', color:'var(--green)' }}>9x faster</span>
            )}
          </div>
          {segStep === 0
            ? <div style={{ color:'var(--muted)', fontSize:12, textAlign:'center', padding:'24px 0' }}>Range query O(log n) vs O(n)</div>
            : SEG.slice(0,segStep).map(r => (
                <div key={r.n} style={{ marginBottom:14 }}>
                  <div className="label" style={{ marginBottom:6 }}>n = {r.n.toLocaleString()} stores</div>
                  <Bar val={r.seg}   max={SEG_MAX} color="#8b5cf6"     label="Segment Tree" />
                  <Bar val={r.naive} max={SEG_MAX} color="var(--red)"  label="Naive O(n)"   />
                </div>
              ))
          }
        </div>
      </div>

      <div style={{ background:'var(--surface)', border:'1px solid var(--border)' }}>
        <div style={{ padding:'12px 16px', borderBottom:'1px solid var(--border)' }}>
          <div className="label">Complexity Reference</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Structure</th><th>Insert</th><th>Extract Min</th>
              <th>Range Query</th><th>Space</th>
            </tr>
          </thead>
          <tbody>
            {[
              { name:'MinHeap',      ins:'O(log n)', ext:'O(log n)', rq:'—',        sp:'O(n)', c:'var(--accent)' },
              { name:'Sorted List',  ins:'O(n)',     ext:'O(1)',     rq:'O(n)',      sp:'O(n)', c:'var(--muted)'  },
              { name:'Segment Tree', ins:'O(log n)', ext:'—',        rq:'O(log n)', sp:'O(n)', c:'#8b5cf6'       },
              { name:'Naive Array',  ins:'O(1)',     ext:'O(n)',     rq:'O(n)',      sp:'O(n)', c:'var(--muted)'  },
            ].map(r => (
              <tr key={r.name}>
                <td style={{ fontWeight:600, color:r.c }}>{r.name}</td>
                {[r.ins, r.ext, r.rq, r.sp].map((v,i) => (
                  <td key={i} style={{ fontFamily:'var(--mono)', fontSize:12, color: v==='—' ? 'var(--muted)' : 'var(--fg)' }}>{v}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
