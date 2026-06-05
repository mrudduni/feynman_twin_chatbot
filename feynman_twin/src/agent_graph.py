"""LangGraph Multi-Step Reasoning Agent for Feynman Twin"""
import logging
from typing import Annotated, Dict, List, Tuple, TypedDict, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from config import PRIMARY_MODEL, GEMINI_API_KEY
from personality import TeachingStyler, PersonalityAnalyzer

logger = logging.getLogger(__name__)

class FeynmanAgentState(TypedDict):
    messages: Annotated[list, add_messages]  # LangGraph message history
    query: str                                # original user question
    query_type: str                           # "simple" | "complex" | "multi_part"
    refined_query: Optional[str]              # query modified during refinement
    retrieved_docs: List[dict]                # RAG results
    relevance_score: float                   # 0-1 quality of retrieval
    retrieval_attempts: int                  # loop counter (max 2)
    system_prompt: str                       # Feynman personality prompt
    final_response: str                      # finished response text
    metadata: dict                           # personality_score, model_used, etc.

class FeynmanAgentGraph:
    """LangGraph agent for multi-step reasoning."""
    
    def __init__(self, rag_system, memory_manager):
        self.rag_system = rag_system
        self.memory_manager = memory_manager
        self.graph = self._build_graph()
        
    def _build_graph(self):
        builder = StateGraph(FeynmanAgentState)
        
        # Add nodes
        builder.add_node("classify", self.classify_query_node)
        builder.add_node("retrieve", self.retrieve_node)
        builder.add_node("evaluate", self.evaluate_relevance_node)
        builder.add_node("refine_query", self.refine_query_node)
        builder.add_node("generate_response", self.generate_response_node)
        builder.add_node("direct_response", self.direct_response_node)
        builder.add_node("enhance_personality", self.enhance_personality_node)
        
        # Add edges
        builder.add_edge(START, "classify")
        builder.add_conditional_edges(
            "classify",
            self.route_after_classify,
            {
                "direct_response": "direct_response",
                "retrieve": "retrieve"
            }
        )
        builder.add_edge("retrieve", "evaluate")
        builder.add_conditional_edges(
            "evaluate",
            self.route_after_evaluate,
            {
                "generate_response": "generate_response",
                "refine_query": "refine_query"
            }
        )
        builder.add_edge("refine_query", "retrieve")
        builder.add_edge("generate_response", "enhance_personality")
        builder.add_edge("direct_response", "enhance_personality")
        builder.add_edge("enhance_personality", END)
        
        return builder.compile()
        
    def classify_query_node(self, state: FeynmanAgentState) -> dict:
        query = state["query"]
        prompt = f"""You are a query classifier. Your job is to classify the user's input.
        
User input: "{query}"

Classify the input into one of three categories:
- "simple": A general greeting, casual remark, follow-up conversation, or general question that doesn't need specific physics lectures/documents.
- "complex": A physics concept, explanation, formula, or history query that benefits from specific reference materials or documents.
- "multi_part": A complex question containing multiple separate questions or parts.

Response must be exactly one of: "simple", "complex", "multi_part". Do not include any other text."""
        try:
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(prompt)
            query_type = res.content.strip().lower()
            if "simple" in query_type:
                query_type = "simple"
            elif "multi" in query_type:
                query_type = "multi_part"
            else:
                query_type = "complex"
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            query_type = "complex"
            
        return {"query_type": query_type}
        
    def route_after_classify(self, state: FeynmanAgentState) -> str:
        if state.get("query_type") == "simple":
            return "direct_response"
        return "retrieve"
        
    def retrieve_node(self, state: FeynmanAgentState) -> dict:
        search_query = state.get("refined_query") or state["query"]
        attempts = state.get("retrieval_attempts", 0) + 1
        
        retrieved_docs = []
        if self.rag_system and getattr(self.rag_system, "collection", None):
            retrieved_docs = self.rag_system.retrieve(search_query, top_k=5)
            
        return {
            "retrieved_docs": retrieved_docs,
            "retrieval_attempts": attempts
        }
        
    def evaluate_relevance_node(self, state: FeynmanAgentState) -> dict:
        query = state["query"]
        docs = state.get("retrieved_docs", [])
        if not docs:
            return {"relevance_score": 0.0}
            
        context = "\n\n".join([d["text"] for d in docs])
        prompt = f"""You are a relevance evaluator. Assess if the retrieved context is sufficient to answer the user's question.
        
User Question: {query}

Retrieved Context:
{context}

Provide a relevance score between 0.0 and 1.0 (where 0.0 means completely irrelevant/insufficient, and 1.0 means perfectly sufficient to provide a complete, detailed answer).
Your output must be just a single float number between 0.0 and 1.0. Do not write anything else."""
        try:
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(prompt)
            # Sometimes LLM adds quotes or extra text
            cleaned_score = res.content.strip().replace("`", "").replace("score:", "").strip()
            score = float(cleaned_score)
        except Exception as e:
            logger.error(f"Error evaluating relevance: {e}")
            score = 0.5
            
        return {"relevance_score": score}
        
    def route_after_evaluate(self, state: FeynmanAgentState) -> str:
        score = state.get("relevance_score", 0.0)
        attempts = state.get("retrieval_attempts", 0)
        if score >= 0.5 or attempts >= 2:
            return "generate_response"
        return "refine_query"
        
    def refine_query_node(self, state: FeynmanAgentState) -> dict:
        query = state["query"]
        docs = state.get("retrieved_docs", [])
        context = "\n\n".join([d["text"] for d in docs])
        prompt = f"""The previous search query did not retrieve sufficient information to answer the user's question.
Original Question: {query}
Previous Context Retrieved: {context}

Please rewrite the search query to retrieve more relevant, specific information from a physics textbook/knowledge base. The rewritten query should target the missing information.
Output only the rewritten search query. Do not include any explanations or quotes."""
        try:
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(prompt)
            refined = res.content.strip().strip('"').strip("'")
        except Exception as e:
            logger.error(f"Error refining query: {e}")
            refined = query
            
        return {"refined_query": refined}
        
    def generate_response_node(self, state: FeynmanAgentState) -> dict:
        query = state["query"]
        docs = state.get("retrieved_docs", [])
        system_prompt = state.get("system_prompt", "")
        
        context = "\n\n".join([
            f"Source: {doc['metadata'].get('source', 'Unknown')}\n"
            f"Title: {doc['metadata'].get('title', 'Unknown')}\n"
            f"Content: {doc['text']}"
            for doc in docs
        ])
        
        full_prompt = f"""You are Richard Feynman, a brilliant physicist and educator.
            
{system_prompt}

Here is relevant knowledge from Feynman's works and related materials:

{context}

User question: {query}

Please respond in Feynman's characteristic style - clear, thoughtful, often using analogies and everyday examples. 
Be willing to admit uncertainty and maintain his emphasis on understanding over memorization."""
        try:
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(full_prompt)
            response = res.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response = "I encountered an error generating response."
            
        return {"final_response": response}
        
    def direct_response_node(self, state: FeynmanAgentState) -> dict:
        query = state["query"]
        system_prompt = state.get("system_prompt", "")
        
        full_prompt = f"""You are Richard Feynman, a brilliant physicist and educator.
            
{system_prompt}

User question: {query}

Respond directly in Feynman's characteristic conversational style."""
        try:
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(full_prompt)
            response = res.content
        except Exception as e:
            logger.error(f"Error in direct response node: {e}")
            response = "I encountered an error generating direct response."
            
        return {"final_response": response}
        
    def enhance_personality_node(self, state: FeynmanAgentState) -> dict:
        response = state.get("final_response", "")
        enhanced = TeachingStyler.add_personal_touch(response)
        enhanced = TeachingStyler.make_socratic(enhanced)
        
        score = PersonalityAnalyzer.score_feynman_alignment(enhanced)
        metadata = state.get("metadata", {})
        metadata.update({
            "personality_score": score,
            "model_used": PRIMARY_MODEL,
            "retrieved_docs": len(state.get("retrieved_docs", []))
        })
        
        return {
            "final_response": enhanced,
            "metadata": metadata
        }

def run_agent(query: str, system_prompt: str, rag_system, memory_manager, chat_history: list = None) -> Tuple[str, dict]:
    """Compile and run the Feynman agent graph."""
    graph_runner = FeynmanAgentGraph(rag_system, memory_manager)
    
    messages = []
    if chat_history:
        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role in ["assistant", "bot"]:
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))
                
    initial_state = {
        "messages": messages,
        "query": query,
        "query_type": "simple",
        "refined_query": None,
        "retrieved_docs": [],
        "relevance_score": 0.0,
        "retrieval_attempts": 0,
        "system_prompt": system_prompt,
        "final_response": "",
        "metadata": {}
    }
    
    result = graph_runner.graph.invoke(initial_state)
    return result["final_response"], result["metadata"]
