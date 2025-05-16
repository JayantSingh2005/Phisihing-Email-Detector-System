import React, { useRef, useState } from 'react';
import './App.css';
import { FiUploadCloud, FiSearch, FiArrowLeft } from 'react-icons/fi';

function App() {
  const fileInputRef = useRef();
  const [result, setResult] = useState(null);
  const [textMode, setTextMode] = useState(false);
  const [emailText, setEmailText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileSelect = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    // Placeholder: handle file upload logic here
    alert('File(s) selected!');
  };

  const handlePasteText = () => {
    setTextMode(true);
    setResult(null);
    setEmailText('');
  };

  const handleCancelText = () => {
    setTextMode(false);
    setEmailText('');
    setResult(null);
  };

  const handleScanText = async () => {
    if (!emailText.trim()) return;
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body: emailText }),
      });
      const data = await response.json();
      setResult({
        prediction: data.prediction,
        confidence: data.confidence
      });
    } catch (error) {
      setResult({
        prediction: 'Error',
        confidence: 0,
        error: error.message
      });
    }
    setLoading(false);
  };

  const handleQuickScan = () => {
    // Placeholder: handle quick scan logic here
    alert('Quick Scan clicked!');
  };

  return (
    <div className="threat-scanner-bg">
      <div className="threat-card">
        <div className="threat-title-row">
          <span className="threat-title-icon"><FiSearch size={22} /></span>
          <span className="threat-title">Threat Scanner</span>
        </div>
        {!textMode ? (
          <div className="drop-area">
            <div className="upload-icon"><FiUploadCloud size={48} /></div>
            <div className="drop-message">Drop files or emails to scan</div>
            <div className="drop-sub">Upload files to analyze for security threats</div>
            <button className="select-files-btn" onClick={handleFileSelect}>
              <span className="select-files-icon"><FiUploadCloud size={18} /></span> Select Files
            </button>
            <input
              type="file"
              multiple
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
          </div>
        ) : (
          <div className="text-area-block">
            <textarea
              className="email-textarea"
              placeholder="Paste or type email text here..."
              value={emailText}
              onChange={e => setEmailText(e.target.value)}
              rows={7}
              autoFocus
            />
            <div className="text-area-actions">
              <button className="cancel-text-btn" onClick={handleCancelText}>
                <FiArrowLeft style={{marginRight: 6}}/> Cancel
              </button>
              <button className="scan-text-btn" onClick={handleScanText} disabled={loading || !emailText.trim()}>
                {loading ? 'Scanning...' : 'Scan Text'}
              </button>
            </div>
          </div>
        )}
        <div className="threat-actions-row">
          <button className="paste-text-btn" onClick={handlePasteText} disabled={textMode}>Paste Text</button>
          <button className="quick-scan-btn" onClick={handleQuickScan} disabled={textMode}><FiSearch size={18} style={{marginRight: 8}}/> Quick Scan</button>
        </div>
        {result && (
          <div className={`scan-result-card ${result.prediction === 'Error' ? 'error' : result.prediction}`}
               style={{marginTop: 20}}>
            {result.prediction === 'Error' ? (
              <>
                <div className="scan-result-title">Error</div>
                <div className="scan-result-message">{result.error}</div>
              </>
            ) : (
              <>
                <div className="scan-result-title">Prediction: {result.prediction}</div>
                <div className="scan-result-message">Confidence: {(result.confidence * 100).toFixed(2)}%</div>
              </>
            )}
          </div>
        )}
        <div className="threat-desc">
          Scan emails, documents, and executable files for phishing attempts, malware, and other security threats.
        </div>
      </div>
    </div>
  );
}

export default App;
