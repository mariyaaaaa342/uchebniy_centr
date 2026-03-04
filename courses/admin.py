from django import forms
from django.contrib import admin
from .models import Courses, Teachers, Applications, Users, Portfolio, WorkType,  CourseProgress
import json

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
    
    def save_model(self, request, obj, form, change):
        """При сохранении заявки проверяем статус"""
        super().save_model(request, obj, form, change)
        
        # Если заявка подтверждена
        if obj.status == 'confirmed':
            from .models import CourseProgress
            # Создаём прогресс, если его ещё нет
            CourseProgress.objects.get_or_create(
                user=obj.user,
                course=obj.course,
                defaults={
                    'format': obj.format,
                    'status': 'not_started',
                    'modules_progress': {}
                }
            )
    
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

class CourseProgressForm(forms.ModelForm):
    """Форма для редактирования прогресса с удобными полями для каждого модуля"""
    
    class Meta:
        model = CourseProgress
        fields = ['user', 'course', 'format', 'status', 'started_at', 'completed_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Проверяем, есть ли экземпляр и курс
        if self.instance and self.instance.pk and self.instance.course:
            # Получаем программу курса
            course_program = self.instance.course.course_program or ''
            modules = self.parse_program_to_modules(course_program)
            
            # Получаем текущий прогресс
            modules_progress = self.instance.modules_progress or {}
            
            # Создаём поле для каждого модуля (не больше 20)
            for i, module in enumerate(modules[:20], 1):
                field_name = f'module_{i}'
                current_status = modules_progress.get(field_name, 'not_started')
                
                self.fields[field_name] = forms.ChoiceField(
                    label=module['title'],
                    choices=[
                        ('not_started', '⚪ Не начат'),
                        ('in_progress', '🟡 В процессе'),
                        ('completed', '✅ Пройден'),
                    ],
                    initial=current_status,
                    required=False,
                )
    
    def parse_program_to_modules(self, program):
        """Парсит программу курса в список модулей"""
        modules = []
        if not program:
            return modules
        
        lines = program.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Очищаем заголовок
            clean_title = line
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                clean_title = line[1:].strip()
            elif line[0].isdigit() and '.' in line[:3]:
                parts = line.split('.', 1)
                if len(parts) > 1:
                    clean_title = parts[1].strip()
            
            modules.append({
                'key': f'module_{len(modules) + 1}',
                'title': clean_title[:100]
            })
        
        # Если модулей нет, создаём один модуль
        if not modules and program:
            modules.append({
                'key': 'module_1',
                'title': program[:100] if len(program) > 100 else program
            })
        
        return modules
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Собираем JSONB из полей модулей
        modules_progress = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('module_'):
                modules_progress[field_name] = value
        
        instance.modules_progress = modules_progress
        
        # Обновляем общий статус на основе прогресса модулей
        if modules_progress:
            statuses = list(modules_progress.values())
            if all(s == 'completed' for s in statuses):
                instance.status = 'completed'
                from django.utils import timezone
                if not instance.completed_at:
                    instance.completed_at = timezone.now()
            elif any(s in ['in_progress', 'completed'] for s in statuses):
                instance.status = 'in_progress'
                from django.utils import timezone
                if not instance.started_at:
                    instance.started_at = timezone.now()
            else:
                instance.status = 'not_started'
        
        if commit:
            instance.save()
        return instance


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    form = CourseProgressForm
    list_display = ('progress_id', 'get_user_name', 'get_course_title', 'format', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'format')
    search_fields = ('user__full_name', 'user__phone', 'course__title')
    readonly_fields = ('progress_id', 'last_accessed_at')
    
    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else '-'
    get_user_name.short_description = 'Студент'
    
    def get_course_title(self, obj):
        return obj.course.title if obj.course else '-'
    get_course_title.short_description = 'Курс'
    
    def get_fieldsets(self, request, obj=None):
        """Динамически создаём fieldsets с модулями ТОЛЬКО для существующих объектов"""
        fieldsets = [
            ('Студент и курс', {'fields': ('user', 'course', 'format')}),
            ('Статус', {'fields': ('status',)}),
            ('Даты', {'fields': ('started_at', 'completed_at', 'last_accessed_at')}),
        ]
        
        # ТОЛЬКО для существующих объектов (у которых есть pk и курс)
        if obj and obj.pk and obj.course:
            course_program = obj.course.course_program or ''
            lines = [l.strip() for l in course_program.split('\n') if l.strip()]
            if lines:
                # Ограничиваем количество модулей первыми 20
                module_lines = lines[:20]
                module_fields = [f'module_{i+1}' for i in range(len(module_lines))]
                fieldsets.insert(2, ('Прогресс по модулям', {'fields': module_fields}))
        
        return fieldsets