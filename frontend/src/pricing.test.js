import fs from "fs";
import path from "path";

// The pricing data is owned by the backend (backend/app/pricing.json) and
// served to the frontend via GET /providers. These tests validate that the
// on-disk pricing data is well-formed and internally consistent, so a bad
// edit (typo'd price, missing field, malformed structure) fails CI before it
// can reach production. We read the file directly with fs rather than
// importing it, because Create React App forbids imports from outside src/.
const PRICING_PATH = path.resolve(
  __dirname,
  "..",
  "..",
  "backend",
  "app",
  "pricing.json"
);

const raw = fs.readFileSync(PRICING_PATH, "utf8");
const pricing = JSON.parse(raw);

// Every provider → model entry, flattened for per-model assertions.
const modelEntries = Object.entries(pricing.providers).flatMap(
  ([provider, pdata]) =>
    Object.entries(pdata.models).map(([model, data]) => [
      `${provider}/${model}`,
      data,
    ])
);

describe("pricing.json — top-level structure", () => {
  test("is valid JSON with last_updated and providers", () => {
    expect(typeof pricing).toBe("object");
    expect(pricing).toHaveProperty("last_updated");
    expect(pricing).toHaveProperty("providers");
  });

  test("last_updated is an ISO date (YYYY-MM-DD)", () => {
    expect(pricing.last_updated).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    // Must be a real, parseable calendar date.
    expect(Number.isNaN(Date.parse(pricing.last_updated))).toBe(false);
  });

  test("providers is a non-empty object", () => {
    expect(typeof pricing.providers).toBe("object");
    expect(pricing.providers).not.toBeNull();
    expect(Object.keys(pricing.providers).length).toBeGreaterThan(0);
  });

  test("every provider has a non-empty models map", () => {
    for (const [provider, pdata] of Object.entries(pricing.providers)) {
      expect(pdata).toHaveProperty("models");
      expect(Object.keys(pdata.models).length).toBeGreaterThan(0);
    }
  });
});

describe("pricing.json — per-model validation", () => {
  const REQUIRED_NUMERIC = ["input", "output", "context"];
  const REQUIRED_BOOLEAN = ["multimodal", "vision"];
  const REQUIRED_STRING = ["speed", "tier"];

  test("there is at least one model to validate", () => {
    expect(modelEntries.length).toBeGreaterThan(0);
  });

  test.each(modelEntries)("%s has all required fields", (_id, data) => {
    for (const key of [
      ...REQUIRED_NUMERIC,
      ...REQUIRED_BOOLEAN,
      ...REQUIRED_STRING,
    ]) {
      expect(data).toHaveProperty(key);
    }
  });

  test.each(modelEntries)(
    "%s has positive, sane input/output prices",
    (_id, data) => {
      for (const key of ["input", "output"]) {
        expect(typeof data[key]).toBe("number");
        expect(Number.isFinite(data[key])).toBe(true);
        // Prices are USD per 1M tokens: must be positive and within a
        // realistic ceiling (nothing on the market is >$1000 / 1M tokens).
        expect(data[key]).toBeGreaterThan(0);
        expect(data[key]).toBeLessThan(1000);
      }
    }
  );

  test.each(modelEntries)(
    "%s has a positive integer context window",
    (_id, data) => {
      expect(typeof data.context).toBe("number");
      expect(Number.isInteger(data.context)).toBe(true);
      expect(data.context).toBeGreaterThan(0);
    }
  );

  test.each(modelEntries)("%s has boolean capability flags", (_id, data) => {
    for (const key of REQUIRED_BOOLEAN) {
      expect(typeof data[key]).toBe("boolean");
    }
  });

  test.each(modelEntries)(
    "%s has non-empty speed and tier labels",
    (_id, data) => {
      for (const key of REQUIRED_STRING) {
        expect(typeof data[key]).toBe("string");
        expect(data[key].trim().length).toBeGreaterThan(0);
      }
    }
  );

  test.each(modelEntries)(
    "%s does not price output below input (standard LLM pricing)",
    (_id, data) => {
      // Across every current provider, output tokens cost >= input tokens.
      // This catches a common data-entry mistake: swapping the two values.
      expect(data.output).toBeGreaterThanOrEqual(data.input);
    }
  );

  test.each(modelEntries)(
    "%s cannot be vision-capable without being multimodal",
    (_id, data) => {
      if (data.vision) {
        expect(data.multimodal).toBe(true);
      }
    }
  );
});
