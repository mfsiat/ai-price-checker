# Frontend Testing

This document describes the automated tests for the AI Price Checker frontend
and how they are run locally and in CI.

## Stack

- **Test runner:** Jest (via `react-scripts test`)
- **Rendering / DOM assertions:** [@testing-library/react](https://testing-library.com/docs/react-testing-library/intro/)
  and [@testing-library/jest-dom](https://github.com/testing-library/jest-dom)
- **Test files:** `src/**/*.test.js`
- **Shared setup:** `src/setupTests.js` (loads the `jest-dom` matchers)

## Running the tests

```bash
cd frontend

# Watch mode (interactive, re-runs on change) — for local development
npm test

# Single run, as CI runs it (no watch, non-zero exit on failure)
CI=true npm test

# Single run with a coverage report
CI=true npm test -- --coverage --watchAll=false
```

> `CI=true` is important: it makes `react-scripts` run the suite **once** and
> exit with a non-zero status if anything fails (instead of entering watch
> mode). This is exactly how the CI pipeline invokes it.

## What is covered

The suite focuses on the interactive logic introduced by the UI redesign
(issue #17). Styling itself is not asserted; **behavior** is.

### `src/App.test.js`

| Test | Behavior verified |
| --- | --- |
| `renders app heading` | The app mounts and the main heading is shown. |
| `shows the empty state before any calculation` | Before any calculation, the placeholder/empty-state card and the **Calculate costs** button are rendered. |
| `theme toggle › defaults to the light theme` | On first load the document uses `data-theme="light"` and the toggle offers to switch to **Dark**. |
| `theme toggle › switches to dark and persists the choice` | Clicking the toggle sets `data-theme="dark"` on `<html>`, writes `theme=dark` to `localStorage`, and flips the label to offer **Light**. |
| `theme toggle › toggles back to light on a second click` | A second click returns to the light theme and updates `localStorage`. |
| `theme toggle › restores a saved theme from localStorage on load` | A previously saved `theme=dark` is applied automatically on load. |

### Test design notes

These notes capture decisions that are easy to get wrong when extending the
suite:

- **The backend is mocked.** `./api` is replaced with `jest.mock("./api")` so
  `getProviders()` makes no real network request. The mock implementation is
  (re)applied in `beforeEach` because `react-scripts` enables
  `resetMocks: true`, which clears mock implementations between tests — a
  factory-level implementation would be wiped after the first test.
- **The theme toggle is queried by its `aria-label`**
  (`"Toggle color theme"`), not by its visible text. An `aria-label` becomes
  the element's *accessible name*, so `getByRole("button", { name: /dark/i })`
  would not match; the visible "Dark"/"Light" text is asserted separately with
  `toHaveTextContent`.
- **"Calculate costs" appears twice** — once on the button and once inside the
  empty-state hint text. Target the button with
  `getByRole("button", { name: /calculate costs/i })` to avoid an ambiguous
  `getByText` match.
- **`localStorage` and `data-theme` are reset** in `beforeEach` so theme tests
  do not leak state into one another.

## Adding new tests

1. Create `src/<Component>.test.js` (or add to `App.test.js`).
2. Prefer role-based queries (`getByRole`) and user-visible text over CSS
   classes or test IDs.
3. Mock `./api` for anything that would otherwise hit the backend.
4. Verify locally with `CI=true npm test` before pushing — CI runs the exact
   same command.

## Continuous Integration

`.gitlab-ci.yml` at the repository root defines the pipeline:

- **`frontend:test`** (stage `test`) — installs deps with `npm ci` and runs
  `CI=true npm test ... --coverage`. This is the **merge gate**: a merge
  request into `master` cannot be merged while this job fails. Coverage is
  reported to the merge request widget (Cobertura).
- **`frontend:build`** (stage `build`) — runs `npm run build` to confirm the
  production bundle still compiles. Runs after the test job passes.

Both jobs run on merge requests targeting `master` and on pushes to `master`.
To make the test job a hard merge requirement, enable
**Settings → Merge requests → Pipelines must succeed** in the GitLab project.
