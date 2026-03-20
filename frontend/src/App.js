import { useEffect, useState } from "react";
import { calculatePrice, getProviders } from "./api";
import BarChart from "./components/BarChart";
import ModelCard from "./components/ModelCard";
import ModelSelector from "./components/ModelSelector";
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
    try {
      // ✅ Prevent empty payload (VERY IMPORTANT)
      if (!selectedModels || Object.keys(selectedModels).length === 0) {
        console.error("No models selected");
        return;
      }

      const payload = {
        input_tokens: Number(inputTokens),
        output_tokens: Number(outputTokens),
        requests_per_day: Number(requests),
        selected_models: selectedModels,
      };

      console.log("Sending payload:", payload); // 🔍 DEBUG

      const res = await calculatePrice(payload);

      console.log("Response:", res.data); // 🔍 DEBUG

      setResults(res.data.results);
    } catch (err) {
      console.error("API Error:", err.response?.data || err.message);
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>AI Price Checker 🚀</h1>

      {/* Inputs */}
      <div>
        <label>Input Tokens:</label>
        <input
          type="number"
          value={inputTokens}
          onChange={(e) => setInputTokens(e.target.value)}
        />
      </div>

      <div>
        <label>Output Tokens:</label>
        <input
          type="number"
          value={outputTokens}
          onChange={(e) => setOutputTokens(e.target.value)}
        />
      </div>

      <div>
        <label>Requests per day:</label>
        <input
          type="number"
          value={requests}
          onChange={(e) => setRequests(e.target.value)}
        />
      </div>

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