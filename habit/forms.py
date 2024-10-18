from django import forms
from .models import Habit, Category

class HabitForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = self.get_category_choices()

    def get_category_choices(self):
        categories = Category.objects.all()
        return [(category.id, category.name) for category in categories]

    class Meta:
        model = Habit
        fields = ['name', 'description', 'frequency']
