import React, { useState, useRef } from 'react';
import { Upload, FileText, Loader2, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [length, setLength] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const extension = selectedFile.name.split('.').pop().toLowerCase();
    if (['pdf', 'png', 'jpg', 'jpeg'].includes(extension)) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Unsupported format. Please upload a PDF or an Image file (PNG/JPG).');
      setFile(null);
    }
  };

  const triggerFileSelect = () => fileInputRef.current.click();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('length', length);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/summarize', {
        method: 'POST',
        body: formData,
      });

      const jsonResponse = await response.json();

      if (!response.ok) {
        throw new Error(jsonResponse.detail || 'An unexpected failure occurred while generating your summary.');
      }

      setResult(jsonResponse.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Document Summary Assistant</h1>
        <p>Upload complex PDFs or clear scanned documents to generate smart summaries instantly.</p>
      </header>

      <div className="workspace">
        {/* Left Side: Inputs Control Panel */}
        <div className="card">
          <form onSubmit={handleSubmit}>
            <div 
              className={`dropzone ${isDragActive ? 'active' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileSelect}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept=".pdf,.png,.jpg,.jpeg" 
                style={{ display: 'none' }}
              />
              <Upload size={36} color={isDragActive ? '#3b82f6' : '#64748b'} style={{ margin: '0 auto' }} />
              <p>Drag and drop your file here, or <strong>browse</strong></p>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Supports PDF, PNG, JPG (Max 10MB)</span>
            </div>

            {file && (
              <div className="file-indicator">
                <FileText size={18} className="text-accent" />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {file.name}
                </span>
              </div>
            )}

            <div className="controls">
              <label htmlFor="length-select">Target Summary Length</label>
              <select 
                id="length-select" 
                className="select-input"
                value={length}
                onChange={(e) => setLength(e.target.value)}
              >
                <option value="short">Short (1-2 Paragraphs)</option>
                <option value="medium">Medium (3-4 Paragraphs)</option>
                <option value="long">Long (Deep Analysis)</option>
              </select>

              {error && (
                <div className="error-message">
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <AlertCircle size={16} />
                    <strong>Error</strong>
                  </div>
                  <p style={{ margin: '0.25rem 0 0 0' }}>{error}</p>
                </div>
              )}

              <button className="btn" type="submit" disabled={!file || loading}>
                {loading ? (
                  <>
                    <Loader2 size={18} className="spinner" />
                    Running OCR & Processing AI...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Generate Document Summary
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Right Side: Smart Output Panels */}
        <div className="card">
          {!result && !loading && (
            <div className="output-placeholder">
              <FileText size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
              <h3>No Analysis Generated Yet</h3>
              <p>Provide a document configuration on the left workspace panel to run analysis.</p>
            </div>
          )}

          {loading && (
            <div className="output-placeholder">
              <Loader2 size={48} className="spinner" style={{ color: '#3b82f6', marginBottom: '1rem' }} />
              <h3>Processing Pipeline Active</h3>
              <p>Reading layers, adjusting character vectors, and structuring content parameters...</p>
            </div>
          )}

          {result && (
            <div className="results-layout">
              <section>
                <h2>Smart Summary</h2>
                <p className="summary-text">{result.summary}</p>
              </section>

              <section>
                <h2>Key Takeaways</h2>
                <ul className="bullet-list">
                  {result.key_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </section>

              <section>
                <h2>Document Improvement Suggestions</h2>
                <ul className="bullet-list" style={{ color: '#cbd5e1' }}>
                  {result.improvements.map((improvement, index) => (
                    <li key={index} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <CheckCircle size={16} style={{ color: '#22c55e', marginTop: '0.2rem', flexShrink: 0 }} />
                      <span>{improvement}</span>
                    </li>
                  ))}
                </ul>
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;