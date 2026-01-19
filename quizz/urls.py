from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('quiz/<slug:category_slug>/', views.quiz, name="quiz"),
    path('submit/<slug:category_slug>/', views.submit_quiz, name="submit_quiz"),
    path('leaderboard/', views.leaderboard, name="leaderboard"),
    path('result/<slug:category_slug>/', views.final_result, name="final_result"),
    path('login/', auth_views.LoginView.as_view(template_name='quizz/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
]


