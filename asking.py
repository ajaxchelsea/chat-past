import argparse
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

from helpers import print_documents

current_folder = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="Ask your question to OpenAI, combined the top k relevant docs in context.")
parser.add_argument('--db-folder', type=str, default=current_folder + "/db/", help="The folder of your indexed private data.")
parser.add_argument('--top-k', type=int, default=10, help="Default value is 10.")
parser.add_argument("query", type=str, help="The question you want to ask.")
args = parser.parse_args()

db_folder = args.db_folder
top_k = args.top_k
query = args.query

# Step4：从硬盘加载向量数据库，查询与问题最相似的 Top K 片段
embeddings = OpenAIEmbeddings()
vectordb = Chroma(embedding_function=embeddings, persist_directory=db_folder)
relevant_docs = vectordb.similarity_search(query, top_k)
print_documents(relevant_docs)

# Step 5：组成 context，向 OpenAI 发出真正请求
chain = load_qa_chain(OpenAI(temperature=0.7, max_tokens=1024), chain_type="stuff")
answer = chain.run(input_documents=relevant_docs, question=query)
print("answer: ")
print(answer)