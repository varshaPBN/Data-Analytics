import React from 'react'
import './DatasetSelector.css'

function DatasetSelector({ datasets, selectedDataset, onSelect }) {
  if (datasets.length === 0) {
    return (
      <div className="dataset-selector">
        <h3>Datasets</h3>
        <p className="no-datasets">No datasets uploaded yet</p>
      </div>
    )
  }

  return (
    <div className="dataset-selector">
      <h3>Select Dataset</h3>
      <div className="dataset-list">
        {datasets.map((dataset) => (
          <div
            key={dataset.id}
            className={`dataset-item ${selectedDataset === dataset.id ? 'active' : ''}`}
            onClick={() => onSelect(dataset.id)}
          >
            <div className="dataset-name">{dataset.filename}</div>
            <div className="dataset-info">
              {dataset.row_count.toLocaleString()} rows
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DatasetSelector

