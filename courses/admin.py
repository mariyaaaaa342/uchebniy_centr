from django.contrib import admin
from .models import Courses, Teachers, Applications, Users

# Регистрация с настройками (через декоратор)
@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'teacher', 'price_online', 'status')
    list_filter = ('status', 'offline_available', 'online_available')
    search_fields = ('title',)

@admin.register(Teachers)
class TeachersAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'full_name', 'specialization', 'experience', 'email')
    search_fields = ('full_name', 'email')

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'get_user_full_name', 'get_user_phone', 'course', 'format', 'status', 'application_date')
    list_filter = ('status', 'format')
    search_fields = ('user__full_name', 'user__phone', 'course__title')
    readonly_fields = ('application_date',)
    
    def get_user_full_name(self, obj):
        return obj.user.full_name if obj.user else '-'
    get_user_full_name.short_description = 'ФИО'
    
    def get_user_phone(self, obj):
        return obj.user.phone if obj.user else '-'
    get_user_phone.short_description = 'Телефон'

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'phone', 'email', 'registration_date')
    search_fields = ('full_name', 'phone', 'email')
    exclude = ('password_hash',)
    readonly_fields = ('registration_date',)