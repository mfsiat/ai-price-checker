import React from "react";

const PriceTable = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <table className="price-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Provider</th>
          <th>Model</th>
          <th className="col-cost">Monthly cost</th>
        </tr>
      </thead>
      <tbody>
        {results.map((item, i) => (
          <tr key={`${item.provider}-${item.model}`}>
            <td>
              <span className={`rank-dot rank-${i + 1}`}>{i + 1}</span>
            </td>
            <td>{item.provider}</td>
            <td>{item.model}</td>
            <td className="col-cost">${item.monthly_cost}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default PriceTable;
