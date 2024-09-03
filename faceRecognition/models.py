from django.db import models
from django.contrib.auth.models import User
import numpy as np

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Keep the default OneToOneField relationship
    username = models.CharField(max_length=150, unique=True, default='default_user')  # Store username as a separate field
    face_encoding = models.BinaryField(blank=True) 

    def __str__(self):
        return self.username 

    def set_face_encoding(self, encoding):
        self.face_encoding = encoding.tobytes()

    def get_face_encoding(self):
        if self.face_encoding:
            return np.frombuffer(self.face_encoding, dtype=np.float64)
        return None