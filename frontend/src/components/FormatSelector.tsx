import type { FormatOption } from "../data/formats";

interface Props {
  options: FormatOption[];
  selected: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function FormatSelector({ options, selected, onChange, disabled }: Props) {
  return (
    <div className="format-selector">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          className={`format-btn${selected === opt.value ? " format-btn--active" : ""}`}
          data-tooltip={opt.tooltip}
          disabled={disabled}
          onClick={() => onChange(selected === opt.value ? "" : opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
