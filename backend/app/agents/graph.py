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
    response = llm.invoke(prompt)
    sql = response.content.strip()
    
    # Logic to generate SQL based on keywords (FALLBACK/OVERRIDE if LLM fails or for specific cases)
    # For now, we trust the LLM mostly, but can keep fallback if empty or error.
    if not sql or "SELECT" not in sql.upper():
         query_lower = query.lower()
    
    is_count = "count" in query_lower or "how many" in query_lower
    is_list = "list" in query_lower or ("show" in query_lower and "all" in query_lower)
    is_sales = "sales" in query_lower or "revenue" in query_lower

    if is_count and "brand" in query_lower:
        sql = "SELECT COUNT(DISTINCT PRODUCT_BRAND) as BRAND_COUNT FROM DIM_SOURCE_PRODUCT"
    elif is_list and "brand" in query_lower:
         sql = "SELECT DISTINCT PRODUCT_BRAND FROM DIM_SOURCE_PRODUCT"
    elif is_sales:
        if "allegra" in query_lower:
             sql = """
            SELECT 
                p.PRODUCT_BRAND, 
                SUM(s.VALUE_LC) as TOTAL_SALES
            FROM FCT_SALES_NATIONAL_MTH s
            JOIN DIM_SOURCE_PRODUCT p ON s.SOURCE_PRODUCT_ID = p.SOURCE_PRODUCT_ID
            WHERE p.PRODUCT_BRAND = 'Allegra'
            GROUP BY p.PRODUCT_BRAND
            """
        elif "doliprane" in query_lower:
             sql = """
            SELECT 
                p.PRODUCT_BRAND, 
                SUM(s.VALUE_LC) as TOTAL_SALES
            FROM FCT_SALES_NATIONAL_MTH s
            JOIN DIM_SOURCE_PRODUCT p ON s.SOURCE_PRODUCT_ID = p.SOURCE_PRODUCT_ID
            WHERE p.PRODUCT_BRAND = 'Doliprane'
            GROUP BY p.PRODUCT_BRAND
            """
        elif "dulcoflex" in query_lower:
             sql = """
            SELECT 
                p.PRODUCT_BRAND, 
                SUM(s.VALUE_LC) as TOTAL_SALES
            FROM FCT_SALES_NATIONAL_MTH s
            JOIN DIM_SOURCE_PRODUCT p ON s.SOURCE_PRODUCT_ID = p.SOURCE_PRODUCT_ID
            WHERE p.PRODUCT_BRAND = 'Dulcoflex'
            GROUP BY p.PRODUCT_BRAND
            """
        else:
            # Default to all brands
            sql = """
            SELECT 
                p.PRODUCT_BRAND, 
                SUM(s.VALUE_LC) as TOTAL_SALES
            FROM FCT_SALES_NATIONAL_MTH s
            JOIN DIM_SOURCE_PRODUCT p ON s.SOURCE_PRODUCT_ID = p.SOURCE_PRODUCT_ID
            GROUP BY p.PRODUCT_BRAND
            ORDER BY TOTAL_SALES DESC
            """
    else:
        # Fallback
        sql = "SELECT COUNT(*) as TOTAL_ROWS FROM DIM_SOURCE_PRODUCT"
    
    return {"sql_query": sql, "messages": [SystemMessage(content=f"SQL Generated: {sql}")]}

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
    
    # Check if results look like chartable data (e.g. Sales)
    if results and isinstance(results, list) and len(results) > 0 and 'TOTAL_SALES' in results[0]:
        chart_config = {
            "type": "bar",
            "xKey": "PRODUCT_BRAND",
            "yKey": "TOTAL_SALES",
            "title": "Sales by Brand"
        }
    else:
        chart_config = None
    
    return {"chart_config": chart_config, "messages": [SystemMessage(content="Chart Configured")]}

def data_analyst_node(state: AgentState):
    """
    Node 4: Data Analyst
    Generates insights.
    """
    print("--- Data Analyst Node ---")
    results = state['sql_results']
    query = state['user_query'].lower()
    
    is_count = "count" in query or "how many" in query
    is_list = "list" in query or ("show" in query and "all" in query)
    
    if is_count:
        count_val = list(results[0].values())[0] if results else 0
        analysis = f"There are **{count_val}** brands currently in the database."
    elif is_list:
        brands = [list(r.values())[0] for r in results]
        brands_str = ", ".join(str(b) for b in brands)
        analysis = f"The brands in the database are: **{brands_str}**."
    elif results and 'TOTAL_SALES' in results[0]:
        # Simple analysis for sales
        top_brand = results[0]['PRODUCT_BRAND']
        top_val = results[0]['TOTAL_SALES']
        analysis = f"Sales are led by **{top_brand}** with **{top_val}**."
    else:
        analysis = f"I found {len(results)} records matching your query."
    
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
