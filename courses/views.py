from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, ProfileExtendedForm
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .forms import RegistrationForm
from .models import Applications, Teachers, Courses, Users, Portfolio, Profile, CourseProgress, Module, ModuleProgress, Review
import json

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def course_list(request):
    courses = Courses.objects.filter(status='active').prefetch_related('modules')
    context = {
        'courses': courses,
        'title': 'Nashi kursy'
    }
    return render(request, 'courses/course_list.html', context)

# courses/views.py
def submit_application(request):
    """Обработка отправки заявки (только для авторизованных пользователей)"""
    
    # Проверяем, авторизован ли пользователь
    if 'user_id' not in request.session:
        return JsonResponse({
            'success': False, 
            'error': 'Для отправки заявки необходимо войти в систему'
        }, status=401)
    
    if request.method == 'POST':
        try:
            # Получаем пользователя из сессии
            user_id = request.session['user_id']
            user = Users.objects.get(user_id=user_id)
            
            # Получаем данные из POST-запроса
            course_id = request.POST.get('course_id')
            format_type = request.POST.get('format')
            email = request.POST.get('email') 
            # Проверяем обязательные поля
            if not all([course_id, format_type]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Заполните все поля'
                }, status=400)
            
            # Получаем курс
            try:
                course = Courses.objects.get(course_id=course_id)
            except Courses.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Курс не найден'
                }, status=404)
            
            # Проверяем, не записан ли пользователь уже на этот курс
            existing_application = Applications.objects.filter(
                course=course,
                user=user
            ).first()
            
            if existing_application:
                return JsonResponse({
                    'success': False, 
                    'error': 'Вы уже записаны на этот курс'
                }, status=400)
            
            # Создаём заявку
            application = Applications.objects.create(
                course=course,
                format=format_type,
                user=user,
                status='new',
                email=email
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Заявка успешно отправлена'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Метод не разрешён'
    }, status=405)

def course_detail(request, course_id):
    course = Courses.objects.get(course_id=course_id, status='active')
    
    formats = []
    if course.offline_available:
        formats.append({
            'type': 'оффлайн',
            'name': 'Оффлайн',
            'price': course.price_offline
        })
    if course.online_available:
        formats.append({
            'type': 'онлайн',
            'name': 'Онлайн',
            'price': course.price_online
        })
    
    context = {
        'course': course,
        'formats': formats,
        'title': course.title
    }
    return render(request, 'courses/course_detail.html', context)
def index(request):
    """Главная страница"""
    return render(request, 'courses/index.html')
def about_us(request):
    """Страница О нас"""
    return render(request, 'courses/about_us.html')

