import React from "react";

const ModelCard = ({ provider, model, data }) => {
  if (!data) return null;

  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "10px",
        borderRadius: "8px",
        marginBottom: "10px",
        width: "250px",
      }}
    >
      <h4>{provider} - {model}</h4>
      <p>Context: {data.context}</p>
      <p>Speed: {data.speed}</p>
      <p>Tier: {data.tier}</p>
      <p>Multimodal: {data.multimodal ? "Yes" : "No"}</p>
      <p>Vision: {data.vision ? "Yes" : "No"}</p>
    </div>
  );
};

export default ModelCard;
