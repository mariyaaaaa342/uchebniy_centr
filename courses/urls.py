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
]
