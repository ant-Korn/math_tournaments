from django import forms
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from tournaments.models import Tournament, Round, Task
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TournamentCreateForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'name',
            'top_N_to_final',
            'top_N_winners',
        ]


    def __init__(self, *args, **kwargs):
        super(TournamentCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Сохранить'))

class TournamentUpdateForm(forms.ModelForm):
    class Meta:
        model = Tournament
        exclude = [
            'owner'
        ]


    def __init__(self, *args, **kwargs):
        super(TournamentUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Сохранить'))

class RoundForm(forms.ModelForm):
    class Meta:
        model = Round
        exclude = [
            'tournament',
            'subscribers',
        ]


    def __init__(self, *args, **kwargs):
        super(RoundForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Сохранить'))

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = [
            'round',
            'user_answer',
        ]


    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Сохранить'))
