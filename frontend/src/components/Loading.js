import React from "react";

export default function Loading({ label = "Processing..." }) {
  return (
    <div className="loading">
      <div className="loading__spinner" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}
