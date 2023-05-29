import os

from langchain.document_loaders import DirectoryLoader, EverNoteLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

import argparse
from helpers import print_documents, AnyEncodingTextLoader, AnyEncodingHtmlLoader

current_folder = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="""
Using OpenAI Embedding API to index your private data, and persist them to Chroma.

It will load all supported files from your specified source folder. Currently it
supports text file(*.txt), markdown file(*.md) and html file(*.htm*). The support 
for Evernote exported notes is coming.
""")
parser.add_argument('--source-folder', type=str, default=current_folder + "/source/", help="The source folder in which your private data is located.")
parser.add_argument('--db-folder', type=str, default=current_folder + "/db/", help="The folder in which the indexed data will be persisted.")
parser.add_argument('--chunk-size', type=int, default=200, help="chunk size to split your documents. Default is 200.")
args = parser.parse_args()
source_folder = os.path.realpath(args.source_folder)
chunk_size = args.chunk_size
db_folder = args.db_folder

# Step1：加载笔记目录下所有之前的笔记，包含子目录
original_documents = DirectoryLoader(source_folder, glob="*.md", recursive=True).load()
original_documents.extend(DirectoryLoader(source_folder, glob="*.txt", recursive=True, loader_cls=AnyEncodingTextLoader).load())
original_documents.extend(DirectoryLoader(source_folder, glob="*.htm*", recursive=True, loader_cls=AnyEncodingHtmlLoader).load())
original_documents.extend(DirectoryLoader(source_folder, glob="*.enex", recursive=True, loader_cls=EverNoteLoader, loader_kwargs={"load_single_document":False}).load())

# Step2：分块，合适长度
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size/10)
chunked_docs = text_splitter.split_documents(original_documents)
print_documents(chunked_docs)

# Step3：用 OpenAI 创建所有笔记的embedding，并持久化到 vector db 中
#        这一步只需要做一次，后面用的时候直接从硬盘加载，避免费钱

embeddings = OpenAIEmbeddings()
vectordb = Chroma.from_documents(documents=chunked_docs, embedding=embeddings, persist_directory=db_folder)
vectordb.persist()