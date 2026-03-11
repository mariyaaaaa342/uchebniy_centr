from datetime import date

from django.db import models
from django.utils import timezone



FORMAT_CHOICES = [
    ('оффлайн', 'Оффлайн'),
    ('онлайн', 'Онлайн'),
]

APPLICATION_STATUS_CHOICES = [
    ('new', 'Новая'),
    ('processed', 'Обработана'),
    ('confirmed', 'Подтверждена'),
    ('cancelled', 'Отменена'),
]

COURSE_STATUS_CHOICES = [
    ('active', 'Активен'),
    ('inactive', 'Неактивен'),
    ('archive', 'В архиве'),
]

NEWS_TYPE_CHOICES = [
    ('news', 'Новость'),
    ('promo', 'Акция'),
    ('event', 'Событие'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('course_available', 'Курс доступен'),
    ('favorite_update', 'Обновление избранного'),
    ('system', 'Системное'),
    ('promo', 'Акция'),
]

PROGRESS_STATUS_CHOICES = [
    ('not_started', 'Не начат'),
    ('in_progress', 'В процессе'),
    ('completed', 'Завершен'),
]

ADMIN_ROLE_CHOICES = [
    ('superadmin', 'Супер администратор'),
    ('content_manager', 'Контент менеджер'),
    ('operator', 'Оператор'),
]

class Admins(models.Model):
    admin_id = models.AutoField(primary_key=True, verbose_name='ID администратора')
    username = models.CharField(unique=True, max_length=50, verbose_name='Логин')
    password_hash = models.CharField(max_length=150, verbose_name='Хеш пароля')
    role = models.CharField(max_length=20, choices=ADMIN_ROLE_CHOICES, default='operator', verbose_name='Роль')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Последний вход')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')

    class Meta:
        managed = False
        db_table = 'admins'
        verbose_name = 'Администратор'           # Единственное число
        verbose_name_plural = 'Администраторы'

class Applications(models.Model):
    application_id = models.AutoField(primary_key=True, verbose_name='ID заявки')
    course = models.ForeignKey('Courses', models.DO_NOTHING, verbose_name='Курс')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name='Формат')
    application_date = models.DateTimeField(default=timezone.now, verbose_name='Дата подачи')
    status = models.CharField(max_length=15, choices=APPLICATION_STATUS_CHOICES, default='new', verbose_name='Статус')
    admin_comment = models.TextField(blank=True, null=True, verbose_name='Комментарий администратора')
    processed_by = models.ForeignKey(Admins, models.DO_NOTHING, db_column='processed_by', blank=True, null=True, verbose_name='Обработал')
    user = models.ForeignKey('Users', models.DO_NOTHING, verbose_name='Пользователь')
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='Email')

    class Meta:
        managed = False
        db_table = 'applications'
        unique_together = (('user', 'course'),)
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f"Заявка #{self.application_id} - {self.user.full_name} - {self.course.title}"


class Module(models.Model):
    module_id = models.AutoField(primary_key=True, verbose_name='ID модуля')
    course = models.ForeignKey('Courses', on_delete=models.CASCADE, related_name='modules', verbose_name='Курс')
    title = models.CharField(max_length=200, verbose_name='Название модуля')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    
    class Meta:
        managed = False
        db_table = 'modules'
        ordering = ['order', 'module_id']
        verbose_name = 'Модуль курса'
        verbose_name_plural = 'Модули курса'
    
    def __str__(self):
        return self.title
        #return f"{self.course.title} - {self.title}"

class ModuleProgress(models.Model):
    module_progress_id = models.AutoField(primary_key=True, verbose_name='ID прогресса модуля')
    progress = models.ForeignKey('CourseProgress', on_delete=models.CASCADE, related_name='modules_progress_list', verbose_name='Прогресс курса')
    module = models.ForeignKey('Module', on_delete=models.CASCADE, verbose_name='Модуль')
    status = models.CharField(max_length=20, choices=PROGRESS_STATUS_CHOICES, default='not_started', verbose_name='Статус')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        managed = False
        db_table = 'module_progress'
        unique_together = (('progress', 'module'),)
        verbose_name = 'Прогресс модуля'
        verbose_name_plural = 'Прогресс модулей'
    
    def __str__(self):
        return f"{self.module.title}: {self.get_status_display()}"
    
