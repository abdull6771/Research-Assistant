# AI Research Assistant

A professional research assistant powered by LangGraph and Streamlit that helps users conduct research, analyze information, and generate insights.

## Features

- Interactive research workflow using LangGraph
- User-friendly Streamlit interface
- Intelligent research planning and execution
- Comprehensive information gathering and analysis
- Professional report generation

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

To start the research assistant, run:
```bash
streamlit run app.py
```

## Usage

1. Enter your research topic or question in the input field
2. The assistant will help you:
   - Break down the research into manageable steps
   - Gather relevant information
   - Analyze the collected data
   - Generate insights and conclusions

## Architecture

The application uses:
- LangGraph for orchestrating the research workflow
- Streamlit for the user interface
- OpenAI's language models for natural language processing
- Pydantic for data validation and settings management

## License

MIT License 