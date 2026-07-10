import React from "react";

const OPTIONS = [
  { value: "short", label: "Short", hint: "Key highlights only" },
  { value: "medium", label: "Medium", hint: "Balanced overview" },
  { value: "long", label: "Long", hint: "Detailed summary" },
];

export default function SummaryOptions({ value, onChange, disabled }) {
  return (
    <div className="options-row" role="radiogroup" aria-label="Summary length">
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          type="button"
          className={`option-pill ${value === opt.value ? "option-pill--active" : ""}`}
          onClick={() => onChange(opt.value)}
          disabled={disabled}
          role="radio"
          aria-checked={value === opt.value}
        >
          <span className="option-pill__label">{opt.label}</span>
          <span className="option-pill__hint">{opt.hint}</span>
        </button>
      ))}
    </div>
  );
}