def teachers(request):
    """Страница преподавателей"""
    teachers_list = Teachers.objects.all().order_by('full_name')
    context = {
        'teachers': teachers_list,
        'title': 'Наши преподаватели'
    }
    return render(request, 'courses/teachers.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Все проверки пройдены
            full_name = form.cleaned_data['full_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Проверка уникальности email и телефона (если решили оставить)
            if Users.objects.filter(phone=phone).exists():
                form.add_error('phone', 'Пользователь с таким номером телефона уже существует')
                return render(request, 'courses/register.html', {'form': form})
            
            if Users.objects.filter(email=email).exists():
                form.add_error('email', 'Пользователь с таким email уже существует')
                return render(request, 'courses/register.html', {'form': form})
            
            # Создаём пользователя
            user = Users.objects.create(
                full_name=full_name,
                phone=phone,
                email=email,
                password_hash=make_password(password),
                registration_date=timezone.now(),
                is_verified=False,
                theme_preference='light'
            )
            
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('login')
        # else: форма невалидна — ошибки уже есть в form.errors
    else:
        form = RegistrationForm()
    
    return render(request, 'courses/register.html', {'form': form})

def login_view(request):
    """Страница входа пользователя"""
    if request.method == 'POST':
        # Получаем данные из формы
        login_input = request.POST.get('login_input')  # может быть телефон или email
        password = request.POST.get('password')
        
        # Ищем пользователя по телефону или email
        user = None
        if login_input:
            user = Users.objects.filter(phone=login_input).first()
            if not user:
                user = Users.objects.filter(email=login_input).first()
        
        # Проверяем пароль
        if user and check_password(password, user.password_hash):
            # Сохраняем пользователя в сессии
            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.full_name
            messages.success(request, f'Добро пожаловать, {user.full_name}!')
            return redirect('home')  # перенаправляем на главную
        else:
            messages.error(request, 'Неверный телефон/email или пароль')
    
    return render(request, 'courses/login.html')

def logout_view(request):
    """Выход из системы"""
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['user_name']
    messages.success(request, 'Вы вышли из системы')
    return redirect('home')

def portfolio(request):
    """Страница портфолио"""
    # Получаем все активные работы
    works = Portfolio.objects.filter(is_active=True).order_by('-created_at')
    
    # Получаем все типы работ из отдельной таблицы WorkType
    from .models import WorkType
    work_types = WorkType.objects.all()
    
    # Типы авторов
    author_types = Portfolio.AUTHOR_TYPE_CHOICES
    
    context = {
        'works': works,
        'work_types': work_types,
        'author_types': author_types,
        'title': 'Портфолио работ'
    }
    return render(request, 'courses/portfolio.html', context)


@custom_login_required
def profile_view(request):
    """Личный кабинет пользователя - просмотр"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('login')
    
    from .models import Users
    user = get_object_or_404(Users, user_id=user_id)
    
    # Получаем или создаём профиль
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Получаем заявки пользователя
    applications = Applications.objects.filter(user=user).order_by('-application_date').select_related('course')
    
    context = {
        'title': 'Личный кабинет',
        'user': user,
        'profile': profile,
        'applications': applications,
    }
    return render(request, 'courses/profile.html', context)


@custom_login_required
def profile_edit(request):
    """Редактирование профиля"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('login')
    
    from .models import Users
    user = get_object_or_404(Users, user_id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        profile_form = ProfileExtendedForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Сохраняем пользователя
            user.full_name = user_form.cleaned_data['full_name']
            user.email = user_form.cleaned_data['email']
            user.phone = user_form.cleaned_data['phone']
            user.save()
            
            # Сохраняем профиль
            profile_form.save()
            
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = ProfileExtendedForm(instance=profile)
    
    context = {
        'title': 'Редактирование профиля',
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'profile': profile,
    }
    return render(request, 'courses/profile_edit.html', context)


@custom_login_required
def profile_applications(request):
    """История заявок пользователя"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('login')
    
    from .models import Users
    user = get_object_or_404(Users, user_id=user_id)
    applications = Applications.objects.filter(user=user).order_by('-application_date').select_related('course')
    
    context = {
        'title': 'Мои заявки',
        'applications': applications,
    }
    return render(request, 'courses/profile_applications.html', context)

@custom_login_required
def my_courses(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    from .models import ModuleProgress
    
    user = get_object_or_404(Users, user_id=user_id)
    progresses = CourseProgress.objects.filter(user=user).select_related('course')
    
    courses_data = []
    for progress in progresses:
        course = progress.course
        modules_progress = ModuleProgress.objects.filter(progress=progress).select_related('module')
        
        total_modules = modules_progress.count()
        completed_modules = modules_progress.filter(status='completed').count()
        percent = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0
        
        courses_data.append({
            'progress_id': progress.progress_id,
            'course': course,
            'format': progress.format,
            'status': progress.status,
            'modules_progress': modules_progress,
            'completed_modules': completed_modules,
            'total_modules': total_modules,
            'progress_percent': percent,
            'started_at': progress.started_at,
            'completed_at': progress.completed_at,
        })
    
    context = {
        'title': 'Мои курсы',
        'courses_data': courses_data,
    }
    return render(request, 'courses/my_courses.html', context)


@custom_login_required
def update_module_progress(request):
    """Обновление статуса модуля (AJAX запрос от преподавателя/админа)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    
    # Проверка прав: только администраторы и преподаватели
    # Проверяем сессию админа (настройте под свои роли)
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Недостаточно прав'}, status=403)
    
    try:
        data = json.loads(request.body)
        progress_id = data.get('progress_id')
        module_id = data.get('module_id')  # теперь используем module_id вместо module_key
        new_status = data.get('status')  # 'not_started', 'in_progress', 'completed'
        
        from .models import Module, ModuleProgress
        
        progress = CourseProgress.objects.get(progress_id=progress_id)
        module = Module.objects.get(module_id=module_id)
        
        # Обновляем или создаём ModuleProgress
        module_progress, created = ModuleProgress.objects.update_or_create(
            progress=progress,
            module=module,
            defaults={'status': new_status}
        )
        
        # Обновляем общий статус курса
        all_modules = ModuleProgress.objects.filter(progress=progress)
        total = all_modules.count()
        completed = all_modules.filter(status='completed').count()
        in_progress = all_modules.filter(status='in_progress').count()
        
        if total == 0:
            progress.status = 'not_started'
        elif completed == total:
            progress.status = 'completed'
            if not progress.completed_at:
                progress.completed_at = timezone.now()
        elif completed > 0 or in_progress > 0:
            progress.status = 'in_progress'
            if not progress.started_at:
                progress.started_at = timezone.now()
        else:
            progress.status = 'not_started'
        
        progress.last_accessed_at = timezone.now()
        progress.save()
        
        percent = int((completed / total) * 100) if total > 0 else 0
        
        return JsonResponse({
            'success': True,
            'new_status': progress.status,
            'progress_percent': percent,
            'completed_modules': completed,
            'total_modules': total,
            'message': f'Модуль "{module.title}" отмечен как {new_status}'
        })
        
    except CourseProgress.DoesNotExist:
        return JsonResponse({'error': 'Прогресс не найден'}, status=404)
    except Module.DoesNotExist:
        return JsonResponse({'error': 'Модуль не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@custom_login_required
def course_progress_detail(request, progress_id):
    """Детальный просмотр прогресса по курсу - используем модули из БД"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('login')
    
    from .models import Users, Module, ModuleProgress
    
    user = get_object_or_404(Users, user_id=user_id)
    progress = get_object_or_404(CourseProgress, progress_id=progress_id, user=user)
    
    course = progress.course
    
    # Получаем все модули курса
    modules = Module.objects.filter(course=course).order_by('order', 'module_id')
    
    # Получаем прогресс по каждому модулю
    modules_progress_dict = {
        mp.module_id: mp.status 
        for mp in ModuleProgress.objects.filter(progress=progress).select_related('module')
    }
    
    # Формируем список модулей с их статусами
    modules_with_status = []
    for module in modules:
        modules_with_status.append({
            'module_id': module.module_id,
            'title': module.title,
            'order': module.order,
            'status': modules_progress_dict.get(module.module_id, 'not_started'),
        })
    
    context = {
        'title': f'Прогресс: {course.title}',
        'progress': progress,
        'course': course,
        'modules': modules_with_status,
    }
    return render(request, 'courses/course_progress_detail.html', context)

@login_required
def save_theme(request):
    """Сохранение выбранной темы пользователя"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            theme = data.get('theme')
            user_id = request.session.get('user_id')
            
            if user_id and theme in ['light', 'dark']:
                user = Users.objects.get(user_id=user_id)
                user.theme_preference = theme
                user.save()
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False}, status=400)

def contacts(request):
    """Страница контактов"""
    context = {
        'title': 'Контакты - Учебный центр Леди'
    }
    return render(request, 'courses/contacts.html', context)

from .models import News

def news_list(request):
    """Страница со списком новостей и акций"""
    # Получаем активные новости, сортируем от новых к старым
    news_list = News.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now().date()
    ).order_by('-publish_date', '-created_at')
    
    # Разделяем на новости и акции
    news = news_list.filter(type='news')
    promos = news_list.filter(type='promo')
    events = news_list.filter(type='event')
    
    context = {
        'title': 'Новости и акции - Учебный центр Леди',
        'news': news,
        'promos': promos,
        'events': events,
        'has_content': news_list.exists()
    }
    return render(request, 'courses/news.html', context)


def news_detail(request, news_id):
    """Детальная страница новости/акции"""
    news_item = get_object_or_404(
        News, 
        news_id=news_id, 
        is_active=True,
        publish_date__lte=timezone.now().date()
    )
    
    # Получаем следующие/предыдущие новости для навигации
    prev_news = News.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now().date(),
        publish_date__lt=news_item.publish_date
    ).order_by('-publish_date').first()
    
    next_news = News.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now().date(),
        publish_date__gt=news_item.publish_date
    ).order_by('publish_date').first()
    
    context = {
        'title': f'{news_item.title} - Учебный центр Леди',
        'news_item': news_item,
        'prev_news': prev_news,
        'next_news': next_news,
    }
    return render(request, 'courses/news_detail.html', context)

