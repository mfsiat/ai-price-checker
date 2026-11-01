import { render, screen, fireEvent, within } from "@testing-library/react";
import App from "./App";
import { getProviders, calculatePrice } from "./api";

// Avoid real network calls: the backend is not available in the test env.
jest.mock("./api");

// Charts render on <canvas> via chart.js, which isn't supported in jsdom.
// Stub them so this test can focus on result ordering (issue #14).
jest.mock("./components/BarChart", () => () => null);
jest.mock("./components/PieChart", () => () => null);

// A model entry with every field ModelSelector/ModelCard read, so rendering
// the populated UI doesn't throw. Values are irrelevant to the sort test.
const MODEL = {
  input: 1,
  output: 2,
  context: 128000,
  speed: "fast",
  tier: "standard",
  multimodal: false,
  vision: false,
};

// Two providers so selectedModels is populated and /calculate is driven.
const PROVIDERS = {
  providers: {
    openai: { models: { "gpt-x": { ...MODEL } } },
    anthropic: { models: { "claude-x": { ...MODEL } } },
  },
};

// Deliberately returned OUT of ascending cost order. App must sort these
// before rendering so the cheapest row comes first.
const UNSORTED_RESULTS = [
  { provider: "openai", model: "gpt-x", monthly_cost: 30 },
  { provider: "anthropic", model: "claude-x", monthly_cost: 10 },
  { provider: "google", model: "gemini-x", monthly_cost: 20 },
];

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  getProviders.mockResolvedValue({ data: PROVIDERS });
  calculatePrice.mockResolvedValue({ data: { results: UNSORTED_RESULTS } });
});

async function renderAndCalculate() {
  render(<App />);
  await screen.findByText(/ai price checker/i);
  fireEvent.click(screen.getByRole("button", { name: /calculate costs/i }));
  // Wait for the results table to appear.
  await screen.findByRole("table");
}

test("renders result rows sorted ascending by monthly cost (issue #14)", async () => {
  await renderAndCalculate();

  const table = screen.getByRole("table");
  const costCells = within(table)
    .getAllByText(/^\$\d+(\.\d+)?$/)
    .map((el) => parseFloat(el.textContent.replace("$", "")));

  expect(costCells).toEqual([10, 20, 30]);
  // Explicitly assert ascending order, independent of the exact values.
  const ascending = [...costCells].sort((a, b) => a - b);
  expect(costCells).toEqual(ascending);
});

test("ranks the cheapest model first in the table (issue #14)", async () => {
  await renderAndCalculate();

  const rows = screen.getAllByRole("row").slice(1); // drop header row
  const firstRowText = rows[0].textContent;
  expect(firstRowText).toMatch(/anthropic/);
  expect(firstRowText).toMatch(/\$10/);
});
