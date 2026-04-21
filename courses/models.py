from django.db import models

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
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ADMIN_ROLE_CHOICES, default='operator')
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admins'

class Applications(models.Model):
    application_id = models.AutoField(primary_key=True)
    course = models.ForeignKey('Courses', models.DO_NOTHING)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    application_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=APPLICATION_STATUS_CHOICES, default='new')
    admin_comment = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(Admins, models.DO_NOTHING, db_column='processed_by', blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'applications'
        unique_together = (('user', 'course'),)

class CourseProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    course = models.ForeignKey('Courses', models.DO_NOTHING)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=15, choices=PROGRESS_STATUS_CHOICES, default='not_started')
    modules_progress = models.JSONField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_progress'
        unique_together = (('user', 'course'),)

class Courses(models.Model):
    course_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey('Teachers', models.DO_NOTHING)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    course_program = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    price_offline = models.DecimalField(max_digits=10, decimal_places=2)
    price_online = models.DecimalField(max_digits=10, decimal_places=2)
    offline_available = models.BooleanField(blank=True, null=True)
    online_available = models.BooleanField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=COURSE_STATUS_CHOICES, default='active')
    max_students = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'courses'

class Favorites(models.Model):
    favorite_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    course = models.ForeignKey(Courses, models.DO_NOTHING)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'favorites'
        unique_together = (('user', 'course'),)

class News(models.Model):
    news_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.CharField(max_length=255, blank=True, null=True)
    publish_date = models.DateField()
    type = models.CharField(max_length=10, choices=NEWS_TYPE_CHOICES, default='news')
    is_active = models.BooleanField(blank=True, null=True)
    created_by = models.ForeignKey(Admins, models.DO_NOTHING, db_column='created_by')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'news'

class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifications'

class WorkType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Код')
    
    class Meta:
        managed = False
        db_table = 'work_type'  # ← важно! Имя таблицы должно совпадать
        verbose_name = 'Тип работы'
        verbose_name_plural = 'Типы работ'
    
    def __str__(self):
        return self.name
    
class Portfolio(models.Model):
   
    # Выбор автора
    AUTHOR_TYPE_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('student', 'Студент/Выпускник'),
    ]
    
    portfolio_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='Название работы')
    
    # Два способа добавить фото: через загрузку файла или через URL
    image = models.ImageField(upload_to='portfolio/', verbose_name='Фотография (файл)', blank=True, null=True)
    image_url = models.CharField(max_length=500, verbose_name='URL фотографии (ссылка)', blank=True, null=True)
    
    work_types = models.ManyToManyField('WorkType', verbose_name='Типы работ', blank=True)
    
    author_type = models.CharField(max_length=20, choices=AUTHOR_TYPE_CHOICES, verbose_name='Тип автора')
    author_name = models.CharField(max_length=200, verbose_name='Имя автора', blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    is_active = models.BooleanField(default=True, verbose_name='Отображать на сайте')
    
    teacher = models.ForeignKey('Teachers', models.SET_NULL, blank=True, null=True)
    student = models.ForeignKey('Users', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portfolio'
        ordering = ['-created_at']

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
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    registration_date = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(blank=True, null=True)
    theme_preference = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

class Teachers(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    biography = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    email = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teachers'


