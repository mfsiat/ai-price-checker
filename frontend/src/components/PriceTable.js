import React from "react";

const PriceTable = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <table border="1" cellPadding="10" style={{ marginTop: "20px", width: "100%" }}>
      <thead>
        <tr>
          <th>Provider</th>
          <th>Model</th>
          <th>Monthly Cost ($)</th>
        </tr>
      </thead>
      <tbody>
        {results.map((item) => (
          <tr key={item.provider}>
            <td>{item.provider}</td>
            <td>{item.model}</td>
            <td>{item.monthly_cost}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default PriceTable;
