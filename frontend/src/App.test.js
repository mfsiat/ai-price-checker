import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App";
import { getProviders } from "./api";

// Avoid real network calls: the backend is not available in the test env.
jest.mock("./api");

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  // Re-set the implementation each test — react-scripts enables resetMocks,
  // which clears mock implementations between tests.
  getProviders.mockResolvedValue({ data: {} });
});

// Let the getProviders() effect settle so we don't leak act() warnings.
async function renderApp() {
  render(<App />);
  await screen.findByText(/ai price checker/i);
}

test("renders app heading", async () => {
  await renderApp();
  expect(screen.getByText(/ai price checker/i)).toBeInTheDocument();
});

test("shows the empty state before any calculation", async () => {
  await renderApp();
  expect(screen.getByText(/to see a/i)).toBeInTheDocument();
  expect(
    screen.getByRole("button", { name: /calculate costs/i })
  ).toBeInTheDocument();
});

describe("theme toggle", () => {
  // The button is identified by its aria-label; its visible text reflects
  // the theme it will switch *to*.
  const toggle = () =>
    screen.getByRole("button", { name: /toggle color theme/i });

  test("defaults to the light theme", async () => {
    await renderApp();
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    // In light mode the button offers to switch to dark.
    expect(toggle()).toHaveTextContent(/dark/i);
  });

  test("switches to dark and persists the choice", async () => {
    await renderApp();
    fireEvent.click(toggle());

    await waitFor(() =>
      expect(document.documentElement.getAttribute("data-theme")).toBe("dark")
    );
    expect(localStorage.getItem("theme")).toBe("dark");
    // Label flips to offer switching back to light.
    expect(toggle()).toHaveTextContent(/light/i);
  });

  test("toggles back to light on a second click", async () => {
    await renderApp();
    fireEvent.click(toggle()); // -> dark
    fireEvent.click(toggle()); // -> light

    await waitFor(() =>
      expect(document.documentElement.getAttribute("data-theme")).toBe("light")
    );
    expect(localStorage.getItem("theme")).toBe("light");
  });

  test("restores a saved theme from localStorage on load", async () => {
    localStorage.setItem("theme", "dark");
    await renderApp();
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });
});
