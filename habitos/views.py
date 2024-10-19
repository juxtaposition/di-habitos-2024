from django import forms
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect



"""
Apartado para la vista login
"""
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('habit_list')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

"""
Apartado para la vista register
"""
class CustomUserCreationForm(forms.ModelForm):

    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('login')
"""
Aparatado para la vista home
"""
def home_view(request):
    return render(request, 'home.html')

"""
Apartado para la vista dashboard
"""
def dashboard_view(request):
    steps_data = [1000, 9500, 8000, 12000, 6000]
    water_data = [2, 2.5, 2.2, 2, 2.4, 2.3, 2]
    avg_data = {
        '2h': [120, 140, 160, 180, 200, 220, 240],
        '30m': [30, 40, 50, 60, 70, 80, 90],
        '5h': [300, 350, 400, 450, 500, 550, 600]
    }
    return render(request, 'dashboard.html', {
        'steps_data': steps_data,
        'water_data': water_data,
        'avg_data': avg_data
    })