def index(request):
    """Главная страница"""
    reviews = Review.objects.filter(status='approved', is_active=True).order_by('-created_at')
    context = {
        'reviews': reviews,
    }
    return render(request, 'courses/index.html', context)

@custom_login_required
def available_for_review(request):
    """Страница с курсами, на которые можно оставить отзыв"""
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, user_id=user_id)
    
    # Находим курсы, где пользователь прошел хотя бы один модуль и ещё не оставил отзыв
    progresses = CourseProgress.objects.filter(
        user=user,
        has_reviewed=False
    ).select_related('course')
    
    # Фильтруем только те, где есть хотя бы один пройденный модуль
    available_courses = []
    for progress in progresses:
        completed_modules = ModuleProgress.objects.filter(
            progress=progress,
            status='completed'
        ).count()
        
        if completed_modules > 0:
            # Считаем общий прогресс
            total_modules = Module.objects.filter(course=progress.course).count()
            percent = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0
            
            available_courses.append({
                'progress': progress,
                'course': progress.course,
                'progress_percent': percent,
                'completed_modules': completed_modules,
                'total_modules': total_modules,
            })
    
    context = {
        'title': 'Оставить отзыв',
        'available_courses': available_courses,
    }
    return render(request, 'courses/available_for_review.html', context)

