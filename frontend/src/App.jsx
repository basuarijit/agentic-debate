import { Gavel, LoaderCircle, MessageSquareQuote, Play, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { getDebate, startDebate } from "./api/debates.js";

const terminalStatuses = new Set(["completed", "failed"]);

function splitTurns(turns) {
  return {
    pro: turns.filter((turn) => turn.agent_role === "pro"),
    con: turns.filter((turn) => turn.agent_role === "con"),
  };
}

function formatStatus(status) {
  return status ? status.replace("_", " ") : "not started";
}

function App() {
  const [debate, setDebate] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState("");
  const pollTimerRef = useRef(null);

  const turnsBySide = useMemo(
    () => splitTurns(debate?.turns ?? []),
    [debate?.turns],
  );

  const isRunning =
    Boolean(debate) && !terminalStatuses.has(debate.status) && !isStarting;
  const isJudging = debate?.status === "judging";

  useEffect(() => {
    return () => {
      if (pollTimerRef.current) {
        window.clearInterval(pollTimerRef.current);
      }
    };
  }, []);

  async function pollDebate(debateId) {
    const latest = await getDebate(debateId);
    setDebate(latest);

    if (terminalStatuses.has(latest.status) && pollTimerRef.current) {
      window.clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  }

  async function handleStartDebate() {
    setError("");
    setIsStarting(true);
    setDebate(null);

    if (pollTimerRef.current) {
      window.clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }

    try {
      const created = await startDebate();
      const latest = await getDebate(created.debate_id);
      setDebate(latest);

      if (!terminalStatuses.has(latest.status)) {
        pollTimerRef.current = window.setInterval(() => {
          pollDebate(created.debate_id).catch((err) => {
            setError(err.message);
            window.clearInterval(pollTimerRef.current);
            pollTimerRef.current = null;
          });
        }, 700);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsStarting(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="top-bar">
        <div>
          <p className="eyebrow">Agentic Debate</p>
          <h1>AI Agent Debate Arena</h1>
        </div>
        <button
          className="start-button"
          type="button"
          onClick={handleStartDebate}
          disabled={isStarting || isRunning}
          title="Start Debate"
        >
          {isStarting || isRunning ? (
            <LoaderCircle className="spin" size={20} />
          ) : debate ? (
            <RotateCcw size={20} />
          ) : (
            <Play size={20} />
          )}
          <span>{debate ? "Start New Debate" : "Start Debate"}</span>
        </button>
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="topic-band">
        <div>
          <p className="section-label">Topic</p>
          <h2>{debate?.topic ?? "Click Start Debate to select a topic."}</h2>
        </div>
        <div className="status-pill">{formatStatus(debate?.status)}</div>
      </section>

      <section className="debate-section" aria-label="Debate arguments">
        <PartyColumn
          title="Party A"
          subtitle="Argues in favor"
          role="pro"
          turns={turnsBySide.pro}
          accent="green"
          isRunning={isRunning}
        />
        <PartyColumn
          title="Party B"
          subtitle="Argues against"
          role="con"
          turns={turnsBySide.con}
          accent="red"
          isRunning={isRunning}
        />
      </section>

      <section className="judge-section">
        <div className="judge-heading">
          <Gavel size={22} />
          <div>
            <p className="section-label">Judge&apos;s Result</p>
            <h2>{resultTitle(debate)}</h2>
          </div>
        </div>
        <p className="judge-summary">
          {isJudging
            ? "The judge agent is evaluating both parties and preparing the result."
            : debate?.result?.judge_summary ??
              "The judge's result will appear after both parties complete three turns."}
        </p>
      </section>
    </main>
  );
}

function PartyColumn({ title, subtitle, role, turns, accent, isRunning }) {
  return (
    <article className={`party-column ${accent}`}>
      <div className="party-header">
        <div>
          <p className="party-kicker">{role === "pro" ? "Pro" : "Con"}</p>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <div className="turn-count">{turns.length}/3</div>
      </div>

      <div className="turn-list">
        {turns.length === 0 ? (
          <div className="empty-turns">
            {isRunning ? (
              <LoaderCircle className="spin" size={20} />
            ) : (
              <MessageSquareQuote size={20} />
            )}
            <span>Waiting for this party&apos;s opening argument.</span>
          </div>
        ) : (
          <>
            {turns.map((turn) => (
              <section className="turn-card" key={turn.turn_number}>
                <div className="turn-meta">
                  <span>Turn {turn.turn_number}</span>
                  <span>{new Date(turn.created_at).toLocaleTimeString()}</span>
                </div>
                <p>{turn.content}</p>
              </section>
            ))}
            {isRunning && turns.length < 3 ? (
              <div className="processing-turn">
                <LoaderCircle className="spin" size={18} />
                <span>Next argument is being prepared.</span>
              </div>
            ) : null}
          </>
        )}
      </div>
    </article>
  );
}

function resultTitle(debate) {
  if (!debate) {
    return "Awaiting debate";
  }
  if (debate.status === "failed") {
    return "Debate failed";
  }
  if (!debate.result) {
    return "Judging pending";
  }
  return debate.result.winner === "pro" ? "Party A wins" : "Party B wins";
}

export default App;
