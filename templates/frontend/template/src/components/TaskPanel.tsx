type Task = {
  id: string;
  title: string;
  status: string;
};

type TaskPanelProps = {
  title: string;
  tasks: Task[];
};

export function TaskPanel({ title, tasks }: TaskPanelProps) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h2>{title}</h2>
        <span>{tasks.length} items</span>
      </div>
      <div className="task-list">
        {tasks.map((task) => (
          <article className="task-row" key={task.id}>
            <div>
              <strong>{task.title}</strong>
              <p>{task.id}</p>
            </div>
            <span className="task-row__status">{task.status}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
