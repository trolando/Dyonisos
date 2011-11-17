from django import forms
from django.utils.safestring import mark_safe
from jdideal.subscribe.models import *

class SubscribeForm(forms.Form):
    def __init__(self, event, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        # First the manditory fields
        self.fields["first_name"] = forms.CharField(max_length=64, 
                                        required=True, label="Voornaam")
        self.fields["last_name"] = forms.CharField(max_length=64, 
                                        required=True, label="Achternaam")
        self.fields["email"] = forms.EmailField(required=True, label="Email")
        
        # The dynamic fields
        for question in event.eventquestion_set.all():
            name = question.form_id()
            if question.question_type == "INT":
                self.fields[name] = forms.IntegerField(label = question.name,
                                                    required = question.required)
            elif question.question_type ==  "TXT":
                self.fields[name] = forms.CharField(max_length=256,
                                                    label = question.name,
                                                    required = question.required)
            elif question.question_type == "AFD":
                self.fields[name] = forms.CharField(max_length=256, 
                                            label=question.name,
                                            required=question.required,
                                            widget=forms.Select(choices=AFDELINGEN))
            elif question.question_type == "BOOL":
                self.fields[name] = forms.BooleanField(label=question.name,
                                                       required=question.required)
        # Closing fixed options
        self.fields["option"] = forms.ModelChoiceField(
                                        queryset=event.eventoption_set.all(),
                                        label="Optie")
        # Only show bank choice if at least one of the options costs money
        if not event.all_free():
            self.fields["issuer"] = forms.ModelChoiceField(
                                queryset=IdealIssuer.objects.all(), label="Bank")

def fill_subscription(form, event):
    reg = Registration(event=event)
    reg.first_name = form.cleaned_data["first_name"]
    reg.last_name = form.cleaned_data["last_name"]
    reg.email = form.cleaned_data["email"]
    reg.event_option = form.cleaned_data["option"]
    reg.save()
    for question in event.eventquestion_set.all():
        ans = Answer(question=question)
        ans.set_answer(form.cleaned_data[question.form_id()])
        ans.save()
        reg.answers.add(ans)
    reg.save()
    return reg