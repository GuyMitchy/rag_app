from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Document
from .forms import DocumentForm
from rag.utils import RAGPipeline

# Create your views here.

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            
            # Process the document
            rag_pipeline = RAGPipeline()
            vectorstore = rag_pipeline.process_document(document)
            document.save_vectorstore(vectorstore)
            
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form})

@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user)
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
