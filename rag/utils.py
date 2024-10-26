from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from django.conf import settings
import numpy as np

class RAGPipeline:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.llm = OpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY, max_tokens=256)

    def process_document(self, document):
        texts = self.text_splitter.split_text(document.content)
        vectorstore = FAISS.from_texts(texts, self.embeddings)
        return vectorstore

    def answer_question(self, document, question):
        vectorstore = self.process_document(document)
        relevant_docs = vectorstore.similarity_search(question, k=10)

        if not self._check_relevance(question, relevant_docs):
            return {
                "result": "I'm sorry, but I couldn't find any relevant information about that topic in the document.",
                "sources": []
            }

        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        prompt_template = """You are a helpful assistant that answers questions based ONLY on the information provided in the context below. If the answer cannot be found in the context, say "I'm sorry, but I don't have enough information to answer that question based on the given context." Do not use any external knowledge.

        Context:
        {context}

        Question: {question}
        Answer:"""
        
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        
        formatted_prompt = prompt.format(context=context, question=question)
        
        result = self.llm.invoke(formatted_prompt)

        return {
            "result": result,
            "sources": [doc.page_content for doc in relevant_docs]
        }

    def _check_relevance(self, question, documents, threshold=0.5):
        question_embedding = self.embeddings.embed_query(question)
        for doc in documents:
            doc_embedding = self.embeddings.embed_query(doc.page_content)
            similarity = self._cosine_similarity(question_embedding, doc_embedding)
            if similarity > threshold:
                return True
        return False

    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
