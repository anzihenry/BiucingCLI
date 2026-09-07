import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";
import { getProjectOverview } from "./services/projectOverview";

describe("App", () => {
  it("renders the project overview content", async () => {
    const overview = await getProjectOverview();

    render(<App />);

    expect(await screen.findByRole("heading", { name: overview.title })).toBeInTheDocument();
    expect(screen.getByText(overview.description)).toBeInTheDocument();
    expect(screen.getByText("Build Queue")).toBeInTheDocument();
    expect(screen.getByText("Project Notes")).toBeInTheDocument();
  });
});
