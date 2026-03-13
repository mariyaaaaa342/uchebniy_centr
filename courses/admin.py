from django import forms
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import admin
from .models import Courses, Teachers, Applications, Users, Portfolio, WorkType, Module, ModuleProgress, CourseProgress, News, Certificate
from .models import Review

@admin.register(Teachers)
class TeachersAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'full_name', 'specialization', 'experience', 'email')
    search_fields = ('full_name', 'email')

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'get_user_full_name', 'get_user_phone', 'email', 'course', 'format', 'status', 'application_date')
    list_filter = ('status', 'format')
    search_fields = ('user__full_name', 'user__phone', 'course__title')
    readonly_fields = ('application_date',)
    
    def save_model(self, request, obj, form, change):
        """При сохранении заявки проверяем статус"""
        super().save_model(request, obj, form, change)
        
        #Если заявка подтверждена
        if obj.status == 'confirmed':
            from .models import CourseProgress, Module, ModuleProgress
            
            #Проверяем, существует ли уже прогресс
            progress = CourseProgress.objects.filter(
                user=obj.user,
                course=obj.course
            ).first()
            
            if not progress:
                #Создаём прогресс 
                progress = CourseProgress.objects.create(
                    user=obj.user,
                    course=obj.course,
                    format=obj.format,
                    status='not_started'
                )
                print(f"Создан новый прогресс #{progress.progress_id}")
            else:
                print(f"Прогресс уже существует #{progress.progress_id}")
            
            #Добавляем все модули курса
            all_modules = Module.objects.filter(course=obj.course)
            for module in all_modules:
                mp, created = ModuleProgress.objects.get_or_create(
                    progress=progress,
                    module=module,
                    defaults={'status': 'not_started'}
                )
                if created:
                    print(f"  Добавлен модуль: {module.title}")
    
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
    list_display = ('portfolio_id', 'title', 'get_work_types_display', 'author_type', 'created_at', 'is_active')
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
            'fields': ('author_type',)
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

class ModuleInline(admin.TabularInline):
    """Inline-форма для модулей внутри курса"""
    model = Module
    extra = 1
    fields = ['title', 'order']
    ordering = ['order']

@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'teacher', 'price_online', 'status')
    list_filter = ('status', 'offline_available', 'online_available')
    search_fields = ('title',)
    inlines = [ModuleInline]

class ModuleProgressInline(admin.TabularInline):
    """Inline-форма для прогресса модулей внутри прогресса курса"""
    model = ModuleProgress
    extra = 0
    fields = ['module', 'status']
    readonly_fields = ['module']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('module')
    
    def has_change_permission(self, request, obj=None):
        #Разрешаем изменение только если объект существует
        return obj is not None
    
    def has_add_permission(self, request, obj=None):
        #Разрешаем добавление только если объект существует
        return obj is not None

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('progress_id', 'get_user_name', 'get_course_title', 'format', 'status')
    list_filter = ('status', 'format')
    search_fields = ('user__full_name', 'user__phone', 'course__title')
    readonly_fields = ('progress_id', 'last_accessed_at')
    inlines = [ModuleProgressInline]  
    
    fieldsets = (
        ('Студент и курс', {'fields': ('user', 'course', 'format')}),
        ('Даты', {'fields': ('started_at', 'completed_at', 'last_accessed_at')}),
    )
    
    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else '-'
    get_user_name.short_description = 'Студент'
    
    def get_course_title(self, obj):
        return obj.course.title if obj.course else '-'
    get_course_title.short_description = 'Курс'
    
    def save_model(self, request, obj, form, change):
        """При создании нового прогресса автоматически создаём записи для всех модулей курса"""
        super().save_model(request, obj, form, change)
        
        if not change:  # Только для новых объектов
            modules = obj.course.modules.all()
            for module in modules:
                ModuleProgress.objects.get_or_create(
                    progress=obj,
                    module=module,
                    defaults={'status': 'not_started'}
                )

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'image_preview', 'publish_date', 'is_active')
    list_filter = ('type', 'is_active', 'publish_date')
    search_fields = ('title', 'content')
    date_hierarchy = 'publish_date'
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'type', 'publish_date', 'is_active')
        }),
        ('Изображение', {
            'fields': ('image_url', 'image', 'image_preview'),
            'description': 'Вы можете указать ссылку на изображение (URL) или загрузить файл'
        }),
        ('Автор', {
            'fields': ('created_by',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 150px;"/>', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 150px;"/>', obj.image_url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            from .models import Admins
            #Создаём или получаем администратора 
            admin, created = Admins.objects.get_or_create(
                username=request.user.username,
                defaults={
                    'password_hash': 'system',
                    'role': 'superadmin',
                    'created_at': timezone.now()
                }
            )
            obj.created_by = admin
        super().save_model(request, obj, form, change)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'course', 'rating_display', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'rating', 'course')
    search_fields = ('student_name', 'text')
    list_editable = ('status', 'is_active')
    list_per_page = 20
    
    fieldsets = (
        ('Информация об отзыве', {
            'fields': ('student_name', 'course', 'text', 'rating', 'photo')
        }),
        ('Модерация', {
            'fields': ('status', 'is_active'),
            'description': 'Чтобы отзыв появился на сайте, выберите статус "Одобрен" и поставьте галочку "Активен"'
        }),
    )
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return stars
    rating_display.short_description = 'Оценка'
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(status='approved', is_active=True)
        self.message_user(request, f'{queryset.count()} отзыв(ов) одобрено')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'
    
    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected', is_active=False)
        self.message_user(request, f'{queryset.count()} отзыв(ов) отклонено')
    reject_reviews.short_description = 'Отклонить выбранные отзывы'

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('title',)
    list_per_page = 20
    fieldsets = (
        ('Информация о сертификате', {
            'fields': ('title', 'image', 'order', 'is_active')
        }),
    )