
const ModelSelector = ({ models, selectedModels, setSelectedModels }) => {
  return (
    <div>
      <h3>Select Models</h3>

      {Object.keys(models).map((provider) => (
        <div key={provider} style={{ marginBottom: "10px" }}>
          <label style={{ marginRight: "10px" }}>{provider}</label>

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
                {model} | ${data.input}/${data.output} | {data.speed} | {data.tier}
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
};

export default ModelSelector;