class CourseProgress(models.Model):
    progress_id = models.AutoField(primary_key=True, verbose_name='ID прогресса')
    user = models.ForeignKey('Users', models.DO_NOTHING, verbose_name='Пользователь')
    course = models.ForeignKey('Courses', models.DO_NOTHING, verbose_name='Курс')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, blank=True, null=True, verbose_name='Формат')
    status = models.CharField(max_length=15, choices=PROGRESS_STATUS_CHOICES, default='not_started', verbose_name='Статус')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')
    last_accessed_at = models.DateTimeField(blank=True, null=True, verbose_name='Последний доступ')
    has_reviewed = models.BooleanField(default=False, verbose_name='<Благодарим за отзыв, это очень важно для нас!')

    class Meta:
        managed = True
        db_table = 'course_progress'
        unique_together = (('user', 'course'),)
        verbose_name = 'Прогресс обучения'
        verbose_name_plural = 'Прогресс студентов'

    def __str__(self):
        return f"Прогресс: {self.user.full_name} - {self.course.title}"
    
    def update_status_from_modules(self):
        """Обновляет общий статус на основе ModuleProgress"""
        # Проверяем, есть ли уже primary key (объект сохранён в БД)
        if not self.pk:
            return  # Если объект ещё не сохранён, ничего не делаем
        
        modules_progress = self.modules_progress_list.all()
        if not modules_progress.exists():
            self.status = 'not_started'
            return
        
        statuses = [mp.status for mp in modules_progress]
        if all(s == 'completed' for s in statuses):
            self.status = 'completed'
        elif any(s in ['in_progress', 'completed'] for s in statuses):
            self.status = 'in_progress'
        else:
            self.status = 'not_started'
    def save(self, *args, **kwargs):
        # Обновляем статус только если объект уже существует в БД
        if self.pk:
            self.update_status_from_modules()
        super().save(*args, **kwargs)

class Courses(models.Model):
    course_id = models.AutoField(primary_key=True, verbose_name='ID курса')
    teacher = models.ForeignKey('Teachers', models.DO_NOTHING, verbose_name='Преподаватель')
    title = models.CharField(max_length=200, verbose_name='Название курса')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    duration = models.CharField(max_length=50, blank=True, null=True, verbose_name='Длительность')
    price_offline = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (оффлайн)')
    price_online = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (онлайн)')  
    status = models.CharField(max_length=10, choices=COURSE_STATUS_CHOICES, default='active', verbose_name='Статус')
    max_students = models.IntegerField(blank=True, null=True, verbose_name='Макс. студентов')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления')

    offline_available = models.BooleanField(
    blank=True, 
    null=True, 
    verbose_name='Доступен оффлайн',
    choices=[(True, 'Да'), (False, 'Нет')]
    )

    online_available = models.BooleanField(
        blank=True, 
        null=True, 
        verbose_name='Доступен онлайн',
        choices=[(True, 'Да'), (False, 'Нет')]
    )

    class Meta:
        managed = False
        db_table = 'courses'
        verbose_name = 'Курс'           
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title

class Favorites(models.Model):
    favorite_id = models.AutoField(primary_key=True, verbose_name='ID избранного курса')
    user = models.ForeignKey('Users', models.DO_NOTHING, verbose_name='Пользователь')
    course = models.ForeignKey(Courses, models.DO_NOTHING, verbose_name='Курс')
    added_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата добавления')

    class Meta:
        managed = False
        db_table = 'favorites'
        unique_together = (('user', 'course'),)
        verbose_name = 'Избранное'           
        verbose_name_plural = 'Избранные курсы'

class News(models.Model):
    news_id = models.AutoField(primary_key=True, verbose_name='ID новости/акции')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='URL изображения')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name='Изображение (файл)')
    publish_date = models.DateField(verbose_name='Дата публикации')
    type = models.CharField(max_length=10, choices=NEWS_TYPE_CHOICES, default='news', verbose_name='Тип')
    is_active = models.BooleanField(blank=True, null=True, verbose_name='Активно')
    created_by = models.ForeignKey(Admins, models.DO_NOTHING, db_column='created_by', verbose_name='Автор')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления')

    class Meta:
        managed = False
        db_table = 'news'
        verbose_name = 'Новость'           
        verbose_name_plural = 'Новости'

class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True, verbose_name='ID уведомления')
    user = models.ForeignKey('Users', models.DO_NOTHING, verbose_name='Пользователь')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='system', verbose_name='Тип')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщения')
    is_read = models.BooleanField(blank=True, null=True, verbose_name='Прочитано')
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ссылка')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')

    class Meta:
        managed = False
        db_table = 'notifications'
        verbose_name = 'Уведомление'           
        verbose_name_plural = 'Уведомления'

class WorkType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Код')
    
    class Meta:
        managed = False
        db_table = 'work_type'  
        verbose_name = 'Тип работы'
        verbose_name_plural = 'Типы работ'
    
    def __str__(self):
        return self.name
    
