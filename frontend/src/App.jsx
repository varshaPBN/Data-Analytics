import React, { useState, useEffect } from 'react'
import FileUpload from './components/FileUpload'
import ChatInterface from './components/ChatInterface'
import DatasetSelector from './components/DatasetSelector'
import './App.css'

function App() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchDatasets()
  }, [])

  const fetchDatasets = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/datasets')
      const data = await response.json()
      setDatasets(data.datasets || [])
      if (data.datasets && data.datasets.length > 0 && !selectedDataset) {
        setSelectedDataset(data.datasets[0].id)
      }
    } catch (error) {
      console.error('Error fetching datasets:', error)
    }
  }

  const handleFileUpload = async () => {
    await fetchDatasets()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📊 Data Analytics Agent</h1>
        <p>Ask questions about your data in plain English</p>
      </header>

      <main className="app-main">
        <div className="sidebar">
          <FileUpload onUpload={handleFileUpload} />
          <DatasetSelector
            datasets={datasets}
            selectedDataset={selectedDataset}
            onSelect={setSelectedDataset}
          />
        </div>

        <div className="main-content">
          {selectedDataset ? (
            <ChatInterface datasetId={selectedDataset} />
          ) : (
            <div className="welcome-message">
              <h2>Welcome!</h2>
              <p>Upload a CSV or Excel file to get started.</p>
              
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App

