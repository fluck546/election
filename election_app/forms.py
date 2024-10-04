from django import forms
from .models import Vote, Candidate, ElectionRound, Candidate, Vote
from faceRecognition.models import User


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ["candidate"]

    def __init__(self, *args, **kwargs):
        round_id = kwargs.pop("round_id", None)
        super(VoteForm, self).__init__(*args, **kwargs)

        if round_id:
            self.fields["candidate"].queryset = Candidate.objects.filter(
                election_round_id=round_id
            )


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["sid", "name", "last_name", "branch", "is_active", "is_staff"]


class ElectionRoundForm(forms.ModelForm):
    class Meta:
        model = ElectionRound
        fields = ["name", "start_date", "end_date", "is_active"]


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['number','name', 'last_name', 'detail', 'branch', 'year', 'election_round', 'picture']
