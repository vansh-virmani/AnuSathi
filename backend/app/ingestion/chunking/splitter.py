

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200,
    separators=[
        "\n\n","\n", ". ", " ", ""
         #on basis of paras, new line, word, sentence it splits text...
    ],
)


def split_documents(documents: list[Document]) -> list[Document]:
    return text_splitter.split_documents(documents)

