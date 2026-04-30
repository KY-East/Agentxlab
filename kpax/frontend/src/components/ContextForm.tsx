import { useState } from "react";
import type { ContextField } from "../api/client";

interface Props {
  questionSummary: string;
  fields: ContextField[];
  onSubmit: (answers: Record<string, unknown>) => void;
  loading: boolean;
}

export default function ContextForm({ questionSummary, fields, onSubmit, loading }: Props) {
  const [answers, setAnswers] = useState<Record<string, unknown>>({});

  const setValue = (fieldId: string, value: unknown) => {
    setAnswers((prev) => ({ ...prev, [fieldId]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(answers);
  };

  const requiredFieldsFilled = fields
    .filter((f) => f.required)
    .every((f) => {
      const val = answers[f.field_id];
      if (val === undefined || val === null || val === "") return false;
      if (Array.isArray(val) && val.length === 0) return false;
      return true;
    });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs text-kpax-500 font-mono uppercase tracking-wider mb-1">
          Your question
        </p>
        <p className="text-white text-lg">{questionSummary}</p>
      </div>

      <div className="bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-5 space-y-1.5">
        <p className="text-sm text-zinc-300">
          To give you a precise analysis, I need some context about your situation.
        </p>
        <p className="text-xs text-zinc-600">
          Fields marked with * are required. The more you share, the better the analysis.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {fields.map((field) => (
          <FieldRenderer
            key={field.field_id}
            field={field}
            value={answers[field.field_id]}
            onChange={(v) => setValue(field.field_id, v)}
          />
        ))}

        <button
          type="submit"
          disabled={loading || !requiredFieldsFilled}
          className="w-full bg-kpax-600 hover:bg-kpax-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-white font-medium py-3 px-6 rounded-xl transition-all text-sm"
        >
          {loading ? "Assembling experts..." : "Continue"}
        </button>
      </form>
    </div>
  );
}

function FieldRenderer({
  field,
  value,
  onChange,
}: {
  field: ContextField;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  const labelCls = "block text-sm text-zinc-300 mb-1.5";
  const descCls = "text-xs text-zinc-600 mb-2";
  const inputCls =
    "w-full bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-kpax-600/50 focus:border-kpax-700";

  return (
    <div>
      <label className={labelCls}>
        {field.label}
        {field.required && <span className="text-kpax-500 ml-0.5">*</span>}
      </label>
      {field.description && <p className={descCls}>{field.description}</p>}

      {field.input_type === "text" && (
        <textarea
          value={(value as string) || ""}
          onChange={(e) => onChange(e.target.value)}
          rows={2}
          className={`${inputCls} resize-none`}
          placeholder="Type here..."
        />
      )}

      {field.input_type === "select" && field.options && (
        <div className="flex flex-wrap gap-2">
          {field.options.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange(opt.value)}
              className={`px-4 py-2 rounded-lg text-sm border transition-all ${
                value === opt.value
                  ? "bg-kpax-600/20 border-kpax-600/50 text-kpax-300"
                  : "bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-zinc-600"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}

      {field.input_type === "multi_select" && field.options && (
        <div className="flex flex-wrap gap-2">
          {field.options.map((opt) => {
            const arr = (value as string[]) || [];
            const selected = arr.includes(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  const next = selected
                    ? arr.filter((v) => v !== opt.value)
                    : [...arr, opt.value];
                  onChange(next);
                }}
                className={`px-4 py-2 rounded-lg text-sm border transition-all ${
                  selected
                    ? "bg-kpax-600/20 border-kpax-600/50 text-kpax-300"
                    : "bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-zinc-600"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      )}

      {field.input_type === "tags" && field.options && (
        <div className="flex flex-wrap gap-2">
          {field.options.map((opt) => {
            const arr = (value as string[]) || [];
            const selected = arr.includes(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  const next = selected
                    ? arr.filter((v) => v !== opt.value)
                    : [...arr, opt.value];
                  onChange(next);
                }}
                className={`px-3 py-1.5 rounded-full text-xs border transition-all ${
                  selected
                    ? "bg-kpax-600/20 border-kpax-600/50 text-kpax-300"
                    : "bg-zinc-900/50 border-zinc-800 text-zinc-500 hover:border-zinc-600"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      )}

      {field.input_type === "slider" && field.slider_config && (
        <div className="space-y-2">
          <input
            type="range"
            min={field.slider_config.min}
            max={field.slider_config.max}
            step={field.slider_config.step}
            value={(value as number) ?? field.slider_config.min}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-full accent-kpax-600"
          />
          <div className="flex justify-between text-xs text-zinc-500">
            <span>
              {field.slider_config.min} {field.slider_config.unit}
            </span>
            <span className="text-kpax-400 font-medium">
              {(value as number) ?? field.slider_config.min} {field.slider_config.unit}
            </span>
            <span>
              {field.slider_config.max} {field.slider_config.unit}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
