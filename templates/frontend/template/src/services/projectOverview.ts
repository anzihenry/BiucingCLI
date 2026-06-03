import type { ProjectOverview } from "../types/projectOverview";

export function getProjectOverview(): ProjectOverview {
  return {
    title: "{{DISPLAY_NAME}}",
    description:
      "A practical React + TypeScript starter with a small UI structure, a lightweight service layer, and room to grow without cleanup first.",
    tags: ["React", "TypeScript", "Vite", "BiucingCLI"],
    metrics: [
      { label: "Screens ready", value: "1", tone: "amber" },
      { label: "Shared services", value: "1", tone: "slate" },
      { label: "UI building blocks", value: "2", tone: "slate" },
    ],
    buildQueue: [
      { id: "task_01", title: "Replace starter copy with product copy", status: "Ready" },
      { id: "task_02", title: "Connect API requests in services layer", status: "Planned" },
      { id: "task_03", title: "Split HomePage into route-level screens", status: "Backlog" },
    ],
    notes: [
      { id: "note_01", title: "Start with pages as feature entrypoints", status: "Pattern" },
      { id: "note_02", title: "Keep API logic inside services", status: "Pattern" },
      { id: "note_03", title: "Promote components only when reused", status: "Reminder" },
    ],
  };
}
