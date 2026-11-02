import { render, screen, fireEvent, within } from "@testing-library/react";
import App from "./App";
import { getProviders, calculatePrice } from "./api";

// Avoid real network calls.
jest.mock("./api");

// Charts render on <canvas> (chart.js) which jsdom can't do.
jest.mock("./components/BarChart", () => () => null);
jest.mock("./components/PieChart", () => () => null);

const MODEL = {
  input: 1,
  output: 2,
  context: 128000,
  speed: "fast",
  tier: "standard",
  multimodal: false,
  vision: false,
};

const PROVIDERS = {
  providers: {
    openai: { models: { "gpt-x": { ...MODEL } } },
  },
};

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  getProviders.mockResolvedValue({ data: PROVIDERS });
});

async function renderAndCalculate() {
  render(<App />);
  await screen.findByText(/ai price checker/i);
  fireEvent.click(screen.getByRole("button", { name: /calculate costs/i }));
}

test("shows a warning when the backend reports skipped models", async () => {
  calculatePrice.mockResolvedValue({
    data: {
      results: [{ provider: "openai", model: "gpt-x", monthly_cost: 10 }],
      warnings: [{ provider: "ghost", model: "x", reason: "unknown" }],
    },
  });

  await renderAndCalculate();

  const warning = await screen.findByText(/skipped 1 unrecognized model/i);
  expect(warning).toHaveTextContent("ghost/x");
});

test("shows a distinct empty state after a calculation returns no results", async () => {
  calculatePrice.mockResolvedValue({
    data: { results: [], warnings: [{ provider: "ghost", model: "x" }] },
  });

  await renderAndCalculate();

  // The post-calculation empty state differs from the initial prompt.
  expect(
    await screen.findByText(/none of the selected models were found/i)
  ).toBeInTheDocument();
  // No results table should be rendered.
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
});

test("renders a results table and no warning when everything resolves", async () => {
  calculatePrice.mockResolvedValue({
    data: {
      results: [{ provider: "openai", model: "gpt-x", monthly_cost: 10 }],
      warnings: [],
    },
  });

  await renderAndCalculate();

  const table = await screen.findByRole("table");
  expect(within(table).getByText("$10")).toBeInTheDocument();
  expect(screen.queryByText(/unrecognized model/i)).not.toBeInTheDocument();
});
