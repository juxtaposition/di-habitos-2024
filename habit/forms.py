from django import forms
from .models import Habit, Category

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'frequency', 'repetitions', 'category']
        labels = {
            'name': 'Nombre',
            'frequency': 'Frecuencia',
            'repetitions': 'Repeticiones',
            'category': 'Categoría',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-modal', 'placeholder': 'Ingrese el nombre del hábito'}),
            'frequency': forms.Select(attrs={'class': 'form-control-modal', 'style':'background-color:white'}),
            'repetitions': forms.NumberInput(attrs={'class': 'form-control-modal', 'placeholder': 'Número de repeticiones'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'] = forms.ModelChoiceField(
            queryset=Category.objects.all(),
            label='Categoría',
            widget=forms.Select(attrs={'class': 'form-control-modal','style':'background-color:white'})
        )