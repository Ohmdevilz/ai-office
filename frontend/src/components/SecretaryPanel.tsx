import { useState } from "react";
import { runTask } from "../api";
import type { AgentType } from "../api";

interface Props {
  agent: AgentType;
  title: string;
  icon: string;
  placeholder: string;
  accentColor: string;
}

type Status = "idle" | "loading" | "success" | "error";

export default function SecretaryPanel({
  agent,
  title,
  icon,
  placeholder,
  accentColor,
}: Props) {
  const [task, setTask] = useState("");
  const [expectedOutput, setExpectedOutput] = useState("");
  const [result, setResult] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!task.trim()) return;

    setStatus("loading");
    setError("");
    setResult("");

    try {
      const res = await runTask(agent, {
        task: task.trim(),
        ...(expectedOutput.trim() && { expected_output: expectedOutput.trim() }),
      });
      setResult(res.result);
      setStatus("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด");
      setStatus("error");
    }
  }

  function handleClear() {
    setTask("");
    setExpectedOutput("");
    setResult("");
    setError("");
    setStatus("idle");
  }

  return (
    <div className="panel" style={{ "--accent": accentColor } as React.CSSProperties}>
      <div className="panel-header">
        <span className="panel-icon">{icon}</span>
        <h2>{title}</h2>
      </div>

      <form onSubmit={handleSubmit} className="panel-form">
        <label>
          คำสั่ง / โจทย์
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder={placeholder}
            rows={4}
            disabled={status === "loading"}
          />
        </label>

        <label>
          รูปแบบผลลัพธ์ที่ต้องการ <span className="optional">(optional)</span>
          <input
            type="text"
            value={expectedOutput}
            onChange={(e) => setExpectedOutput(e.target.value)}
            placeholder="เช่น คำแนะนำ 3 ข้อ, ตารางสรุป, แผนการเทรดสั้นๆ"
            disabled={status === "loading"}
          />
        </label>

        <div className="panel-actions">
          <button
            type="submit"
            className="btn-primary"
            disabled={status === "loading" || !task.trim()}
          >
            {status === "loading" ? (
              <>
                <span className="spinner" /> กำลังประมวลผล…
              </>
            ) : (
              "ส่งคำสั่ง"
            )}
          </button>

          {status !== "idle" && (
            <button type="button" className="btn-ghost" onClick={handleClear}>
              ล้าง
            </button>
          )}
        </div>
      </form>

      {status === "error" && (
        <div className="result-box result-error">
          <strong>เกิดข้อผิดพลาด</strong>
          <p>{error}</p>
        </div>
      )}

      {status === "success" && (
        <div className="result-box result-success">
          <div className="result-header">
            <span>ผลลัพธ์จากเลขา</span>
            <button
              className="btn-copy"
              onClick={() => navigator.clipboard.writeText(result)}
            >
              คัดลอก
            </button>
          </div>
          <pre className="result-text">{result}</pre>
        </div>
      )}
    </div>
  );
}
