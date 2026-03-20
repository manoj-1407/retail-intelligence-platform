import React, { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from './hooks/useAuth'
import ErrorBoundary from './components/ErrorBoundary'
import LoginPage    from './components/LoginPage'
import Sidebar      from './components/Sidebar'
import Dashboard    from './components/Dashboard'
import ProductsPage   from './components/ProductsPage'
import ShipmentsPage  from './components/ShipmentsPage'
import InventoryPage  from './components/InventoryPage'
import AlertsPage     from './components/AlertsPage'
import BenchmarksPage from './components/BenchmarksPage'
import LiveFeed       from './components/LiveFeed'

const qc = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30_000 } } })

function Inner() {
  const { authed, loading, error, doLogin, doLogout } = useAuth()
  const [page, setPage] = useState('dashboard')

  if (loading) return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100vh' }}>
      <span style={{ color:'var(--muted)', fontSize:13 }}>Loading</span>
    </div>
  )

  if (!authed) return (
    <ErrorBoundary>
      <LoginPage onLogin={doLogin} error={error} />
    </ErrorBoundary>
  )

  const PAGES: Record<string, React.ReactElement> = {
    dashboard:  <Dashboard />,
    products:   <ProductsPage />,
    shipments:  <ShipmentsPage />,
    inventory:  <InventoryPage />,
    alerts:     <AlertsPage />,
    benchmarks: <BenchmarksPage />,
    livefeed:   <LiveFeed events={[]} connected={false} standalone />,
  }

  return (
    <div style={{ display:'flex', minHeight:'100vh' }}>
      <Sidebar active={page} setActive={setPage} onLogout={doLogout} />
      <main style={{ marginLeft:200, flex:1, padding:'28px 32px', minHeight:'100vh' }}>
        <ErrorBoundary>
          <AnimatePresence mode="wait">
            <motion.div key={page}
              initial={{ opacity:0, y:10 }}
              animate={{ opacity:1, y:0 }}
              exit={{ opacity:0 }}
              transition={{ duration:0.18, ease:'easeOut' }}>
              {PAGES[page] ?? <Dashboard />}
            </motion.div>
          </AnimatePresence>
        </ErrorBoundary>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <Inner />
    </QueryClientProvider>
  )
}
