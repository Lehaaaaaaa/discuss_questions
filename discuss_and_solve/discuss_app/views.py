from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Favorite, Report, Comment
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.text import slugify


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'text', 'image']

def index(request):
    all_questions = Question.objects.all().order_by('-created_at')
    
    user_favorites_ids = []
    user_reports_ids = []
    
    if request.user.is_authenticated:
        user_favorites_ids = Favorite.objects.filter(user=request.user).values_list('question_id', flat=True)
        user_reports_ids = Report.objects.filter(user=request.user).values_list('question_id', flat=True)
        
    return render(request, 'index.html', {
        'questions': all_questions, 
        'user_favorites_ids': user_favorites_ids,
        'user_reports_ids': user_reports_ids
    })

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

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.author == request.user:
        question.delete()
    return redirect('index_page')

@login_required
def toggle_resolve(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.author == request.user:
        question.is_solved = not question.is_solved
        question.save()
    return redirect(request.META.get('HTTP_REFERER', 'index_page'))

@login_required
def toggle_like(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.user in question.likes.all():
        question.likes.remove(request.user)
    else:
        question.likes.add(request.user)
    
    return redirect(request.META.get('HTTP_REFERER', 'index_page'))

@login_required
def toggle_favorite(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    favorite_record = Favorite.objects.filter(user = request.user, question = question)

    if favorite_record.exists():
        favorite_record.delete()
    else:
        Favorite.objects.create(user=request.user, question = question)
    return redirect(request.META.get('HTTP_REFERER', 'index_page'))


@login_required
def favorite_questions(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('question')
    questions = [fav.question for fav in favorites]
    user_favorites_ids = [q.id for q in questions]
    
    return render(request, 'favorites.html', {
        'questions': questions,
        'user_favorites_ids': user_favorites_ids
    })


@login_required
def toggle_report(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    existing_report = Report.objects.filter(user=request.user, question=question).first()
    
    if existing_report:
        existing_report.delete()
    else:
        Report.objects.create(user=request.user, question=question, reason='other')
        
    return redirect('index_page')



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш ответ или комментарий...'
            })
        }


def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    comments = question.comments.all()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.question = question
            comment.author = request.user
            comment.save()
            return redirect('question_detail', question_id=question.id)
    else:
        form = CommentForm()
        
    return render(request, 'question_detail.html', {
        'question': question,
        'comments': comments,
        'form': form
    })

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    return redirect('question_detail', question_id=comment.question.id)

@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
    return redirect('question_detail', question_id=comment.question.id)