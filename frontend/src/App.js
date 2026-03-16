import React, { useState, useEffect } from "react";
import axios from "axios";
import PieChart from "./components/PieChart";
import BarChart from "./components/BarChart";

function App() {
  const [inputTokens, setInputTokens] = useState(2000);
  const [outputTokens, setOutputTokens] = useState(500);
  const [requests, setRequests] = useState(1000);
  const [providers, setProviders] = useState([]);
  const [selectedProviders, setSelectedProviders] = useState([]);
  const [results, setResults] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/providers")
      .then((res) => {
        const keys = Object.keys(res.data);
        setProviders(keys);
        setSelectedProviders(keys);
      })
      .catch((err) => console.log(err));
  }, []);

  const handleProviderChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setSelectedProviders([...selectedProviders, value]);
    } else {
      setSelectedProviders(selectedProviders.filter((p) => p !== value));
    }
  };

  const calculate = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/calculate", {
        input_tokens: Number(inputTokens),
        output_tokens: Number(outputTokens),
        requests_per_day: Number(requests),
        providers: selectedProviders,
      });
      setResults(response.data.results);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>AI Price Checker</h1>

      {/* Inputs */}
      <div style={{ marginTop: "20px" }}>
        <label>Input Tokens:</label>
        <input
          type="number"
          value={inputTokens}
          onChange={(e) => setInputTokens(e.target.value)}
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <label>Output Tokens:</label>
        <input
          type="number"
          value={outputTokens}
          onChange={(e) => setOutputTokens(e.target.value)}
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <label>Requests per day:</label>
        <input
          type="number"
          value={requests}
          onChange={(e) => setRequests(e.target.value)}
        />
      </div>

      <div style={{ marginTop: "20px" }}>
        <label>Select Providers:</label>
        <div>
          {providers.map((provider) => (
            <label key={provider} style={{ marginRight: "15px" }}>
              <input
                type="checkbox"
                value={provider}
                checked={selectedProviders.includes(provider)}
                onChange={handleProviderChange}
              />
              {provider}
            </label>
          ))}
        </div>
      </div>

      <button
        onClick={calculate}
        style={{ marginTop: "20px", padding: "10px 20px" }}
      >
        Calculate Price
      </button>

      {/* Charts side by side */}
      <div style={{ display: "flex", justifyContent: "space-around", marginTop: "40px" }}>
        <div style={{ flex: 1, maxWidth: "600px" }}>
          <BarChart results={results} />
        </div>
        <div style={{ flex: 1, maxWidth: "500px" }}>
          <PieChart results={results} />
        </div>
      </div>
    </div>
  );
}

export default App;
