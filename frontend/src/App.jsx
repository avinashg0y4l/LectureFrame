import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null); // 'queued', 'downloading', 'extracting', 'generating', 'completed', 'error'
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  useEffect(() => {
    let intervalId;
    if (taskId && status !== 'completed' && status !== 'error') {
      intervalId = setInterval(checkStatus, 2000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId, status]);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/status/${taskId}`);
      if (!res.ok) throw new Error('Failed to fetch status');
      const data = await res.json();
      setStatus(data.status);
      setMessage(data.message);
      if (data.status === 'error') {
        setErrorMsg(data.message);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setTaskId(null);
    setStatus('queued');
    setErrorMsg('');
    setMessage('Initializing...');

    try {
      const res = await fetch(`${API_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to process request');

      setTaskId(data.task_id);
    } catch (err) {
      setStatus('error');
      setErrorMsg(err.message);
    }
  };

  const isProcessing = status && status !== 'completed' && status !== 'error';

  return (
    <div className="app-container">
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>

      <div className="hero float-anim">
        <h1>
          Lecture<span className="title-gradient">Frame</span>
        </h1>
        <p>Automagically convert YouTube videos and playlists into high-quality PDF slides. Perfect for capturing lecture notes instantly.</p>
      </div>

      <div className="converter-panel glass-panel">
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="url">YouTube URL</label>
            <input
              type="url"
              id="url"
              className="input-main"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isProcessing}
              required
            />
          </div>

          <div className="action-row">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isProcessing || !url}
            >
              {isProcessing ? (
                <>
                  <div className="spinner"></div> Processing...
                </>
              ) : 'Generate PDF'}
            </button>
          </div>
        </form>

        {status && (
          <div className="status-container">
            {isProcessing && (
              <>
                <div className="progress-track">
                  <div className="progress-bar"></div>
                </div>
                <div style={{ color: 'var(--accent-light)', fontWeight: 500 }}>
                  {message}
                </div>
              </>
            )}

            {status === 'completed' && taskId && (
              <div className="result-card">
                <h3>Slides Ready!</h3>
                <p>We've successfully extracted the slides for your video.</p>
                <a
                  href={`${API_URL}/download/${taskId}`}
                  className="download-link"
                  target="_blank"
                  rel="noreferrer"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download PDF
                </a>
              </div>
            )}

            {status === 'error' && (
              <div className="error-msg">
                <strong>Error:</strong> {errorMsg}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
