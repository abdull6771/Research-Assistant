from typing import Annotated, Dict, List, Tuple, TypedDict
from langgraph.graph import Graph, StateGraph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class ResearchState(TypedDict):
    """State for the research workflow."""
    messages: List[Dict[str, str]]
    research_topic: str
    current_step: str
    findings: List[str]
    next_steps: List[str]

class ResearchAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> Graph:
        """Create the research workflow using LangGraph."""
        
        def plan_research(state: ResearchState) -> ResearchState:
            """Plan the research approach."""
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a research planning expert. Break down the research topic into clear steps."),
                ("human", "Research topic: {research_topic}\nPlease create a detailed research plan.")
            ])
            
            response = self.llm.invoke(prompt.format_messages(
                research_topic=state["research_topic"]
            ))
            
            state["next_steps"] = [step.strip() for step in response.content.split("\n") if step.strip()]
            state["current_step"] = "planning"
            return state

        def gather_information(state: ResearchState) -> ResearchState:
            """Gather information for the current research step."""
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a research assistant. Gather relevant information for the current research step."),
                ("human", "Research topic: {research_topic}\nCurrent step: {current_step}\nPlease gather relevant information.")
            ])
            
            response = self.llm.invoke(prompt.format_messages(
                research_topic=state["research_topic"],
                current_step=state["current_step"]
            ))
            
            state["findings"].append(response.content)
            return state

        def analyze_findings(state: ResearchState) -> ResearchState:
            """Analyze the gathered information."""
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a research analyst. Analyze the gathered information and provide insights."),
                ("human", "Research topic: {research_topic}\nFindings: {findings}\nPlease analyze and provide insights.")
            ])
            
            response = self.llm.invoke(prompt.format_messages(
                research_topic=state["research_topic"],
                findings="\n".join(state["findings"])
            ))
            
            state["messages"].append({"role": "assistant", "content": response.content})
            return state

        # Create the workflow graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("plan_research", plan_research)
        workflow.add_node("gather_information", gather_information)
        workflow.add_node("analyze_findings", analyze_findings)
        
        # Add edges
        workflow.add_edge("plan_research", "gather_information")
        workflow.add_edge("gather_information", "analyze_findings")
        
        # Set entry point
        workflow.set_entry_point("plan_research")
        
        return workflow.compile()

    def process_research_request(self, topic: str) -> Dict:
        """Process a research request."""
        initial_state = {
            "messages": [],
            "research_topic": topic,
            "current_step": "",
            "findings": [],
            "next_steps": []
        }
        
        final_state = self.workflow.invoke(initial_state)
        return final_state 