import React from "react";

const ModelCard = ({ provider, model, data, monthlyCost, isBest }) => {
  if (!data) return null;

  const yesNo = (v) => (
    <span className={`badge ${v ? "badge-yes" : "badge-no"}`}>
      {v ? "Yes" : "No"}
    </span>
  );

  return (
    <div className={`model-card${isBest ? " is-best" : ""}`}>
      {isBest && <span className="badge badge-best">Best value</span>}

      <div className="model-card-provider">{provider}</div>
      <div className="model-card-name">{model}</div>

      {monthlyCost !== undefined && (
        <div className="model-cost">
          ${monthlyCost} <span>/ month</span>
        </div>
      )}

      <div className="spec-list">
        <div className="spec-row">
          <span className="spec-key">Context</span>
          <span className="spec-val">{data.context}</span>
        </div>
        <div className="spec-row">
          <span className="spec-key">Speed</span>
          <span className="spec-val">{data.speed}</span>
        </div>
        <div className="spec-row">
          <span className="spec-key">Tier</span>
          <span className="spec-val">{data.tier}</span>
        </div>
        <div className="spec-row">
          <span className="spec-key">Multimodal</span>
          <span className="spec-val">{yesNo(data.multimodal)}</span>
        </div>
        <div className="spec-row">
          <span className="spec-key">Vision</span>
          <span className="spec-val">{yesNo(data.vision)}</span>
        </div>
      </div>
    </div>
  );
};

export default ModelCard;
