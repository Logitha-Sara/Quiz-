from django.test import TestCase
from .models import Quiz

class QuizTestCase(TestCase):
    def test_quiz_creation(self):
        quiz = Quiz.objects.create(title='Python Basics')
        self.assertEqual(quiz.title, 'Python Basics')


