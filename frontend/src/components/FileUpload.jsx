import React, { useState } from 'react'
import axios from 'axios'
import './FileUpload.css'

function FileUpload({ onUpload }) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const fileExt = file.name.split('.').pop().toLowerCase()
    if (!['csv', 'xlsx', 'xls'].includes(fileExt)) {
      setMessage('Please upload a CSV or Excel file')
      return
    }

    setUploading(true)
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(
        'http://localhost:8000/api/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setMessage(`✅ ${response.data.filename} uploaded successfully!`)
      if (onUpload) {
        onUpload()
      }
      
      // Clear file input
      e.target.value = ''
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="file-upload">
      <h3>Upload Dataset</h3>
      <div className="upload-area">
        <input
          type="file"
          id="file-input"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-input" className="upload-button">
          {uploading ? 'Uploading...' : '📁 Choose File'}
        </label>
        {message && <p className="upload-message">{message}</p>}
      </div>
    </div>
  )
}

export default FileUpload

