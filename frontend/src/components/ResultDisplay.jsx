import React from 'react'
import './ResultDisplay.css'

function ResultDisplay({ result }) {
  if (!result) {
    return <div>No result to display</div>
  }

  const { type, data, metadata } = result

  switch (type) {
    case 'table':
      return (
        <div className="result-table">
          <TableDisplay data={data} metadata={metadata} />
        </div>
      )

    case 'value':
      return (
        <div className="result-value">
          <div className="value-display">{data}</div>
          {metadata.notes && <p className="value-notes">{metadata.notes}</p>}
        </div>
      )

    case 'plot':
      return (
        <div className="result-plot">
          <img
            src={`http://localhost:8000${data}`}
            alt="Analytics Chart"
            className="plot-image"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><text>Image not found</text></svg>'
            }}
          />
          {metadata.notes && <p className="plot-notes">{metadata.notes}</p>}
        </div>
      )

    case 'text':
      return (
        <div className="result-text">
          <p>{data}</p>
          {metadata.notes && <p className="text-notes">{metadata.notes}</p>}
        </div>
      )

    case 'error':
      return (
        <div className="result-error">
          <p>❌ {data}</p>
          {metadata.notes && <p className="error-notes">{metadata.notes}</p>}
        </div>
      )

    default:
      return <div>Unknown result type: {type}</div>
  }
}

function TableDisplay({ data, metadata }) {
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return <p>No data to display</p>
  }

  // Handle array of objects (most common case)
  if (Array.isArray(data) && data.length > 0) {
    const columns = metadata.columns || Object.keys(data[0])
    
    return (
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {columns.map((col, colIdx) => (
                  <td key={colIdx}>{row[col] ?? 'N/A'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {metadata.row_count && (
          <p className="table-info">
            Showing {data.length} of {metadata.row_count} rows
          </p>
        )}
      </div>
    )
  }

  // Handle dictionary/object
  if (typeof data === 'object' && !Array.isArray(data)) {
    return (
      <div className="table-container">
        <table className="data-table">
          <tbody>
            {Object.entries(data).map(([key, value]) => (
              <tr key={key}>
                <th>{key}</th>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return <p>{JSON.stringify(data)}</p>
}

export default ResultDisplay

