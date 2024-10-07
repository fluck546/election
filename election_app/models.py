from django.db import models

from django.conf import settings
from faceRecognition.models import User


class ElectionRound(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    number = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40, blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    branch = models.CharField(max_length=40, blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    picture = models.ImageField(upload_to="candidate_pictures/", blank=True, null=True)
    election_round = models.ForeignKey(
        ElectionRound, related_name="candidates", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    election_round = models.ForeignKey(ElectionRound, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True, blank=True)  # Allow NULL for absent votes
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.voter} voted for {self.candidate}"
