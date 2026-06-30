import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('VISTA Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          minHeight: '300px', padding: 'var(--s8)', textAlign: 'center',
        }}>
          <div style={{ fontSize: '32px', marginBottom: 'var(--s4)' }}>⚠️</div>
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: 'var(--s2)', color: 'var(--text)' }}>
            Something went wrong
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: 'var(--s4)', maxWidth: '400px' }}>
            An unexpected error occurred. Try refreshing the page.
          </p>
          <div style={{ display: 'flex', gap: 'var(--s3)' }}>
            <button className="v-btn v-btn-primary" onClick={() => window.location.reload()}>
              Refresh Page
            </button>
            <button className="v-btn v-btn-secondary" onClick={() => this.setState({ hasError: false, error: null })}>
              Try Again
            </button>
          </div>
          {this.state.error && (
            <details style={{ marginTop: 'var(--s4)', fontSize: '11px', color: 'var(--text-muted)', maxWidth: '500px', textAlign: 'left' }}>
              <summary style={{ cursor: 'pointer' }}>Error details</summary>
              <pre style={{ marginTop: 'var(--s2)', whiteSpace: 'pre-wrap', fontFamily: 'var(--mono)', background: 'var(--bg-secondary)', padding: 'var(--s3)', borderRadius: 'var(--r-sm)' }}>
                {this.state.error.message}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