class Portfolio(models.Model):   
    AUTHOR_TYPE_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('student', 'Студент/Выпускник'),
    ]
    portfolio_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='Название работы')   
    image = models.ImageField(upload_to='portfolio/', verbose_name='Фотография (файл)', blank=True, null=True)
    image_url = models.CharField(max_length=500, verbose_name='URL фотографии (ссылка)', blank=True, null=True)    
    work_types = models.ManyToManyField('WorkType', verbose_name='Типы работ', blank=True)
    author_type = models.CharField(max_length=20, choices=AUTHOR_TYPE_CHOICES, verbose_name='Тип автора')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    is_active = models.BooleanField(default=True, verbose_name='Отображать на сайте')
 

    class Meta:
        managed = False
        db_table = 'portfolio'
        ordering = ['-created_at']
        verbose_name = 'Портфолио'           # Единственное число
        verbose_name_plural = 'Портфолио'

    def __str__(self):
        return self.title
    
    def get_work_types_list(self):
        """Возвращает список названий типов работ"""
        return [wt.name for wt in self.work_types.all()]
    
    def get_work_types_slugs(self):
        """Возвращает список slug для фильтрации"""
        return [wt.slug for wt in self.work_types.all()]
    
    def get_work_types_display(self):
        """Возвращает строку с типами работ через запятую"""
        return ', '.join(self.get_work_types_list())
    def get_image_url(self):
        """Возвращает URL изображения (из файла или из URL)"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/images/no-image.jpg'
    
class Users(models.Model):
    user_id = models.AutoField(primary_key=True, verbose_name='ID пользователя')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    email = models.EmailField(unique=True, max_length=100, verbose_name='Email')
    password_hash = models.CharField(max_length=255, verbose_name='Хеш пароля')
    registration_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата регистрации')
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)

    is_verified = models.BooleanField(
        blank=True, 
        null=True, 
        verbose_name='Подтверждён',
        choices=[(True, 'Да'), (False, 'Нет')]
    )
    
    theme_preference = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        verbose_name='Тема оформления',
        choices=[('light', 'Светлая'), ('dark', 'Тёмная')]
    )

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Пользователь'           # Единственное число
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name

class Teachers(models.Model):
    teacher_id = models.AutoField(primary_key=True, verbose_name='ID преподавателя')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    biography = models.TextField(blank=True, null=True, verbose_name='Биография')
    specialization = models.CharField(max_length=200, blank=True, null=True, verbose_name='Специализация')
    photo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фото')
    experience = models.IntegerField(blank=True, null=True, verbose_name='Опыт (лет)')
    email = models.CharField(unique=True, max_length=100, verbose_name='Email')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')

    class Meta:
        managed = False
        db_table = 'teachers'
        verbose_name = 'преподаватель'           # Единственное число
        verbose_name_plural = 'преподаватели'
        
    def __str__(self):
        return self.full_name

class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('Users', on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар', blank=True, null=True)
    bio = models.TextField(max_length=500, verbose_name='О себе', blank=True, null=True)
    birth_date = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    phone_alt = models.CharField(max_length=20, verbose_name='Доп. телефон', blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        managed = False
        db_table = 'profiles'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.full_name if self.user else 'без пользователя'}"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'
    

class Review(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонён'),
    ]
    review_id = models.AutoField(primary_key=True, verbose_name='ID отзыва')
    student_name = models.CharField(max_length=150, verbose_name='Имя студента')
    course = models.ForeignKey('Courses', models.SET_NULL, blank=True, null=True, verbose_name='Курс')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(default=5, choices=RATING_CHOICES, verbose_name='Оценка')
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name='Фото студента')
    is_active = models.BooleanField(default=False, verbose_name='Отображать на сайте')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус модерации')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
    
    def __str__(self):
        return f"{self.student_name} - {self.course.title if self.course else 'Общий отзыв'}"
    
    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/courses/images/default-avatar.png'
    
class Certificate(models.Model):
    certificate_id = models.AutoField(primary_key=True, verbose_name='ID сертификата')
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name='Название')
    image = models.ImageField(upload_to='certificates/', verbose_name='Изображение')
    order = models.IntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        managed = False
        db_table = 'certificates'
        ordering = ['order', '-created_at']
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
    
    def __str__(self):
        return self.title or f'Сертификат #{self.certificate_id}'
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Applications)
def send_new_application_notification(sender, instance, created, **kwargs):
    """Отправляет уведомление администратору при создании новой заявки"""
    if created:
        # Собираем информацию о заявке
        subject = f'Новая заявка на курс {instance.course.title}'
        
        message = f"""
        Поступила новая заявка на обучение!

        Детали заявки:
        - Студент: {instance.user.full_name}
        - Курс: {instance.course.title}
        - Формат: {instance.format}
        - Телефон: {instance.user.phone}
        - Email: {instance.user.email}
        - Дата заявки: {instance.application_date.strftime('%d.%m.%Y %H:%M') if instance.application_date else 'Не указана'}

        🔗 Ссылка в админ панели: https://ledy-center.ru/admin/courses/applications/{instance.application_id}/change/
        """
        
        # Отправляем письмо администратору
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['miininamasha6@gmail.com'],  
            fail_silently=False,
        )