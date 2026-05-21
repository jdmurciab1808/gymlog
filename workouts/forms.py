from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Exercise, Routine, WorkoutSession, WorkoutSet, MuscleGroup


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'muscle_group', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ej. Press de banca'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descripción opcional...'}),
            'muscle_group': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
        }


class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ['name', 'description', 'exercises']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ej. Push Day A'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'exercises': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exercises'].queryset = Exercise.objects.filter(created_by=user)


class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['routine', 'date', 'duration_minutes', 'notes']
        widgets = {
            'routine': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['routine'].queryset = Routine.objects.filter(user=user)
        self.fields['routine'].required = False


class WorkoutSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = ['exercise', 'set_number', 'reps', 'weight', 'rpe', 'notes']
        widgets = {
            'exercise': forms.Select(attrs={'class': 'form-input'}),
            'set_number': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'reps': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': 0}),
            'rpe': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': 1, 'max': 10}),
            'notes': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nota opcional...'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exercise'].queryset = Exercise.objects.filter(created_by=user)


WorkoutSetFormSet = forms.inlineformset_factory(
    WorkoutSession,
    WorkoutSet,
    form=WorkoutSetForm,
    extra=3,
    can_delete=True,
)
