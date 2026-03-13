from django import forms
from .models import Users, Profile
from django.core.validators import EmailValidator


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования основной информации пользователя"""
    full_name = forms.CharField(max_length=150, label='ФИО', required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(max_length=20, label='Телефон', required=True)
    
    class Meta:
        model = Users
        fields = ['full_name', 'email', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['full_name'].initial = self.instance.full_name
            self.fields['email'].initial = self.instance.email
            self.fields['phone'].initial = self.instance.phone


class ProfileExtendedForm(forms.ModelForm):
    """Форма для редактирования дополнительной информации профиля"""
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'birth_date', 'phone_alt', 'address']
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
            'birth_date': 'Дата рождения',
            'phone_alt': 'Дополнительный телефон',
            'address': 'Адрес',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input'}),
            'phone_alt': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 (___) ___-__-__'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
        }

class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()  
    password = forms.CharField(min_length=6)
    password_confirm = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают')
        return cleaned_data