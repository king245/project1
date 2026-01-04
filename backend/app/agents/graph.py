from typing import TypedDict, List, Dict, Any, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from app.services.llm_factory import llm_factory
from app.services.snowflake_service import snowflake_service

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    resolved_entities: Dict[str, Any]
    sql_query: str
    sql_results: List[Dict[str, Any]]
    chart_config: Dict[str, Any]
    analysis: str
    final_response: Dict[str, Any]

# --- NODES ---

def initializer_node(state: AgentState):
    """
    Node 1: Initializer
    Uses RAG (mocked here) to resolve entities and extract user intent.
    """
    print("--- Initializer Node ---")
    query = state['user_query']
    llm = llm_factory.create_llm()
    
    # In a real app, we would query Pinecone here for entity resolution
    # prompt = f"Resolve entities in: {query}"
    # response = llm.invoke(prompt)
    
    # Mock behavior
    resolved_entities = {"intent": "sales_analysis", "entities": []}
    
    return {"resolved_entities": resolved_entities, "messages": [SystemMessage(content="Entities Resolved")]}

def sql_writer_node(state: AgentState):
    """
    Node 2: SQL Writer
    Transforms natural language into Snowflake SQL.
    """
    print("--- SQL Writer Node ---")
    query = state['user_query']
    schema = snowflake_service.get_schema_info()
    llm = llm_factory.create_llm()
    
    # Prompt would be complex with few-shot examples
    prompt = f"""
    You are a Snowflake SQL expert. Generate a SQL query for: "{query}"
    Using Schema:
    {schema}
    
    Return ONLY the SQL.
    """
    # response = llm.invoke(prompt)
    
    # Mock behavior: Simple query on dummy data
    # We'll just select from FCT_SALES_NATIONAL_MTH join DIM_SOURCE_PRODUCT
    # For now, let's return a valid query on our mock DB
    sql = """
    SELECT 
        p.PRODUCT_BRAND, 
        SUM(s.VALUE_LC) as TOTAL_SALES
    FROM FCT_SALES_NATIONAL_MTH s
    JOIN DIM_SOURCE_PRODUCT p ON s.SOURCE_PRODUCT_ID = p.SOURCE_PRODUCT_ID
    GROUP BY p.PRODUCT_BRAND
    """
    
    return {"sql_query": sql, "messages": [SystemMessage(content="SQL Generated")]}

def sql_executor_node(state: AgentState):
    """
    Extra Node: Executor
    Actually runs the SQL against Snowflake (Mock SQLite).
    """
    print("--- SQL Executor Node ---")
    sql = state['sql_query']
    try:
        results = snowflake_service.execute_query(sql)
    except Exception as e:
        results = [{"error": str(e)}]
        
    return {"sql_results": results, "messages": [SystemMessage(content=f"SQL Executed. Rows: {len(results)}")]}

def chart_recommender_node(state: AgentState):
    """
    Node 3: Chart Recommender
    Analyzes results to suggest visualization.
    """
    print("--- Chart Recommender Node ---")
    results = state['sql_results']
    # Logic to determine best chart type based on data shape
    
    chart_config = {
        "type": "bar",
        "xKey": "PRODUCT_BRAND",
        "yKey": "TOTAL_SALES",
        "title": "Sales by Brand"
    }
    
    return {"chart_config": chart_config, "messages": [SystemMessage(content="Chart Configured")]}

def data_analyst_node(state: AgentState):
    """
    Node 4: Data Analyst
    Generates insights.
    """
    print("--- Data Analyst Node ---")
    results = state['sql_results']
    llm = llm_factory.create_llm()
    
    prompt = f"Analyze these results: {results}"
    # response = llm.invoke(prompt)
    
    analysis = "Sales for Advil are robust, totaling 1000.0 in the last period."
    
    return {"analysis": analysis, "messages": [SystemMessage(content="Analysis Complete")]}

def merger_node(state: AgentState):
    """
    Node 5: Merger
    Consolidates everything.
    """
    print("--- Merger Node ---")
    response = {
        "query": state['user_query'],
        "sql": state['sql_query'],
        "data": state['sql_results'],
        "chart": state['chart_config'],
        "narrative": state['analysis']
    }
    return {"final_response": response, "messages": [SystemMessage(content="Workflow Finished")]}

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

workflow.add_node("initializer", initializer_node)
workflow.add_node("sql_writer", sql_writer_node)
workflow.add_node("sql_executor", sql_executor_node) # Added this to actually get data
workflow.add_node("chart_recommender", chart_recommender_node)
workflow.add_node("data_analyst", data_analyst_node)
workflow.add_node("merger", merger_node)

workflow.set_entry_point("initializer")

workflow.add_edge("initializer", "sql_writer")
workflow.add_edge("sql_writer", "sql_executor")
workflow.add_edge("sql_executor", "chart_recommender")
workflow.add_edge("chart_recommender", "data_analyst")
workflow.add_edge("data_analyst", "merger")
workflow.add_edge("merger", END)

# Compile
app_graph = workflow.compile()
