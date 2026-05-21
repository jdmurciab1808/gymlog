from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import MuscleGroup, Exercise, Routine, WorkoutSession, WorkoutSet


class MuscleGroupModelTest(TestCase):
    def test_str(self):
        mg = MuscleGroup.objects.create(name="Pecho")
        self.assertEqual(str(mg), "Pecho")


class ExerciseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='pass1234')
        self.mg = MuscleGroup.objects.create(name="Piernas")
        self.exercise = Exercise.objects.create(
            name="Sentadilla",
            muscle_group=self.mg,
            category='fuerza',
            created_by=self.user
        )

    def test_str(self):
        self.assertEqual(str(self.exercise), "Sentadilla")

    def test_personal_record_no_sets(self):
        self.assertIsNone(self.exercise.get_personal_record(self.user))

    def test_personal_record_with_sets(self):
        session = WorkoutSession.objects.create(user=self.user, date=timezone.now().date())
        WorkoutSet.objects.create(session=session, exercise=self.exercise, set_number=1, reps=5, weight=100)
        WorkoutSet.objects.create(session=session, exercise=self.exercise, set_number=2, reps=5, weight=120)
        pr = self.exercise.get_personal_record(self.user)
        self.assertEqual(float(pr), 120.0)


class WorkoutSessionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester2', password='pass1234')
        self.mg = MuscleGroup.objects.create(name="Pecho")
        self.exercise = Exercise.objects.create(
            name="Press Banca",
            muscle_group=self.mg,
            category='fuerza',
            created_by=self.user
        )
        self.session = WorkoutSession.objects.create(user=self.user, date=timezone.now().date())

    def test_total_volume_empty(self):
        self.assertEqual(self.session.total_volume(), 0)

    def test_total_volume_with_sets(self):
        WorkoutSet.objects.create(session=self.session, exercise=self.exercise, set_number=1, reps=10, weight=50)
        WorkoutSet.objects.create(session=self.session, exercise=self.exercise, set_number=2, reps=8, weight=60)
        # 10*50 + 8*60 = 500 + 480 = 980
        self.assertEqual(self.session.total_volume(), 980)

    def test_str(self):
        self.assertIn('tester2', str(self.session))


class RoutineModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester3', password='pass1234')

    def test_routine_creation(self):
        routine = Routine.objects.create(user=self.user, name="Push Day")
        self.assertEqual(routine.name, "Push Day")
        self.assertEqual(routine.total_sessions(), 0)


class AuthViewTest(TestCase):
    def test_landing_redirects_anon(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_post_valid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_required_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')


class ExerciseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('viewuser', password='pass1234')
        self.client.login(username='viewuser', password='pass1234')
        self.mg = MuscleGroup.objects.create(name="Espalda")
        self.exercise = Exercise.objects.create(
            name="Dominadas",
            muscle_group=self.mg,
            category='fuerza',
            created_by=self.user
        )

    def test_exercise_list(self):
        response = self.client.get(reverse('workouts:exercise_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dominadas')

    def test_exercise_create(self):
        response = self.client.post(reverse('workouts:exercise_create'), {
            'name': 'Peso Muerto',
            'description': 'Ejercicio compuesto',
            'muscle_group': self.mg.pk,
            'category': 'fuerza',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Exercise.objects.filter(name='Peso Muerto').exists())

    def test_exercise_delete(self):
        response = self.client.post(reverse('workouts:exercise_delete', args=[self.exercise.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Exercise.objects.filter(pk=self.exercise.pk).exists())

    def test_other_user_cannot_edit(self):
        other = User.objects.create_user('other', password='pass1234')
        self.client.login(username='other', password='pass1234')
        response = self.client.get(reverse('workouts:exercise_edit', args=[self.exercise.pk]))
        self.assertEqual(response.status_code, 404)


class RoutineViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('routineuser', password='pass1234')
        self.client.login(username='routineuser', password='pass1234')

    def test_routine_list(self):
        response = self.client.get(reverse('workouts:routine_list'))
        self.assertEqual(response.status_code, 200)

    def test_routine_create(self):
        response = self.client.post(reverse('workouts:routine_create'), {
            'name': 'Legs Day',
            'description': 'Día de piernas',
            'exercises': [],
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Routine.objects.filter(name='Legs Day').exists())
