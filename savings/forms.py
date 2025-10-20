# savings/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Member, Contribution, Expense
from django.contrib.auth.models import User

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'phone_number_1', 'phone_number_2']

# class ContributionForm(forms.ModelForm):
#     class Meta:
#         model = Contribution
#         fields = ['member', 'amount', 'date', 'note']
#
#     def clean(self):
#         cleaned = super().clean()
#         member = cleaned.get('member')
#         date = cleaned.get('date')
#         if member and date:
#             if Contribution.objects.filter(member=member, month=date.month, year=date.year).exists():
#                 raise ValidationError("This member already has a contribution recorded for that month.")
#         return cleaned

# class ExpenseForm(forms.ModelForm):
#     class Meta:
#         model = Expense
#         fields = ['category', 'amount', 'date', 'description']


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['member', 'amount', 'date']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:outline-none'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:outline-none'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:outline-none'
            }),
        }

    def clean(self):
        cleaned = super().clean()
        member = cleaned.get('member')
        date = cleaned.get('date')
        if member and date:
            if Contribution.objects.filter(member=member, month=date.month, year=date.year).exists():
                raise ValidationError("This member already has a contribution recorded for that month.")
        return cleaned


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-red-500 focus:outline-none'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-red-500 focus:outline-none'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-red-500 focus:outline-none'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-red-500 focus:outline-none h-20'
            }),
        }



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data
