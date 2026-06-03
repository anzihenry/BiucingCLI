import { MetricCard } from "../components/MetricCard";
import { TaskPanel } from "../components/TaskPanel";
import { useProjectOverview } from "../hooks/useProjectOverview";

export function HomePage() {
  const overview = useProjectOverview();

  if (!overview) {
    return (
      <main className="app-shell">
        <div className="workspace">
          <section className="hero">
            <p className="hero__eyebrow">BiucingCLI</p>
            <div className="hero__headline">
              <h1>{{DISPLAY_NAME}}</h1>
              <p>Loading your starter workspace...</p>
            </div>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <div className="workspace">
        <section className="hero">
          <p className="hero__eyebrow">BiucingCLI</p>
          <div className="hero__headline">
            <h1>{overview.title}</h1>
            <p>{overview.description}</p>
          </div>
          <div className="hero__meta">
            {overview.tags.map((tag) => (
              <span className="hero__tag" key={tag}>
                {tag}
              </span>
            ))}
          </div>
        </section>

        <section className="metrics">
          {overview.metrics.map((metric) => (
            <MetricCard
              key={metric.label}
              label={metric.label}
              value={metric.value}
              tone={metric.tone}
            />
          ))}
        </section>

        <section className="panels">
          <TaskPanel title="Build Queue" tasks={overview.buildQueue} />
          <TaskPanel title="Project Notes" tasks={overview.notes} />
        </section>
      </div>
    </main>
  );
}
