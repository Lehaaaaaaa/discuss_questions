from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sum_of_likes = models.PositiveIntegerField(default = 0)
    sum_of_dislikes = models.PositiveIntegerField(default = 0)

class Tag(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    slug = models.SlugField(max_length = 50, unique = True)
    description = models.TextField(blank = True)

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')

    title = models.CharField(max_length=200, default="Без названия")

    slug = models.SlugField(max_length=255, unique = True, blank = True, null = True)
    text = models.TextField()
    is_solved = models.BooleanField(default=False, verbose_name="Решено")

    image = models.ImageField(upload_to='question_images/', blank=True, null = True)
    video = models.FileField(upload_to='question_videos/', blank=True, null = True)

    tags = models.ManyToManyField(Tag, blank=True)

    likes = models.ManyToManyField(User, blank=True, related_name='liked_questions')

    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments', verbose_name="Вопрос")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту {self.question.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    question = models.ForeignKey(Question, on_delete = models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'question')

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Обязательно добавляем related_name='reports', чтобы работал поиск со стороны Вопроса
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reports')

    REASONS = [
        ('spam', 'Спам / Реклама'),
        ('insult', 'Оскорбления / Нецензурная лексика'),
        ('wrong_topic', 'Вопрос не по теме сайта'),
        ('other', 'Другое'),
    ]
    reason = models.CharField(max_length=20, choices=REASONS)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        target_question = self.question
        likes_count = target_question.likes.count()
        reports_count = target_question.reports.count()

        if likes_count == 0:
            if reports_count > 0:
                target_question.delete()
            return

        if reports_count >= likes_count:
            target_question.delete()
        else:            
            report_percentage = (reports_count / likes_count) * 100
            if report_percentage >= 40:
                target_question.delete()