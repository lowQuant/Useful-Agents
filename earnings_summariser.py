from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
import os
import html2text
from typing import Dict, Optional as OptionalType
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
from dotenv import load_dotenv
from edgar import Company, set_identity
from pydantic import Field, ConfigDict

# Load environment variables
load_dotenv()
set_identity("lange.johannes@outlook.com")
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4'# 'gpt-3.5-turbo'

class GetEdgarFiling(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "Earnings Report Extraction Tool"
    description: str = "Extracts key financial metrics from earnings report"
    index: OptionalType[VectorStoreIndex] = Field(default=None, exclude=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.index = None
        
    def _create_index(self, text: str):
        documents = [Document(text=text)]
        parser = SimpleNodeParser.from_defaults()
        nodes = parser.get_nodes_from_documents(documents)
        self.index = VectorStoreIndex(nodes)
    
    def _extract_metrics(self) -> Dict[str, OptionalType[str]]:
        metrics = {}
        
        # Targeted queries for specific metrics
        queries = {
            'revenue': "What is the current quarter revenue and its year-over-year growth rate? Return only the number and growth rate.",
            'operating_income': "What is the operating income and its year-over-year growth rate? Return only the number and growth rate.",
            'eps': "What is the EPS (earnings per share) and its year-over-year growth rate? Return only the number and growth rate.",
            'guidance': "What is the company's specific forward guidance for next quarter/year? Return only the numbers if provided.",
            'drivers': "What were the main drivers of the results? Focus on segments, products, or market trends that significantly impacted performance. List only 3-5 key points if available."
        }
        
        query_engine = self.index.as_query_engine(
            response_mode="compact",
            similarity_top_k=3
        )
            
        def format_growth(response: str) -> tuple:
            try:
                # Extract number and growth rate using simple parsing
                parts = response.lower().replace('%', '').split()
                number = next(p for p in parts if p.replace('.', '').replace(',', '').isdigit() or '$' in p)
                growth = next(float(p) for p in parts if p.replace('.', '').replace('-', '').isdigit())
                
                # Format growth with correct sign
                growth_str = f"+{growth}%" if growth > 0 else f"{growth}%"
                return number, growth_str
            except:
                return response, "N/A"

        for metric, query in queries.items():
            response = query_engine.query(query).response
            if metric != 'guidance':
                number, growth = format_growth(response)
                metrics[metric] = f"{number} {growth} YoY"
            else:
                metrics[metric] = response
            
        return metrics

    def _run(self, ticker: str, form: str = "8-K") -> str:
        try:
            company = Company(ticker)
            filings = company.get_filings(form=form)
            
            if not filings:
                return f"No {form} filings found for {ticker}"
            
            exhibits = filings[0].attachments.exhibits
            results = exhibits.query("document_type in ['EX-99.1', 'EX-99', 'EX-99.01']")
            if not results:
                return f"No earnings exhibits found in latest {form} filing for {ticker}"
            
            latest_filing = next(iter(results))
            html_content = latest_filing.download()
            text_content = html2text.HTML2Text().handle(html_content)
            
            # Create vector index from the document
            self._create_index(text_content)
            
            # Extract specific metrics
            metrics = self._extract_metrics()
            
            # Format output in a concise way
            output = (
            f"Revenue: {metrics['revenue']}\n"
            f"Operating Income: {metrics['operating_income']}\n"
            f"EPS: {metrics['eps']}\n\n"
            f"Guidance: {metrics['guidance']}"
            )

            if metrics['drivers'] and metrics['drivers'].lower() not in ['none', 'n/a', 'not available']:
                output += "Key Drivers:\n" + metrics['drivers']
            return output
            
        except Exception as e:
            return f"Error processing {ticker}: {str(e)}"

# Initialize the tool
edgar_filing_tool = GetEdgarFiling()

# Create the analyst agent
earnings_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Extract key financial metrics from earnings reports",
    backstory="You extract and verify key financial metrics from earnings reports, focusing only on revenue, operating income, EPS, and guidance.",
    tools=[edgar_filing_tool],
    allow_delegation=False,
    verbose=True
)

earnings_analysis_task = Task(
    description=(
        "Extract these specific metrics from the {ticker} earnings report using 8-K filing:\n"
        "1. Revenue + YoY growth\n"
        "2. Operating Income + YoY growth\n"
        "3. EPS + YoY growth\n"
        "4. Forward guidance (if provided)\n"
        "5. Key business drivers (3-5 points on segments, products, or market trends)\n"
        "Present the numbers first, followed by key drivers if available."
        "Note: Always use form='8-K' as this contains the latest earnings information."
    ),
    expected_output=(
        "Revenue: [number] [growth] YoY\n"
        "Operating Income: [number] [growth] YoY\n"
        "EPS: [number] [growth] YoY\n"
        "Guidance: [specific numbers if provided, or 'Not provided']\n\n"
        "Key Drivers: [3-5 bullet points if available]"
    ),
    tools=[edgar_filing_tool],
    agent=earnings_analyst
)

# Create the crew
crew = Crew(
    agents=[earnings_analyst],
    tasks=[earnings_analysis_task],
    verbose=True
)

if __name__ == "__main__":
    ticker = input("Enter a ticker symbol: ")
    inputs = {"ticker": ticker}
    result = crew.kickoff(inputs=inputs)
    print("\n{}'s Results Summary:".format(ticker))
    print(result)