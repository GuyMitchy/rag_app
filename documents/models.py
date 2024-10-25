from django.db import models
from django.contrib.auth.models import User
import pickle
import base64
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from django.conf import settings

# Create your models here.

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    vectorstore_data = models.TextField(null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('txt', 'Text'),
        ('md', 'Markdown')
    ], null=True, blank=True)  # Make it optional

    def __str__(self):
        return self.title

    def save_vectorstore(self, vectorstore):
        # Serialize the index to bytes
        serialized_index = vectorstore.serialize_to_bytes()
        # Encode the bytes to base64 string
        encoded_index = base64.b64encode(serialized_index).decode('utf-8')
        self.vectorstore_data = encoded_index
        self.processed = True
        self.save()

    def get_vectorstore(self):
        if self.vectorstore_data:
            # Decode the base64 string back to bytes
            serialized_index = base64.b64decode(self.vectorstore_data)
            # Deserialize the bytes back to a FAISS index
            return FAISS.deserialize_from_bytes(
                embeddings=OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY),
                serialized=serialized_index,
                allow_dangerous_deserialization=True  # Add this line
            )
        return None

    def save(self, *args, **kwargs):
        if not self.id and not self.file_type:  # Only set file_type on creation if not already set
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)
