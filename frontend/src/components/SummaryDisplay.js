import React, { useState } from "react";

function StatChip({ label, value }) {
  if (value === undefined || value === null || value === "") return null;
  return (
    <div className="stat-chip">
      <span className="stat-chip__value">{value}</span>
      <span className="stat-chip__label">{label}</span>
    </div>
  );
}

export default function SummaryDisplay({ result, onCopy }) {
  const [activeTab, setActiveTab] = useState("summary");
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const {
    filename,
    word_count,
    page_count,
    extraction_method,
    summary,
    key_points = [],
    suggestions = [],
    readability,
  } = result;

  const handleCopy = () => {
    navigator.clipboard.writeText(summary || "").then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
      if (onCopy) onCopy();
    });
  };

  return (
    <div className="results-card">
      <div className="results-header">
        <div>
          <h2 className="results-title">{filename || "Document"}</h2>
          <div className="stats-row">
            <StatChip label="words" value={word_count} />
            {page_count ? <StatChip label="pages" value={page_count} /> : null}
            {readability?.label ? <StatChip label="readability" value={readability.label} /> : null}
            {extraction_method ? (
              <StatChip
                label="extraction"
                value={
                  extraction_method === "tesseract_ocr"
                    ? "OCR"
                    : extraction_method === "ocr_fallback"
                    ? "OCR (scanned PDF)"
                    : "text layer"
                }
              />
            ) : null}
          </div>
        </div>
      </div>

      <div className="tabs" role="tablist">
        <button
          role="tab"
          aria-selected={activeTab === "summary"}
          className={`tab ${activeTab === "summary" ? "tab--active" : ""}`}
          onClick={() => setActiveTab("summary")}
        >
          Summary
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "keypoints"}
          className={`tab ${activeTab === "keypoints" ? "tab--active" : ""}`}
          onClick={() => setActiveTab("keypoints")}
        >
          Key Points ({key_points.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === "suggestions"}
          className={`tab ${activeTab === "suggestions" ? "tab--active" : ""}`}
          onClick={() => setActiveTab("suggestions")}
        >
          Suggestions ({suggestions.length})
        </button>
      </div>

      <div className="tab-panel">
        {activeTab === "summary" && (
          <div>
            <div className="panel-actions">
              <button className="btn-secondary" onClick={handleCopy}>
                {copied ? "Copied!" : "Copy Summary"}
              </button>
            </div>
            <p className="summary-text">{summary || "No summary available."}</p>
          </div>
        )}

        {activeTab === "keypoints" && (
          <ul className="key-points-list">
            {key_points.length === 0 && <li>No key points found.</li>}
            {key_points.map((point, idx) => (
              <li key={idx}>
                <span className="key-points-list__marker">{idx + 1}</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        )}

        {activeTab === "suggestions" && (
          <ul className="suggestions-list">
            {suggestions.length === 0 && <li>No suggestions.</li>}
            {suggestions.map((s, idx) => (
              <li key={idx} className="suggestions-list__item">
                <span className="suggestion-category">{s.category}</span>
                <span>{s.message}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
