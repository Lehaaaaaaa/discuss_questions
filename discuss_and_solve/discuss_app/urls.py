from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns= [
    path('', views.index, name = 'index_page'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ask/', views.create_question, name = 'create_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name = 'delete_question'),
    path('question/<int:question_id>/toggle/', views.toggle_resolve, name='toggle_resolve'),
    path('question/<int:question_id>/like/', views.toggle_like, name='toggle_like'),
    path('question/<int:question_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_questions, name='favorite_questions')
]