from django import forms
from .models import Habit, Category

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'frequency', 'category']
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'frequency': 'Frecuencia',
            'category': 'Categoría',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-modal', 'placeholder': 'Ingrese el nombre del hábito'}),
            'description': forms.Textarea(attrs={'class': 'form-control-modal', 'rows': 2, 'placeholder': 'Describa su hábito'}),
            'frequency': forms.Select(attrs={'class': 'form-control-modal', 'style':'background-color:white'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'] = forms.ModelChoiceField(
            queryset=Category.objects.all(),
            label='Categoría',
            widget=forms.Select(attrs={'class': 'form-control-modal','style':'background-color:white'})
        )

