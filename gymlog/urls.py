from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from workouts import views as workout_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', workout_views.landing, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', workout_views.register_view, name='register'),
    path('dashboard/', workout_views.dashboard, name='dashboard'),
    path('workouts/', include('workouts.urls', namespace='workouts')),
]
