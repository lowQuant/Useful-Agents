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

## Adding New Agents

Each agent in this repository follows these principles:
- Single responsibility
- Clear input/output interface
- Focused on automation of specific tasks
- Includes error handling and input validation

## Contributing

Feel free to contribute by:
1. Adding new purpose-built agents
2. Improving existing agents
3. Enhancing documentation
4. Reporting issues

## License

MIT License - feel free to use in your own projects.
