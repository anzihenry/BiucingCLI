import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import { Welcome } from "./welcome";
import { renderToString } from "react-dom/server";

test("server HTML keeps JavaScript-only actions disabled", () => {
  const container = document.createElement("div");
  container.innerHTML = renderToString(<Welcome />);
  const buttons = container.querySelectorAll("button");
  expect(buttons).toHaveLength(2);
  for (const button of buttons) expect(button).toBeDisabled();
});

test("increments and opens an accessible dialog", async () => {
  const user = userEvent.setup();
  render(<Welcome />);
  await user.click(screen.getByRole("button", { name: "Count: 0" }));
  expect(screen.getByRole("button", { name: "Count: 1" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "About this starter" }));
  expect(
    await screen.findByRole("dialog", { name: "Ready to build" }),
  ).toBeInTheDocument();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});
