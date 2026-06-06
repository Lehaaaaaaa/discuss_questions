from django.shortcuts import render, redirect
from .models import Question
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.text import slugify


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'text', 'image']

def index(request):
    all_questions = Question.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'questions':all_questions})

@login_required(login_url = 'login')
def create_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit = False)
            question.author = request.user
            question.save()
            return redirect('index_page')
    else:
        form = QuestionForm()
    
    return render(request, 'create_question.html', {'form':form})


