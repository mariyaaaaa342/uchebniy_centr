from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # Главная страница
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
]
