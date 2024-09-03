from django.db import models
from django.contrib.auth.models import User


class ElectionRound(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    election_round = models.ForeignKey(ElectionRound, related_name='candidates', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    election_round = models.ForeignKey(ElectionRound, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.voter} voted for {self.candidate}'

