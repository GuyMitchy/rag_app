from django.db import models
from django.contrib.auth.models import User
import pickle

# Create your models here.

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    vectorstore = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save_vectorstore(self, vectorstore):
        self.vectorstore = pickle.dumps(vectorstore)
        self.processed = True
        self.save()

    def get_vectorstore(self):
        return pickle.loads(self.vectorstore) if self.vectorstore else None
