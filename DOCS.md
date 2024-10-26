# RAG-based Study Assistant: Development Log and Documentation

## Project Overview

This project involves the development of a Retrieval-Augmented Generation (RAG) based study assistant using Django. The application allows users to upload documents, process them, and ask questions about their content using AI-powered natural language processing.

## Key Components

1. **Backend**: Django (Python)
2. **Database**: PostgreSQL (implied from Django usage)
3. **AI/ML**: LangChain, OpenAI API
4. **File Processing**: PyPDF2 for PDFs, built-in support for text files, Markdown library for .md files

## Development Process and Challenges

### Initial Setup and Basic Functionality

1. Created Django project structure with `documents` and `rag` apps.
2. Implemented basic document upload and storage functionality.
3. Integrated OpenAI's language model for question answering.

### RAG Pipeline Implementation

1. Created `RAGPipeline` class in `rag/utils.py` to handle document processing and question answering.
2. Implemented document chunking, embedding, and vector storage using FAISS.
3. Used LangChain's `RetrievalQA` for initial question-answering functionality.

### Challenges and Solutions

#### 1. PDF Processing

**Challenge**: Needed to extract text content from PDF files.
**Solution**: Used PyPDF2 (later updated to use `pypdf`) to read PDF content and extract text.


python
from pypdf import PdfReader
import io
def extract_text_from_pdf(file_content):
pdf_reader = PdfReader(io.BytesIO(file_content))
text_content = ""
for page in pdf_reader.pages:
text_content += page.extract_text() + "\n"
return text_content


#### 2. Handling Different File Types

**Challenge**: Expand support beyond PDFs to include text and Markdown files.
**Solution**: Implemented file type detection and specific processing for each type.


python
if file_extension == 'pdf':
text_content = extract_text_from_pdf(file_content)
elif file_extension in ['txt', 'md']:
text_content = file_content.decode('utf-8')
if file_extension == 'md':
text_content = markdown.markdown(text_content)


#### 3. LangChain Deprecation Warnings

**Challenge**: Encountered deprecation warnings for LangChain components.
**Solution**: Updated imports and method calls to use the latest LangChain API.


python
from langchain_openai import OpenAIEmbeddings, OpenAI
... other imports ...
class RAGPipeline:
def init(self):
self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
self.llm = OpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY, max_tokens=256)
# ... rest of the class ...



#### 4. Irrelevant Answer Generation

**Challenge**: The model sometimes generated plausible but incorrect answers not based on the document content.
**Solution**: Modified the prompt to explicitly instruct the model to use only the provided context and implemented a relevance check.


python
prompt_template = """You are a helpful assistant that answers questions based ONLY on the information provided in the context below. If the answer cannot be found in the context, say "I'm sorry, but I don't have enough information to answer that question based on the given context." Do not use any external knowledge.
Context:
{context}
Question: {question}
Answer:"""
... in the answer_question method ...
if not self.check_relevance(question, relevant_docs):
return {
"result": "I'm sorry, but I couldn't find any relevant information about that topic in the document.",
"sources": []
}



#### 5. Database Schema Updates

**Challenge**: Added new fields to the `Document` model, causing database errors.
**Solution**: Created and applied migrations, updated the model to handle optional fields, and provided data migration steps.


python
class Document(models.Model):
# ... other fields ...
file_type = models.CharField(max_length=10, choices=[
('pdf', 'PDF'),
('txt', 'Text'),
('md', 'Markdown')
], null=True, blank=True)
def save(self, args, kwargs):
if not self.id and not self.file_type:
self.file_type = self.file.name.split('.')[-1].lower()
super().save(args, kwargs)



## Current Project Structure


study_assistant/
├── documents/
│ ├── models.py
│ ├── views.py
│ ├── forms.py
│ └── urls.py
├── rag/
│ └── utils.py
├── templates/
│ └── documents/
│ ├── list.html
│ ├── upload.html
│ └── qa.html
└── study_assistant/
├── settings.py
└── urls.py



## Key Functionalities

1. **Document Upload**: Supports PDF, TXT, and MD files.
2. **Document Processing**: Extracts text, chunks it, and creates embeddings for efficient retrieval.
3. **Question Answering**: Uses RAG to provide context-aware answers based on document content.
4. **Relevance Checking**: Ensures answers are based on document content, not external knowledge.

## Future Improvements

1. Implement more robust error handling and user feedback.
2. Add support for more file types (e.g., DOCX, RTF).
3. Improve the UI/UX for a more intuitive user experience.
4. Implement user authentication and document ownership.
5. Optimize performance for large documents or high user loads.
6. Add features like document summarization or key point extraction.

## Conclusion

This RAG-based study assistant demonstrates the integration of advanced NLP techniques with a web application framework. It showcases handling various file types, processing documents for AI-powered question answering, and addressing challenges related to relevance and accuracy in information retrieval and generation.