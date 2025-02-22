# Useful Agents

A collection of purpose-built AI agents to automate specific tasks using the CrewAI framework.

## Available Agents

### 1. Earnings Summarizer
📊 Extracts and analyzes earnings reports from SEC EDGAR filings, providing concise summaries of key financial metrics (Revenue, Operating Income, EPS) with YoY growth rates and business drivers.

## Requirements

- Python 3.8+
- OpenAI API key (set in `.env` file)
- Required packages:
  ```bash
  pip install crewai llama-index edgar html2text python-dotenv
  ```

## Usage

1. Clone the repository
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
3. Run the desired agent script:
   ```bash
   python earnings_summariser.py
   ```

## New Agents coming soon
