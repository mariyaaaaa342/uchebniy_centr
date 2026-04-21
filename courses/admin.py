from django.contrib import admin
from .models import Courses, Teachers, Applications, Users, Portfolio, WorkType

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

@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('portfolio_id', 'title', 'get_work_types_display', 'author_type', 'author_name', 'created_at', 'is_active')
    list_filter = ('work_types', 'author_type', 'is_active')
    search_fields = ('title', 'author_name', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    
    filter_horizontal = ('work_types',)  

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'work_types', 'description')
        }),
        ('Автор', {
            'fields': ('author_type', 'author_name', 'teacher', 'student')
        }),
        ('Изображение', {
            'fields': ('image', 'image_url')
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    def get_work_types_display(self, obj):
        return obj.get_work_types_display()
    get_work_types_display.short_description = 'Типы работ'