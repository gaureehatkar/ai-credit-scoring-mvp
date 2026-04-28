import { useNavigate } from 'react-router-dom';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ background: 'var(--bg)', minHeight: '100vh' }}>
      {/* Nav */}
      <nav className="landing-nav">
        <div className="navbar-brand">
          <div className="logo-icon">S</div>
          <span>Saral Credit</span>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/login')}>Sign in</button>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/register')}>Get started →</button>
        </div>
      </nav>

      {/* Hero */}
      <div className="hero">
        <div>
          <div className="hero-tag">✦ Built for Bharat · AI + SHAP Explainability</div>
          <h1>Credit that sees the <span className="highlight">whole</span> you.</h1>
          <p>UPI history. Gig ratings. Community trust. Microfinance loyalty. We turn the data of your real life into a credit score that opens real doors — in seconds, with full transparency.</p>
          <div className="hero-actions">
            <button className="btn btn-primary" onClick={() => navigate('/register')}>Apply for credit →</button>
            <button className="btn btn-ghost" onClick={() => navigate('/admin/login')}>Lender / Admin login</button>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <div className="stat-num">82k+</div>
              <div className="stat-desc">people scored</div>
            </div>
            <div className="hero-stat">
              <div className="stat-num">₹240Cr</div>
              <div className="stat-desc">unlocked</div>
            </div>
            <div className="hero-stat">
              <div className="stat-num">94%</div>
              <div className="stat-desc">repayment</div>
            </div>
            <div className="hero-stat">
              <div className="stat-num">4.2s</div>
              <div className="stat-desc">avg decision</div>
            </div>
          </div>
        </div>

        {/* Score preview card */}
        <div className="score-preview-card">
          <div className="score-preview-header">Live Score Preview</div>
          <div className="score-preview-number">742</div>
          <div className="score-preview-sub">out of 850</div>
          <div className="score-preview-approved">
            <span>Approved EMI</span>
            <span>₹4,238/mo</span>
          </div>
          {[
            { label: 'UPI Activity', impact: 'Helps', positive: true, width: 85 },
            { label: 'Gig Platform Rating', impact: 'Helps', positive: true, width: 70 },
            { label: 'Late Payments', impact: 'Hurts', positive: false, width: 30 },
            { label: 'Community Trust', impact: 'Helps', positive: true, width: 60 },
          ].map((item) => (
            <div key={item.label} className="shap-bar-wrap" style={{ marginBottom: '10px' }}>
              <div className="shap-bar-label">
                <span style={{ fontSize: '12px' }}>{item.label}</span>
                <span style={{ fontSize: '11px', color: item.positive ? 'var(--success)' : 'var(--red)', fontWeight: 600 }}>
                  {item.positive ? '▲' : '▼'} {item.impact}
                </span>
              </div>
              <div className="shap-bar-track">
                <div
                  className={`shap-bar-fill ${item.positive ? 'shap-positive' : 'shap-negative'}`}
                  style={{ width: `${item.width}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="features-section">
        <div className="section-tag">Why Saral</div>
        <div className="section-title">Built differently. Built for everyone.</div>
        <div className="features-grid">
          {[
            { icon: '🛡️', title: 'Explainable AI', desc: "Every score comes with SHAP-powered reasons. Know exactly which signals helped — and which hurt.", num: '01' },
            { icon: '❤️', title: 'Inclusive by design', desc: "If you've never had a loan, that doesn't mean you can't pay one back. We score your real life.", num: '02' },
            { icon: '📈', title: 'Improve over time', desc: "Track your score, follow tailored credit health tips, and re-apply with confidence.", num: '03' },
          ].map((f) => (
            <div key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
              <div className="feature-num">{f.num}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="cta-section">
        <div>
          <h2>Get your score in under 5 minutes.</h2>
          <p>Free, no impact on existing credit, full explanation included.</p>
        </div>
        <div className="cta-actions">
          <button className="btn btn-accent" onClick={() => navigate('/register')}>Create your account →</button>
          <button className="btn btn-outline" style={{ color: 'white', borderColor: 'rgba(255,255,255,0.4)' }} onClick={() => navigate('/login')}>I have an account</button>
        </div>
      </div>

      {/* Footer */}
      <div className="landing-footer">
        <div className="navbar-brand">
          <div className="logo-icon" style={{ width: 24, height: 24, fontSize: 12 }}>S</div>
          <span style={{ fontSize: 14 }}>Saral Credit</span>
        </div>
        <span>© 2026 Saral Credit. Fair finance for Bharat.</span>
      </div>
    </div>
  );
}

export default LandingPage;
