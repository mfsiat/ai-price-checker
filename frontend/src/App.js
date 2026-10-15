import React, { useEffect, useState } from "react";
import { getProviders, calculatePrice } from "./api";
import ModelSelector from "./components/ModelSelector";
import ModelCard from "./components/ModelCard";
import BarChart from "./components/BarChart";
import PieChart from "./components/PieChart";
import PriceTable from "./components/PriceTable";

function App() {
  const [models, setModels] = useState({});
  const [selectedModels, setSelectedModels] = useState({});
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [inputTokens, setInputTokens] = useState(2000);
  const [outputTokens, setOutputTokens] = useState(500);
  const [requests, setRequests] = useState(1000);

  const [theme, setTheme] = useState(
    () => localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    getProviders()
      .then((res) => {
        setModels(res.data);

        const defaults = {};
        Object.keys(res.data).forEach((provider) => {
          defaults[provider] = Object.keys(res.data[provider].models)[0];
        });

        setSelectedModels(defaults);
      })
      .catch(() => setError("Failed to load providers. Is the backend running?"));
  }, []);

  const calculate = async () => {
    if (inputTokens < 1 || outputTokens < 1 || requests < 1) {
      setError("All token inputs must be at least 1.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await calculatePrice({
        input_tokens: inputTokens,
        output_tokens: outputTokens,
        requests_per_day: requests,
        selected_models: selectedModels,
      });
      setResults(
        [...res.data.results].sort((a, b) => a.monthly_cost - b.monthly_cost)
      );
    } catch {
      setError("Calculation failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const cheapest = results.length ? results[0] : null;
  const hasResults = results.length > 0;

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1 className="app-title">AI Price Checker 🚀</h1>
          <p className="app-subtitle">
            Compare monthly LLM costs across providers in seconds.
          </p>
        </div>
        <button
          className="theme-toggle"
          onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
          aria-label="Toggle color theme"
        >
          {theme === "light" ? "🌙 Dark" : "☀️ Light"}
        </button>
      </header>

      {/* Inputs */}
      <section className="card">
        <h2 className="card-title">⚙️ Usage</h2>
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Input tokens / request</span>
            <input
              value={inputTokens}
              onChange={(e) => setInputTokens(parseInt(e.target.value, 10) || 0)}
              type="number"
              min="1"
            />
          </label>
          <label className="field">
            <span className="field-label">Output tokens / request</span>
            <input
              value={outputTokens}
              onChange={(e) =>
                setOutputTokens(parseInt(e.target.value, 10) || 0)
              }
              type="number"
              min="1"
            />
          </label>
          <label className="field">
            <span className="field-label">Requests / day</span>
            <input
              value={requests}
              onChange={(e) => setRequests(parseInt(e.target.value, 10) || 0)}
              type="number"
              min="1"
            />
          </label>
        </div>
      </section>

      {/* Model selection */}
      <section className="card">
        <h2 className="card-title">🧩 Models</h2>
        <ModelSelector
          models={models}
          selectedModels={selectedModels}
          setSelectedModels={setSelectedModels}
        />
        <div className="actions-row">
          <button
            className="btn-primary"
            onClick={calculate}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" /> Calculating…
              </>
            ) : (
              <>Calculate costs</>
            )}
          </button>
        </div>
        {error && <div className="alert-error">⚠️ {error}</div>}
      </section>

      {/* Model Cards */}
      <div className="model-grid" style={{ marginTop: 24 }}>
        {Object.keys(selectedModels).map((provider) => {
          const model = selectedModels[provider];
          const data = models[provider]?.models?.[model];
          const resultEntry = results.find(
            (r) => r.provider === provider && r.model === model
          );
          const isBest =
            cheapest &&
            cheapest.provider === provider &&
            cheapest.model === model;

          return (
            <ModelCard
              key={provider}
              provider={provider}
              model={model}
              data={data}
              monthlyCost={resultEntry?.monthly_cost}
              isBest={isBest}
            />
          );
        })}
      </div>

      {/* Results */}
      {hasResults ? (
        <>
          <h2 className="section-title">📊 Cost comparison</h2>
          <section className="card">
            <div className="charts-grid">
              <div className="chart-box">
                <BarChart results={results} />
              </div>
              <div className="chart-box">
                <PieChart results={results} />
              </div>
            </div>
          </section>

          <section className="card">
            <PriceTable results={results} />
          </section>
        </>
      ) : (
        <section className="card" style={{ marginTop: 24 }}>
          <div className="empty-state">
            <div className="empty-state-icon">📈</div>
            <div className="empty-state-text">
              Pick your models and hit <strong>Calculate costs</strong> to see a
              side-by-side breakdown.
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
