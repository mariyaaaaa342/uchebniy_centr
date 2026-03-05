from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  
    path('about/', views.about_us, name='about'),
    path('courses/', views.course_list, name='course_list'),
    path('teachers/', views.teachers, name='teachers'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit-application/', views.submit_application, name='submit_application'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/applications/', views.profile_applications, name='profile_applications'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('progress/<int:progress_id>/', views.course_progress_detail, name='course_progress_detail'),
    path('api/update-module-progress/', views.update_module_progress, name='update_module_progress'),
    path('save-theme/', views.save_theme, name='save_theme'),
    path('contacts/', views.contacts, name='contacts'),
    path('news/', views.news_list, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('available-for-review/', views.available_for_review, name='available_for_review'),
    path('submit-review/', views.submit_review, name='submit_review'),
]
