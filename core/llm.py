import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

deepseek_API_KEY = os.getenv("deepseek_API_KEY")
deepseek_API_BASE = os.getenv("deepseek_API_BASE")
LLM_MODEL = os.getenv("LLM_MODEL")

llm =ChatOpenAI(
    model=LLM_MODEL,
    api_key=deepseek_API_KEY,
    base_url=deepseek_API_BASE,
    temperature=0.8,
    streaming=True,
)