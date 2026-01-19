from django.contrib import admin
from .models import Category, Question, Choice, QuizResult

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'category')

admin.site.register(Category)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizResult)
