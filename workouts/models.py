from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MuscleGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name="Grupo muscular")

    class Meta:
        verbose_name = "Grupo Muscular"
        verbose_name_plural = "Grupos Musculares"
        ordering = ['name']

    def __str__(self):
        return self.name


class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ('fuerza', 'Fuerza'),
        ('cardio', 'Cardio'),
        ('flexibilidad', 'Flexibilidad'),
        ('funcional', 'Funcional'),
    ]
    name = models.CharField(max_length=100, verbose_name="Nombre del ejercicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.SET_NULL, null=True, related_name='exercises', verbose_name="Grupo muscular")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='fuerza', verbose_name="Categoría")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises', verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_personal_record(self, user):
        """Retorna el máximo peso levantado por el usuario en este ejercicio."""
        sets = WorkoutSet.objects.filter(
            session__user=user,
            exercise=self
        ).order_by('-weight')
        if sets.exists():
            return sets.first().weight
        return None


class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines', verbose_name="Usuario")
    name = models.CharField(max_length=100, verbose_name="Nombre de la rutina")
    description = models.TextField(blank=True, verbose_name="Descripción")
    exercises = models.ManyToManyField(Exercise, blank=True, related_name='routines', verbose_name="Ejercicios")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def total_sessions(self):
        return self.sessions.count()


class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name="Usuario")
    routine = models.ForeignKey(Routine, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions', verbose_name="Rutina")
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    notes = models.TextField(blank=True, verbose_name="Notas")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name="Duración (min)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sesión de Entrenamiento"
        verbose_name_plural = "Sesiones de Entrenamiento"
        ordering = ['-date']

    def __str__(self):
        return f"Sesión {self.date} - {self.user.username}"

    def total_volume(self):
        """Calcula el volumen total (kg × reps) de la sesión."""
        total = 0
        for s in self.sets.all():
            total += (s.weight or 0) * s.reps
        return total


class WorkoutSet(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='sets', verbose_name="Sesión")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='sets', verbose_name="Ejercicio")
    set_number = models.PositiveIntegerField(default=1, verbose_name="# Serie")
    reps = models.PositiveIntegerField(verbose_name="Repeticiones")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    rpe = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="RPE (esfuerzo 1-10)")
    notes = models.CharField(max_length=200, blank=True, verbose_name="Nota")

    class Meta:
        verbose_name = "Serie"
        verbose_name_plural = "Series"
        ordering = ['set_number']

    def __str__(self):
        return f"Serie {self.set_number} - {self.exercise.name}: {self.reps}x{self.weight}kg"
