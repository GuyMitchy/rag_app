from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Document
from .forms import DocumentForm
from rag.utils import RAGPipeline
from django.contrib import messages
import traceback
import chardet
from pypdf import PdfReader
import io
import markdown

# Create your views here.

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            
            file_content = document.file.read()
            file_extension = document.file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                text_content = extract_text_from_pdf(file_content)
            elif file_extension in ['txt', 'md']:
                text_content = file_content.decode('utf-8')
                if file_extension == 'md':
                    text_content = markdown.markdown(text_content)
            else:
                messages.error(request, "Unsupported file type. Please upload a PDF, TXT, or MD file.")
                return redirect('upload_document')
            
            document.content = text_content
            document.save()
            
            # Process the document
            try:
                rag_pipeline = RAGPipeline()
                rag_pipeline.process_document(document)
                document.processed = True
                document.save()
                messages.success(request, "Document uploaded and processed successfully.")
            except Exception as e:
                messages.error(request, f"Error processing document: {str(e)}")
            
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form})

def extract_text_from_pdf(file_content):
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text_content = ""
    for page in pdf_reader.pages:
        text_content += page.extract_text() + "\n"
    return text_content

@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'documents/list.html', {'documents': documents})

def home(request):
    if request.user.is_authenticated:
        return redirect('document_list')
    return render(request, 'home.html')

@login_required
def ask_question(request, document_id):
    document = Document.objects.get(id=document_id)
    if request.method == 'POST':
        question = request.POST.get('question')
        vectorstore = document.get_vectorstore()
        rag_pipeline = RAGPipeline()
        answer = rag_pipeline.answer_question(vectorstore, question)
        return render(request, 'documents/qa.html', {'document': document, 'question': question, 'answer': answer})
    return render(request, 'documents/qa.html', {'document': document})

@login_required
def document_qa(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if request.method == 'POST':
        question = request.POST.get('question')
        try:
            if document.processed:
                rag_pipeline = RAGPipeline()
                result = rag_pipeline.answer_question(document, question)
                answer = result['result']
                sources = result['sources']  # This line changed
            else:
                answer = "This document hasn't been processed yet."
                sources = []
        except Exception as e:
            answer = f"An error occurred while processing your question: {str(e)}"
            sources = []
        
        return render(request, 'documents/qa.html', {
            'document': document,
            'question': question,
            'answer': answer,
            'sources': sources
        })
    
    return render(request, 'documents/qa.html', {'document': document})
