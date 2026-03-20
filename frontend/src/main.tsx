import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:      #050a0f;
    --surface: #0a1020;
    --card:    #0d1525;
    --border:  #15243a;
    --border2: #1c3050;
    --accent:  #2563eb;
    --fg:      #e2ecff;
    --muted:   #4a6080;
    --muted2:  #7a94b0;
    --green:   #10b981;
    --amber:   #f59e0b;
    --red:     #ef4444;
    --radius:  4px;
    --mono:    'JetBrains Mono', 'Fira Code', monospace;
  }

  html { scroll-behavior: smooth; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--fg);
    font-size: 14px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

  .mono { font-family: var(--mono); }
  .num  { font-family: var(--mono); text-align: right; }

  .label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 500;
  }

  table { border-collapse: collapse; width: 100%; }

  th {
    padding: 8px 12px;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    text-align: left;
    border-bottom: 1px solid var(--border);
    font-weight: 500;
    white-space: nowrap;
  }

  th.r, td.r { text-align: right; }

  td {
    padding: 9px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
    color: var(--fg);
  }

  tr:hover td { background: rgba(255,255,255,0.012); }

  @keyframes shimmer {
    0%   { background-position: -600px 0; }
    100% { background-position:  600px 0; }
  }

  .sk {
    background: linear-gradient(90deg, var(--surface) 25%, #0f1e35 50%, var(--surface) 75%);
    background-size: 1200px 100%;
    animation: shimmer 1.5s infinite linear;
    border-radius: 3px;
  }
`;

const el = document.createElement('style');
el.textContent = css;
document.head.appendChild(el);
document.title = 'Retail Intelligence';

createRoot(document.getElementById('root')!).render(
  <StrictMode><App /></StrictMode>
)
