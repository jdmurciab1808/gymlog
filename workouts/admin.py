from django.contrib import admin
from .models import MuscleGroup, Exercise, Routine, WorkoutSession, WorkoutSet


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'category', 'created_by', 'created_at']
    list_filter = ['category', 'muscle_group']
    search_fields = ['name', 'created_by__username']
    raw_id_fields = ['created_by']


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 0
    fields = ['exercise', 'set_number', 'reps', 'weight', 'rpe']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'routine', 'duration_minutes', 'total_volume']
    list_filter = ['date', 'routine']
    search_fields = ['user__username']
    inlines = [WorkoutSetInline]
    date_hierarchy = 'date'

    def total_volume(self, obj):
        return f"{obj.total_volume()} kg·rep"
    total_volume.short_description = "Volumen total"


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'total_sessions', 'updated_at']
    search_fields = ['name', 'user__username']
    filter_horizontal = ['exercises']


@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise', 'set_number', 'reps', 'weight', 'rpe']
    list_filter = ['exercise']
    search_fields = ['exercise__name', 'session__user__username']


admin.site.site_header = "GymLog Admin"
admin.site.site_title = "GymLog"
admin.site.index_title = "Panel de administración"
