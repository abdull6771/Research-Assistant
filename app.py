import streamlit as st
from research_agent import ResearchAgent
import time
import json
from datetime import datetime
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput>div>div>input {
        font-size: 1.2rem;
    }
    .stButton>button {
        width: 100%;
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
    }
    .research-output {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .history-item {
        border: 1px solid #e0e0e0;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'research_agent' not in st.session_state:
    st.session_state.research_agent = ResearchAgent()
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

# Sidebar for history and export
with st.sidebar:
    st.title("Research History")
    
    # Display research history
    if st.session_state.research_history:
        for idx, history_item in enumerate(st.session_state.research_history):
            with st.container():
                st.markdown(f"""
                    <div class="history-item" onclick="document.getElementById('load-{idx}').click()">
                        <h4>{history_item['topic']}</h4>
                        <p>{history_item['timestamp']}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Load", key=f"load-{idx}", type="secondary"):
                    st.session_state.research_results = history_item['results']
                    st.rerun()
    
    st.markdown("---")
    
    # Export options
    if st.session_state.research_results:
        st.subheader("Export Options")
        export_format = st.selectbox(
            "Select format",
            ["Markdown", "JSON", "CSV"]
        )
        
        if st.button("Export Results"):
            if export_format == "Markdown":
                markdown_content = f"""# Research Results: {st.session_state.research_results['research_topic']}

## Research Plan
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(st.session_state.research_results['next_steps'])])}

## Key Findings
{chr(10).join([f"- {finding}" for finding in st.session_state.research_results['findings']])}

## Analysis and Insights
{chr(10).join([msg['content'] for msg in st.session_state.research_results['messages'] if msg['role'] == 'assistant'])}
"""
                st.download_button(
                    "Download Markdown",
                    markdown_content,
                    file_name="research_results.md",
                    mime="text/markdown"
                )
            elif export_format == "JSON":
                st.download_button(
                    "Download JSON",
                    json.dumps(st.session_state.research_results, indent=2),
                    file_name="research_results.json",
                    mime="application/json"
                )
            elif export_format == "CSV":
                # Convert findings to DataFrame
                df = pd.DataFrame({
                    'Step': range(1, len(st.session_state.research_results['findings']) + 1),
                    'Finding': st.session_state.research_results['findings']
                })
                st.download_button(
                    "Download CSV",
                    df.to_csv(index=False),
                    file_name="research_results.csv",
                    mime="text/csv"
                )

# Main content
st.title("🔍 AI Research Assistant")
st.markdown("""
    Welcome to the AI Research Assistant! This tool helps you conduct thorough research on any topic.
    Simply enter your research topic below, and the assistant will help you gather and analyze information.
""")

# Research input
research_topic = st.text_input(
    "Enter your research topic or question:",
    placeholder="e.g., Impact of artificial intelligence on healthcare",
    key="research_input"
)

# Process button
if st.button("Start Research", type="primary"):
    if research_topic:
        st.session_state.is_processing = True
        st.session_state.research_results = None
        
        with st.spinner("Conducting research... This may take a few moments."):
            try:
                results = st.session_state.research_agent.process_research_request(research_topic)
                st.session_state.research_results = results
                
                # Add to history
                st.session_state.research_history.append({
                    'topic': research_topic,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'results': results
                })
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                st.session_state.is_processing = False

# Display results
if st.session_state.research_results:
    st.markdown("## Research Results")
    
    # Display research plan
    st.markdown("### Research Plan")
    for i, step in enumerate(st.session_state.research_results["next_steps"], 1):
        st.markdown(f"{i}. {step}")
    
    # Display findings with visualization
    st.markdown("### Key Findings")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Text View", "Visual Analysis"])
    
    with tab1:
        for finding in st.session_state.research_results["findings"]:
            st.markdown(f"""
                <div class="research-output">
                    {finding}
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Create a simple visualization of findings
        findings_df = pd.DataFrame({
            'Finding': range(1, len(st.session_state.research_results["findings"]) + 1),
            'Length': [len(f) for f in st.session_state.research_results["findings"]]
        })
        fig = px.bar(findings_df, x='Finding', y='Length', 
                    title='Finding Length Distribution',
                    labels={'Finding': 'Finding Number', 'Length': 'Text Length'})
        st.plotly_chart(fig)
    
    # Display analysis
    st.markdown("### Analysis and Insights")
    for message in st.session_state.research_results["messages"]:
        if message["role"] == "assistant":
            st.markdown(f"""
                <div class="research-output">
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Built by Abdullahi Ahmad  using LangGraph and Streamlit</p>
    </div>
""", unsafe_allow_html=True) 