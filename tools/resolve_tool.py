from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatOpenAI(temperature=0)

# Use a prompt like:
prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are a finance assistant. Given a company name or stock ticker symbol, return its corresponding company name only.

Examples:
AAPL → Apple
TSLA → Tesla
GOOGL → Google
MSFT → Microsoft

Input: {input}
Company Name:"""
)

resolve_chain = LLMChain(llm=llm, prompt=prompt)

def resolve_company_name(input: str) -> str:
    result = resolve_chain.run({"input": input.strip()})
    return result.strip()