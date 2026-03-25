import type { QuickPrompt } from "../data/quickPrompts";

interface Props {
  prompts: QuickPrompt[];
  onSelect: (text: string) => void;
  disabled?: boolean;
}

export default function QuickPrompts({ prompts, onSelect, disabled }: Props) {
  return (
    <div className="quick-prompts">
      <span className="quick-prompts-label">Quick Prompts</span>
      <div className="quick-prompts-list">
        {prompts.map((p) => (
          <button
            key={p.label}
            type="button"
            className="quick-prompt-btn"
            disabled={disabled}
            onClick={() => onSelect(p.text)}
          >
            ⚡ {p.label}
          </button>
        ))}
      </div>
    </div>
  );
}
