from langchain_google_genai import GoogleGenerativeAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from database import init_database,execute_query
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_GENERATIVE_AI_API_KEY = os.getenv('GEMINI_API_KEY')
llm = GoogleGenerativeAI(model = "gemini-2.0-flash",api_key=GOOGLE_GENERATIVE_AI_API_KEY,temperature=0.7)

db_connection = init_database()

def get_sql_chain():
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking questions about the sales and inventory database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.

    <SCHEMA>
    - customers (customer_id, name, email, phone, address)
    - products (product_id, name, description, price, category)
    - orders (order_id, customer_id, order_date, total_amount)
    - order_details (order_detail_id, order_id, product_id, quantity, unit_price)
    - inventory (inventory_id, product_id, quantity, warehouse_id)
    - warehouses (warehouse_id, name, location)
    - suppliers (supplier_id, name, contact, email)
    - stock_transactions (transaction_id, product_id, quantity, transaction_type, transaction_date)
    </SCHEMA>

    Conversation History: {chat_history}

    IMPORTANT: Return ONLY the SQL query. Do not include any markdown formatting, backticks, or any other text.
    Just return the pure SQL query that can be directly executed.

    Question: {question}
    SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)

    def get_schema(_):
        return ""
    
    return RunnablePassthrough.assign(Schema=get_schema)|prompt|llm|StrOutputParser()

def get_response(user_query,chat_history):
    sql_chain = get_sql_chain()
    template = """
    You are a data analyst at a company. Based on the table schema below, question, SQL query, and SQL response, write a natural language response.
    <SCHEMA>
    - customers (customer_id, name, email, phone, address)
    - products (product_id, name, description, price, category)
    - orders (order_id, customer_id, order_date, total_amount)
    - order_details (order_detail_id, order_id, product_id, quantity, unit_price)
    - inventory (inventory_id, product_id, quantity, warehouse_id)
    - warehouses (warehouse_id, name, location)
    - suppliers (supplier_id, name, contact, email)
    - stock_transactions (transaction_id, product_id, quantity, transaction_type, transaction_date)
    </SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            response=lambda vars: execute_query(db_connection, vars["query"])
        )
        | prompt
        | llm
        | StrOutputParser()
    ) 

    return chain.invoke({"question": user_query, "chat_history": chat_history})
