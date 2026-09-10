import React, { useState, useEffect } from 'react'

export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHealth()
  }, [])

  const fetchHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/health')
      if (!res.ok) {
        throw new Error(`Health check returned status ${res.status}`)
      }
      const data = await res.json()
      setHealthData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const navItems = [
    { id: 'overview', label: 'System Overview', icon: '⚡' },
    { id: 'chat', label: 'Agent Chat', icon: '💬', badge: 'Phase 4' },
    { id: 'tasks', label: 'Execution Tasks', icon: '📋', badge: 'Phase 4' },
    { id: 'knowledge', label: 'Knowledge Base', icon: '📚', badge: 'Phase 7' },
    { id: 'models', label: 'Model Registry', icon: '🧠', badge: 'Phase 2' },
    { id: 'artifacts', label: 'Artifacts', icon: '📁', badge: 'Phase 9' },
    { id: 'security', label: 'Security & Sovereignty', icon: '🛡️', badge: 'Phase 12' },
  ]

  const executionSteps = [
    'Understand',
    'Plan',
    'Route',
    'Act',
    'Observe',
    'Verify',
    'Iterate',
    'Deliver',
  ]

  return (
    <div className="workbench-container">
      {/* Top Header */}
      <header className="top-header">
        <div className="brand-section">
          <div className="brand-icon">S</div>
          <span className="brand-title">SovAI</span>
          <span className="brand-tagline">Confidential Industrial Workbench</span>
        </div>

        <div className="header-status-area">
          <div className="badge badge-airgap">
            <div className="badge-pulse"></div>
            <span>SOVEREIGN AIR-GAP ACTIVE</span>
          </div>
          <div className="badge badge-version">
            v{healthData?.version || '0.1.0'} (Phase 0)
          </div>
        </div>
      </header>

      {/* Main Body */}
      <div className="workbench-body">
        {/* Navigation Sidebar */}
        <aside className="sidebar">
          <ul className="sidebar-nav">
            {navItems.map((item) => (
              <li
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.badge && (
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    {item.badge}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </aside>

        {/* Viewport */}
        <main className="main-viewport">
          {/* Header Title */}
          <div className="view-header">
            <div>
              <h1 className="view-title">Operational Workbench</h1>
              <p className="view-subtitle">
                On-premise confidential agentic execution engine • NVIDIA RTX 4050 6GB target
              </p>
            </div>
            <button
              onClick={fetchHealth}
              style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '8px 16px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 600,
              }}
            >
              🔄 Refresh Status
            </button>
          </div>

          {/* Philosophy Strip */}
          <div className="philosophy-strip">
            {executionSteps.map((step, idx) => (
              <React.Fragment key={step}>
                <div className={`philosophy-step ${idx === 0 ? 'active' : ''}`}>
                  <span>{step}</span>
                </div>
                {idx < executionSteps.length - 1 && (
                  <span className="philosophy-arrow">→</span>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Target Models Grid */}
          <div>
            <h2 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>
              Target Models (Local RTX 4050 6GB Environment)
            </h2>
            <div className="models-banner">
              <div className="model-pill">
                <div className="model-role">Coding Specialist</div>
                <div className="model-name">Qwen2.5-Coder-3B</div>
                <div className="model-meta">Code synthesis, sandbox execution, repair</div>
              </div>
              <div className="model-pill">
                <div className="model-role">Reasoning / General</div>
                <div className="model-name">Qwen3-4B</div>
                <div className="model-meta">Planning, industrial logic, SOP synthesis</div>
              </div>
              <div className="model-pill">
                <div className="model-role">Vision / Multimodal</div>
                <div className="model-name">Gemma 3 4B</div>
                <div className="model-meta">Inspection reports, P&ID visual analysis</div>
              </div>
            </div>
          </div>

          {/* Main Status Grid */}
          <div className="dashboard-grid">
            {/* Live Backend Telemetry */}
            <div className="card">
              <div className="card-title">
                <span>Backend Telemetry</span>
                <span className={`status-tag ${healthData?.status === 'healthy' ? 'ready' : 'pending'}`}>
                  {loading ? 'CHECKING...' : healthData?.status || 'OFFLINE'}
                </span>
              </div>
              {error ? (
                <div style={{ color: 'var(--accent-rose)', fontSize: '0.85rem' }}>
                  Connection issue: {error}. Ensure FastAPI backend is running on port 8000.
                </div>
              ) : healthData ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                  <div><strong>Environment:</strong> {healthData.environment}</div>
                  <div><strong>Version:</strong> {healthData.version}</div>
                  <div><strong>Air-Gap Strict Mode:</strong> {healthData.airgap_mode ? 'ENFORCED' : 'OFF'}</div>
                  <div><strong>Report Timestamp:</strong> {healthData.timestamp}</div>
                </div>
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Polling backend status...</div>
              )}
            </div>

            {/* Subsystem Readiness Ledger */}
            <div className="card" style={{ gridColumn: 'span 2' }}>
              <div className="card-title">
                <span>Subsystem Readiness Ledger (Factual State)</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Phase-by-Phase Rollout
                </span>
              </div>
              <div className="readiness-list">
                {healthData?.subsystems ? (
                  Object.entries(healthData.subsystems).map(([key, item]) => (
                    <div key={key} className="readiness-item">
                      <div>
                        <div className="readiness-name">
                          <span>{key.replace(/_/g, ' ').toUpperCase()}</span>
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            (Phase {item.phase})
                          </span>
                        </div>
                        <div className="readiness-desc">{item.description}</div>
                      </div>
                      <span className={`status-tag ${item.status.toLowerCase()}`}>
                        {item.status}
                      </span>
                    </div>
                  ))
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Subsystem data unavailable.
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
