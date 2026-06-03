export type MetricTone = "amber" | "slate";

export type ProjectTask = {
  id: string;
  title: string;
  status: string;
};

export type ProjectMetric = {
  label: string;
  value: string;
  tone: MetricTone;
};

export type ProjectOverview = {
  title: string;
  description: string;
  tags: string[];
  metrics: ProjectMetric[];
  buildQueue: ProjectTask[];
  notes: ProjectTask[];
};
