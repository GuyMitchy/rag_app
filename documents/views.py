from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Document
from .forms import DocumentForm

# Create your views here.

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
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
