from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    # Ejercicios
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/new/', views.ExerciseCreateView.as_view(), name='exercise_create'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercises/<int:pk>/edit/', views.ExerciseUpdateView.as_view(), name='exercise_edit'),
    path('exercises/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise_delete'),

    # Rutinas
    path('routines/', views.RoutineListView.as_view(), name='routine_list'),
    path('routines/new/', views.RoutineCreateView.as_view(), name='routine_create'),
    path('routines/<int:pk>/', views.RoutineDetailView.as_view(), name='routine_detail'),
    path('routines/<int:pk>/edit/', views.RoutineUpdateView.as_view(), name='routine_edit'),
    path('routines/<int:pk>/delete/', views.RoutineDeleteView.as_view(), name='routine_delete'),

    # Sesiones
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/new/', views.session_create, name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('sessions/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),

    # Progreso
    path('progress/', views.progress_view, name='progress'),
]
