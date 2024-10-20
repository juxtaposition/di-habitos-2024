from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and not User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('El usuario no existe.'))

        user = authenticate(username=username, password=password)
        if username and password and user is None:
            raise forms.ValidationError(_('La contraseña es incorrecta.'))

        return cleaned_data

class CustomUserCreationForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'username': 'Usuario',
            'email': 'Correo',
            'password': 'Contraseña',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'username': forms.TextInput(attrs={'class': 'form-control',}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'password': forms.PasswordInput(attrs={'class': 'form-control',}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user