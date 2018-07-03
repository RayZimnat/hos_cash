import datetime

from django import forms
from django.forms import ModelForm, RadioSelect
from django.utils import timezone

from .models import Agent, Book, Claim, Dependant, Insured, Policy, PolicyVersion, PayingAuthority


class ClaimForm(ModelForm):
    class Meta:
        model = Claim
        exclude = [
            'policy',
            'created_by',
            'approved_by',
            'approved_date',
            'dependant',
            'status'
        ]
        labels = {
            'days': 'Number of days',
            'amount': 'Claim amount',
            'peril_detail': 'Details',
            'preexisting': 'Pre-existitng condition?',
            'bank_branch': 'Branch',
            }
        widgets = {
            'peril_type': RadioSelect()
        }

class DependantForm(ModelForm):
    class Meta:
        model = Dependant
        exclude = ['policy', 'dependant_deleted', 'dependant_monthly_premium']


class InsuredForm(ModelForm):
    class Meta:
        model = Insured
        fields = '__all__'
        labels = {
            'insured_surname': 'Surname',
            'insured_name': 'First name(s)',
            'insured_gender': 'Gender',
            'insured_id_number': 'ID number',
            'insured_nationality': 'Nationality',
            'insured_dob': 'Date of birth',
            'insured_employer': 'Employer',
            'insured_occupation':'Occupation',
            'insured_phone': 'Phone number',
            'insured_address': 'Address',
            'insured_e_address':'Email address',
            'insured_ec_number':'EC Number'
            }

    def clean(self):
        cleaned_data = super(InsuredForm, self).clean()
        dob = cleaned_data.get('insured_dob')

        if dob:
            if dob > datetime.date.today():
                raise forms.ValidationError(
                    'Date of birth cannot be later than today'
                )


class PolicyForm(ModelForm):
    class Meta:
        model = Policy
        fields = ['agent', 'proposal_number',
                    'proposal_date', 'inception_date', 'payment_method', 'paying_authority', 'scheme']


class PolicyVersionForm(ModelForm):
    class Meta:
        model = PolicyVersion
        fields = ['narration', 'effective_date']
        labels = {
            'narration':'Reason for endorsement'
        }


class SearchForm(forms.Form):
    search = forms.CharField(max_length=200, required=False)


class AgentSearchForm(forms.Form):
    agent_code = forms.CharField(max_length = 10, required=False)
    agent_name = forms.CharField(max_length=20, required=False)
    agent_branch = forms.ChoiceField(required=False,
        choices= [
            ('','All'),
            ('Harare','Harare'),
            ('Bulawayo','Bulawayo'),
            ('Kwekwe', 'Kwekwe'),
            ('Mutare', 'Mutare'),
            ('Masvingo', 'Masvingo'),
            ('Vic Falls', 'Vic Falls'),
            ('Gweru', 'Gweru'),
        ])


class GPWReportForm(forms.Form):
    date_from = forms.DateField(label ="From")
    date_to = forms.DateField(label="to")


class ReportForm(forms.Form):
    inception_date_from = forms.DateField(label="From")
    inception_date_to = forms.DateField(label="to")


class LodgementReportForm(forms.Form):
    date_from = forms.DateField(label="From")
    to = forms.DateField(label="to")
    payment_method = forms.ChoiceField(
        choices= [
            ('Ecocash','Ecocash'),
            ('Stop order','Stop order'),
            ('Cash', 'Cash'),
        ])
    paying_authority = forms.ModelChoiceField(PayingAuthority.objects.all())


class LodgementDownloadForm(forms.Form):
    date_from = forms.DateField(label="From")
    to = forms.DateField(label="to")
    payment_method = forms.CharField(max_length=100, required=False)


class PayingAuthorityForm(ModelForm):

    class Meta:
        model = PayingAuthority
        fields = '__all__'
        labels = {
            'paying_contact_person':'Contact person',
            'paying_contact_number':'Contact number',
            'paying_cut_off_date':'Cut-off',
            'paying_authority_name':'Company name'
        }


class AgentForm(ModelForm):
    class Meta:
        model = Agent
        fields = ['agent_code',
                  'agent_branch',
                  'agent_name',
                  'agent_email',
                  'agent_phone'
                  ]


class BookForm(ModelForm):
    class Meta:
        model = Book
        exclude = ['agent']


class CancelForm(forms.Form):
    reason = forms.CharField(max_length=100)
    date = forms.DateField()
