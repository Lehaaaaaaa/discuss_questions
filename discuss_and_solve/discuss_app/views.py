from django.shortcuts import render
from .models import Question

def index(request):
    all_questions = Question.objects.all()
    context = {
        'questions':all_questions
    }
    return render(request, 'index.html', context)
