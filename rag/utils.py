from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from django.conf import settings

class RAGPipeline:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.llm = OpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    def process_document(self, document):
        text = document.file.read().decode('utf-8')
        texts = self.text_splitter.split_text(text)
        vectorstore = FAISS.from_texts(texts, self.embeddings)
        return vectorstore

    def answer_question(self, vectorstore, question):
        qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=vectorstore.as_retriever())
        return qa.run(question)

