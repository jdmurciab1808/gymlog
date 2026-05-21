from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, Max
from django.utils import timezone
from datetime import timedelta

from .models import Exercise, Routine, WorkoutSession, WorkoutSet, MuscleGroup
from .forms import (
    RegisterForm, ExerciseForm, RoutineForm,
    WorkoutSessionForm, WorkoutSetForm, WorkoutSetFormSet
)


# ─── Vistas públicas ────────────────────────────────────────────────────────

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear grupos musculares por defecto
            defaults = ['Pecho', 'Espalda', 'Hombros', 'Bíceps', 'Tríceps',
                        'Piernas', 'Glúteos', 'Core', 'Cardio']
            for g in defaults:
                MuscleGroup.objects.get_or_create(name=g)
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}! Tu cuenta ha sido creada.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


# ─── Dashboard ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    recent_sessions = WorkoutSession.objects.filter(user=user).order_by('-date')[:5]
    total_sessions = WorkoutSession.objects.filter(user=user).count()
    sessions_this_week = WorkoutSession.objects.filter(user=user, date__gte=week_ago).count()
    total_routines = Routine.objects.filter(user=user).count()
    total_exercises = Exercise.objects.filter(created_by=user).count()

    # PRs por ejercicio (top 5 más usados)
    top_exercises = Exercise.objects.filter(
        created_by=user,
        sets__isnull=False
    ).annotate(
        max_weight=Max('sets__weight'),
        total_sets=Count('sets')
    ).order_by('-total_sets')[:5]

    context = {
        'recent_sessions': recent_sessions,
        'total_sessions': total_sessions,
        'sessions_this_week': sessions_this_week,
        'total_routines': total_routines,
        'total_exercises': total_exercises,
        'top_exercises': top_exercises,
        'today': today,
    }
    return render(request, 'dashboard.html', context)


# ─── Ejercicios ──────────────────────────────────────────────────────────────

class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'exercises/list.html'
    context_object_name = 'exercises'

    def get_queryset(self):
        return Exercise.objects.filter(created_by=self.request.user).select_related('muscle_group')


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = Exercise
    template_name = 'exercises/detail.html'
    context_object_name = 'exercise'

    def get_queryset(self):
        return Exercise.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        exercise = self.get_object()
        sets = WorkoutSet.objects.filter(
            session__user=self.request.user,
            exercise=exercise
        ).order_by('session__date')

        history = []
        for s in sets:
            history.append({
                'date': s.session.date.strftime('%d/%m'),
                'weight': float(s.weight or 0),
                'reps': s.reps,
            })

        ctx['history'] = history
        ctx['personal_record'] = exercise.get_personal_record(self.request.user)
        return ctx


class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/form.html'
    success_url = reverse_lazy('workouts:exercise_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Ejercicio creado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Nuevo Ejercicio'
        ctx['action'] = 'Crear'
        return ctx


class ExerciseUpdateView(LoginRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/form.html'
    success_url = reverse_lazy('workouts:exercise_list')

    def get_queryset(self):
        return Exercise.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Ejercicio actualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Editar Ejercicio'
        ctx['action'] = 'Guardar cambios'
        return ctx


class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    template_name = 'exercises/confirm_delete.html'
    success_url = reverse_lazy('workouts:exercise_list')
    context_object_name = 'exercise'

    def get_queryset(self):
        return Exercise.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Ejercicio eliminado.')
        return super().form_valid(form)


# ─── Rutinas ─────────────────────────────────────────────────────────────────

class RoutineListView(LoginRequiredMixin, ListView):
    model = Routine
    template_name = 'routines/list.html'
    context_object_name = 'routines'

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user).prefetch_related('exercises')


class RoutineDetailView(LoginRequiredMixin, DetailView):
    model = Routine
    template_name = 'routines/detail.html'
    context_object_name = 'routine'

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sessions'] = self.get_object().sessions.order_by('-date')[:10]
        return ctx


class RoutineCreateView(LoginRequiredMixin, CreateView):
    model = Routine
    form_class = RoutineForm
    template_name = 'routines/form.html'
    success_url = reverse_lazy('workouts:routine_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Rutina creada.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Nueva Rutina'
        ctx['action'] = 'Crear'
        return ctx


class RoutineUpdateView(LoginRequiredMixin, UpdateView):
    model = Routine
    form_class = RoutineForm
    template_name = 'routines/form.html'
    success_url = reverse_lazy('workouts:routine_list')

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Rutina actualizada.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Editar Rutina'
        ctx['action'] = 'Guardar cambios'
        return ctx


class RoutineDeleteView(LoginRequiredMixin, DeleteView):
    model = Routine
    template_name = 'routines/confirm_delete.html'
    success_url = reverse_lazy('workouts:routine_list')
    context_object_name = 'routine'

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Rutina eliminada.')
        return super().form_valid(form)


# ─── Sesiones ────────────────────────────────────────────────────────────────

class SessionListView(LoginRequiredMixin, ListView):
    model = WorkoutSession
    template_name = 'sessions/list.html'
    context_object_name = 'sessions'
    paginate_by = 10

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user).select_related('routine')


class SessionDetailView(LoginRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = 'sessions/detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sets'] = self.get_object().sets.select_related('exercise').order_by('exercise__name', 'set_number')
        return ctx


@login_required
def session_create(request):
    if request.method == 'POST':
        session_form = WorkoutSessionForm(request.user, request.POST)
        if session_form.is_valid():
            session = session_form.save(commit=False)
            session.user = request.user
            session.save()
            formset = WorkoutSetFormSet(
                request.POST,
                instance=session,
                form_kwargs={'user': request.user}
            )
            if formset.is_valid():
                formset.save()
                messages.success(request, '¡Sesión registrada exitosamente!')
                return redirect('workouts:session_detail', pk=session.pk)
    else:
        session_form = WorkoutSessionForm(request.user)
        formset = WorkoutSetFormSet(form_kwargs={'user': request.user})

    return render(request, 'sessions/form.html', {
        'session_form': session_form,
        'formset': formset,
        'title': 'Nueva Sesión',
    })


@login_required
def session_edit(request, pk):
    session = get_object_or_404(WorkoutSession, pk=pk, user=request.user)
    if request.method == 'POST':
        session_form = WorkoutSessionForm(request.user, request.POST, instance=session)
        formset = WorkoutSetFormSet(
            request.POST,
            instance=session,
            form_kwargs={'user': request.user}
        )
        if session_form.is_valid() and formset.is_valid():
            session_form.save()
            formset.save()
            messages.success(request, 'Sesión actualizada.')
            return redirect('workouts:session_detail', pk=session.pk)
    else:
        session_form = WorkoutSessionForm(request.user, instance=session)
        formset = WorkoutSetFormSet(instance=session, form_kwargs={'user': request.user})

    return render(request, 'sessions/form.html', {
        'session_form': session_form,
        'formset': formset,
        'title': 'Editar Sesión',
        'session': session,
    })


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkoutSession
    template_name = 'sessions/confirm_delete.html'
    success_url = reverse_lazy('workouts:session_list')
    context_object_name = 'session'

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Sesión eliminada.')
        return super().form_valid(form)


# ─── Progreso ────────────────────────────────────────────────────────────────

@login_required
def progress_view(request):
    user = request.user
    exercises = Exercise.objects.filter(created_by=user).annotate(
        max_weight=Max('sets__weight'),
        total_sets=Count('sets')
    ).filter(total_sets__gt=0).order_by('-max_weight')

    return render(request, 'progress.html', {'exercises': exercises})
