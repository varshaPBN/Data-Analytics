# Data Analytics Agent

A natural language interface for data analytics that allows business users to ask questions about their data in plain English, without writing code.

## Features

- 📊 **Natural Language Queries**: Ask questions like "What were our top 5 products last month?" in plain English
- 🔒 **Secure Execution**: Sandboxed code execution with strict safety validations
- 📈 **Visualizations**: Automatic chart generation using Matplotlib
- 🗄️ **Multiple Formats**: Support for CSV and Excel files
- 💬 **Interactive Chat**: Clean, modern React interface for querying your data
- 🤖 **AI-Powered**: Uses GPT-4 to interpret queries and generate Pandas code

## Architecture

- **Frontend**: React + Vite
- **Backend**: FastAPI (Python)
- **Database**: SQLite for dataset storage
- **AI Agent**: LangChain + GPT-4 for query interpretation
- **Analytics**: Pandas + NumPy + Matplotlib
- **Security**: AST-based code validation and sandboxed execution

## Prerequisites

- Python 3.12 (3.9+ supported)
- Node.js 18+
- OpenAI API key

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd data_analyisis_agent
```

### 2. Initial Setup

```bash
# Run setup script to create necessary directories
python setup.py
```

### 3. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example if it exists, or create manually)
# Add your OpenAI API key:
# OPENAI_API_KEY=your_api_key_here
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend

```bash
# From project root (with virtual environment activated)
python run_backend.py
```

Or using uvicorn directly:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Start the Frontend

```bash
# From project root
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Quick Start

1. **Set up environment**:
   ```bash
   python setup.py
   # Create .env file with your OPENAI_API_KEY
   ```

2. **Install dependencies**:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

3. **Start services**:
   ```bash
   # Terminal 1 - Backend
   python run_backend.py
   
   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

4. **Test with sample data**:
   - Open `http://localhost:3000`
   - Upload `sample_data/sample_sales.csv`
   - Try: "What are the top 5 products by sales?"

## Usage

1. **Upload a Dataset**: Click "Choose File" and upload a CSV or Excel file
2. **Select Dataset**: Choose the dataset you want to analyze from the sidebar
3. **Ask Questions**: Type your question in natural language, for example:
   - "What are the top 5 products by sales?"
   - "Show me monthly revenue trends"
   - "Which region had the lowest performance?"
   - "What is the average order value?"
   - "Group sales by category and show totals"

4. **View Results**: Results are displayed as:
   - **Tables**: For tabular data
   - **Values**: For scalar results
   - **Plots**: For visualizations
   - **Text**: For descriptive answers

## Example Queries

Try these queries with the sample data (`sample_data/sample_sales.csv`):

- "What are the top 5 products by sales?"
- "Show me total sales by region"
- "Which region had the highest sales?"
- "Calculate the average price of products"
- "Show me a bar chart of sales by category"
- "What is the total quantity sold for each product?"
- "Which product category has the highest total sales?"
- "Show monthly sales trends"
- "What is the average sales per transaction?"

## Security Features

The system implements multiple security layers:

1. **Code Validation**: AST-based parsing to detect unsafe operations
2. **Import Restrictions**: Only allows pandas, numpy, matplotlib, math, datetime, json
3. **Function Blacklist**: Blocks dangerous functions (os.system, exec, eval, etc.)
4. **Sandboxed Execution**: Code runs in a restricted environment
5. **No File System Access**: Prevents reading/writing files outside temp directory
6. **No Network Calls**: Blocks all network operations

## API Endpoints

### `POST /api/upload`
Upload a CSV or Excel file

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "dataset_id": 1,
  "filename": "sales.csv",
  "message": "Dataset uploaded successfully"
}
```

### `POST /api/query`
Process a natural language query

**Request**:
```json
{
  "dataset_id": 1,
  "query": "What are the top 5 products by sales?"
}
```

**Response**:
```json
{
  "type": "table",
  "data": [...],
  "metadata": {
    "columns": ["product", "sales"],
    "row_count": 5,
    "notes": "Showing 5 rows"
  }
}
```

### `GET /api/datasets`
List all uploaded datasets

### `GET /api/datasets/{dataset_id}`
Get information about a specific dataset

## Project Structure

```
data_analyisis_agent/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLite operations
│   ├── agent.py             # LangChain agent
│   └── executor.py          # Secure code execution
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── DatasetSelector.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   └── ResultDisplay.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── .gitignore
└── README.md
```

## Limitations

- Maximum result size: 1000 rows (to prevent memory issues)
- Supported file formats: CSV, Excel (.xlsx, .xls)
- Plot format: PNG only
- Code execution timeout: Not yet implemented (recommended for production)

## Future Enhancements

- [ ] Add execution timeouts
- [ ] Support for SQL databases
- [ ] Export results to CSV/Excel
- [ ] Query history and saved queries
- [ ] Multi-user support with authentication
- [ ] Advanced visualization types
- [ ] Natural language explanations of results

## Troubleshooting

### Pandas Installation Error (Windows)

If you see "Failed to build 'pandas' when installing build dependencies":

**Quick Fix:**
```bash
python -m pip install --upgrade pip setuptools wheel
pip install pandas --only-binary :all:
pip install -r requirements.txt
```

**If that doesn't work:**
- Install Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- See `INSTALL_WINDOWS.md` for detailed Windows installation guide

### Backend won't start
- Check that Python 3.12 is installed (3.9+ supported)
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure OPENAI_API_KEY is set in .env file
- Make sure you're in a virtual environment

### Frontend won't start
- Check that Node.js 18+ is installed
- Run `npm install` in the frontend directory
- Check that port 3000 is not in use

### Queries not working
- Verify your OpenAI API key is valid
- Check browser console for errors
- Ensure backend is running on port 8000
- Check that dataset was uploaded successfully
- Check backend terminal for error messages

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

