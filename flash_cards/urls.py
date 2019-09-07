from django.urls import path
from . import views

urlpatterns = [
    path('create_lesson/', views.CreateLessonView.as_view(), name='create_lesson'),
    path('lesson/mark_correct/<entryPk>/<lessonPk>/<lessonIndex>', views.markCorrect, name='lesson_mark_correct'),
    path('lesson/mark_incorrect/<entryPk>/<lessonPk>/<lessonIndex>', views.markIncorrect, name='lesson_mark_incorrect'),
    path('view_entry_tier/<tier>', views.EntryTierView.as_view(), name='view_entry_tier'),
    path('lesson/<pk>', views.LessonView.as_view(), name='view_lesson'),
    path('', views.Index.as_view(), name='flash_cards_index'),
]