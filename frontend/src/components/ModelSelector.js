import React from "react";

const ModelSelector = ({ models, selectedModels, setSelectedModels }) => {
  return (
    <div className="selector-grid">
      {Object.keys(models).map((provider) => (
        <div key={provider} className="selector-row">
          <span className="selector-provider">{provider}</span>

          <select
            value={selectedModels[provider] || ""}
            onChange={(e) =>
              setSelectedModels({
                ...selectedModels,
                [provider]: e.target.value,
              })
            }
          >
            {Object.entries(models[provider].models).map(([model, data]) => (
              <option key={model} value={model}>
                {model} | ${data.input.toFixed(2)}/${data.output.toFixed(2)} |{" "}
                {data.speed} | {data.tier}
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
};

export default ModelSelector;