@custom_login_required
def submit_review(request):
    """Сохранение отзыва пользователя"""
    if request.method != 'POST':
        return redirect('available_for_review')
    
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, user_id=user_id)
    
    course_id = request.POST.get('course_id')
    rating = request.POST.get('rating')
    text = request.POST.get('text')
    photo = request.FILES.get('photo')
    
    # Проверяем, что пользователь действительно проходил этот курс
    progress = CourseProgress.objects.filter(
        user=user,
        course_id=course_id,
        has_reviewed=False
    ).first()
    
    if not progress:
        messages.error(request, 'Вы не можете оставить отзыв на этот курс')
        return redirect('available_for_review')
    
    # Проверяем, что есть хотя бы один пройденный модуль
    completed_modules = ModuleProgress.objects.filter(
        progress=progress,
        status='completed'
    ).count()
    
    if completed_modules == 0:
        messages.error(request, 'Вы можете оставить отзыв только после прохождения хотя бы одного модуля курса')
        return redirect('available_for_review')
    
    # Создаём отзыв
    try:
        review = Review.objects.create(
            student_name=user.full_name,
            course=progress.course,
            text=text,
            rating=int(rating),
            photo=photo,
            is_active=False,  # На модерации
            status='pending'
        )
        
        # Отмечаем, что отзыв уже оставлен
        progress.has_reviewed = True
        progress.save()
        
        #СООБЩЕНИЕ УСПЕХА
        messages.success(request, 'Спасибо за отзыв! Он будет опубликован после проверки администратором.')
        
    except Exception as e:
        messages.error(request, f'Ошибка при сохранении отзыва: {str(e)}')
    
    return redirect('profile')