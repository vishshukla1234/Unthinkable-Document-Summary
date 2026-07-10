import React, { useCallback, useRef, useState } from "react";

const ACCEPTED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"];
const MAX_SIZE_MB = 20;

function isAcceptedFile(file) {
  const lowerName = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
}

export default function FileUpload({ onFileSelected, disabled }) {
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState("");
  const inputRef = useRef(null);

  const validateAndSelect = useCallback(
    (file) => {
      if (!file) return;
      if (!isAcceptedFile(file)) {
        setLocalError("Unsupported file type. Please upload a PDF or image (PNG/JPG/TIFF/BMP/WEBP).");
        return;
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setLocalError(`File is too large. Max size is ${MAX_SIZE_MB}MB.`);
        return;
      }
      setLocalError("");
      onFileSelected(file);
    },
    [onFileSelected]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      if (disabled) return;
      const file = e.dataTransfer.files && e.dataTransfer.files[0];
      validateAndSelect(file);
    },
    [disabled, validateAndSelect]
  );

  const handleDragOver = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!disabled) setIsDragging(true);
    },
    [disabled]
  );

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleInputChange = (e) => {
    const file = e.target.files && e.target.files[0];
    validateAndSelect(file);
    e.target.value = "";
  };

  return (
    <div className="upload-wrapper">
      <div
        className={`dropzone ${isDragging ? "dropzone--active" : ""} ${disabled ? "dropzone--disabled" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !disabled && inputRef.current.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if ((e.key === "Enter" || e.key === " ") && !disabled) inputRef.current.click();
        }}
      >
        <div className="dropzone__icon" aria-hidden="true">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 16V4M12 4L7 9M12 4l5 5M5 20h14"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <p className="dropzone__title">Drag & drop a document here</p>
        <p className="dropzone__subtitle">or click to browse (PDF, PNG, JPG, TIFF, BMP, WEBP -- max {MAX_SIZE_MB}MB)</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          onChange={handleInputChange}
          hidden
          disabled={disabled}
        />
      </div>
      {localError && <p className="upload-error">{localError}</p>}
    </div>
  );
}
