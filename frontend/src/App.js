import React, { useEffect, useState } from "react";
import { getProviders, calculatePrice } from "./api";
import ModelSelector from "./components/ModelSelector";
import ModelCard from "./components/ModelCard";
import BarChart from "./components/BarChart";
import PieChart from "./components/PieChart";

function App() {
  const [models, setModels] = useState({});
  const [selectedModels, setSelectedModels] = useState({});
  const [results, setResults] = useState([]);

  const [inputTokens, setInputTokens] = useState(2000);
  const [outputTokens, setOutputTokens] = useState(500);
  const [requests, setRequests] = useState(1000);

  useEffect(() => {
    getProviders().then((res) => {
      setModels(res.data);

      const defaults = {};
      Object.keys(res.data).forEach((provider) => {
        defaults[provider] = Object.keys(res.data[provider].models)[0];
      });

      setSelectedModels(defaults);
    });
  }, []);

  const calculate = async () => {
    const res = await calculatePrice({
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      requests_per_day: requests,
      selected_models: selectedModels,
    });

    setResults(res.data.results);
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>AI Price Checker 🚀</h1>

      {/* Inputs */}
      <input value={inputTokens} onChange={(e) => setInputTokens(e.target.value)} />
      <input value={outputTokens} onChange={(e) => setOutputTokens(e.target.value)} />
      <input value={requests} onChange={(e) => setRequests(e.target.value)} />

      <ModelSelector
        models={models}
        selectedModels={selectedModels}
        setSelectedModels={setSelectedModels}
      />

      <button onClick={calculate}>Calculate</button>

      {/* Model Cards */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
        {Object.keys(selectedModels).map((provider) => {
          const model = selectedModels[provider];
          const data = models[provider]?.models?.[model];

          return (
            <ModelCard
              key={provider}
              provider={provider}
              model={model}
              data={data}
            />
          );
        })}
      </div>

      {/* Charts */}
      <div style={{ display: "flex", marginTop: "40px" }}>
        <div style={{ width: "50%" }}>
          <BarChart results={results} />
        </div>
        <div style={{ width: "50%" }}>
          <PieChart results={results} />
        </div>
      </div>
    </div>
  );
}

export default App;
