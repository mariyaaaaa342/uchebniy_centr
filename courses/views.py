from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, ProfileExtendedForm
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .forms import RegistrationForm
from .models import Applications, Teachers, Courses, Users, Portfolio, Profile, CourseProgress
import json

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def course_list(request):
    courses = Courses.objects.filter(status='active')
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
                status='new'
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
#def register(request):
    """Страница регистрации нового пользователя"""
    if request.method == 'POST':
        # Получаем данные из формы
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Проверяем, что все поля заполнены
        if not all([full_name, phone, email, password]):
            messages.error(request, 'Заполните все поля')
            return render(request, 'courses/register.html')
        
        # Проверяем, что пароли совпадают
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'courses/register.html')
        
        # Проверяем, существует ли пользователь с таким телефоном или email
        if Users.objects.filter(phone=phone).exists():
            messages.error(request, 'Пользователь с таким номером телефона уже существует')
            return render(request, 'courses/register.html')
        
        if Users.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'courses/register.html')
        
        # Создаём нового пользователя
        user = Users.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            password_hash=make_password(password),  # хешируем пароль
            registration_date=timezone.now(),
            is_verified=False,
            theme_preference='light'
        )
        
        messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
        return redirect('login')
    
    return render(request, 'courses/register.html')
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
    """Мои курсы - отслеживание прогресса обучения"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('login')
    
    from .models import Users, CourseProgress, Courses
    user = get_object_or_404(Users, user_id=user_id)
    
    # Получаем все прогрессы пользователя
    progresses = CourseProgress.objects.filter(user=user).select_related('course')
    
    # Расширяем информацию о курсах
    courses_data = []
    for progress in progresses:
        course = progress.course
        modules_progress = progress.modules_progress if progress.modules_progress else {}
        
        # Разбираем программу курса на модули
        course_program = course.course_program if course.course_program else ''
        modules = parse_course_program_to_modules(course_program)
        
        # Обогащаем модули статусами из JSONB
        for module in modules:
            module_key = module['key']
            if module_key in modules_progress:
                module['status'] = modules_progress[module_key]
            else:
                module['status'] = 'not_started'
        
        # Рассчитываем общий прогресс
        if modules:
            completed = sum(1 for m in modules if m['status'] == 'completed')
            total = len(modules)
            percent = int((completed / total) * 100)
        else:
            completed = 0
            total = 0
            percent = 0
        
        courses_data.append({
            'progress_id': progress.progress_id,
            'course': course,
            'format': progress.format,
            'status': progress.status,
            'modules': modules,
            'completed_modules': completed,
            'total_modules': total,
            'progress_percent': percent,
            'started_at': progress.started_at,
            'completed_at': progress.completed_at,
            'last_accessed_at': progress.last_accessed_at,
        })
    
    context = {
        'title': 'Мои курсы',
        'courses_data': courses_data,
    }
    return render(request, 'courses/my_courses.html', context)


def parse_course_program_to_modules(course_program):
    """Парсит текст программы курса в список модулей"""
    modules = []
    
    if not course_program:
        return modules
    
    # Ищем строки, начинающиеся с цифры и точки (например "1. Введение")
    import re
    lines = course_program.split('\n')
    module_counter = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Проверяем, похоже ли на заголовок модуля
        if re.match(r'^\d+[\.\)]', line) or line[0].isdigit() or len(line) < 50:
            module_key = f'module_{module_counter}'
            modules.append({
                'key': module_key,
                'title': line[:100],  # Ограничиваем длину
                'description': line
            })
            module_counter += 1
        elif modules and len(modules[-1]['description']) < 200:
            # Добавляем продолжение к последнему модулю
            modules[-1]['description'] += ' ' + line
    
    # Если не нашли модулей по номерам, разбиваем на абзацы
    if not modules:
        paragraphs = [p.strip() for p in course_program.split('\n\n') if p.strip()]
        for i, para in enumerate(paragraphs[:20], 1):  # Максимум 20 модулей
            modules.append({
                'key': f'module_{i}',
                'title': para[:50] + ('...' if len(para) > 50 else ''),
                'description': para
            })
    
    return modules


@custom_login_required
def update_module_progress(request):
    """Обновление статуса модуля (AJAX запрос от преподавателя/админа)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    
    # Проверка прав: только администраторы и преподаватели
    # Здесь нужно проверить роль пользователя
    # Пока упрощённо - проверяем сессию админа
    
    try:
        data = json.loads(request.body)
        progress_id = data.get('progress_id')
        module_key = data.get('module_key')
        status = data.get('status')  # 'not_started', 'in_progress', 'completed'
        
        progress = CourseProgress.objects.get(progress_id=progress_id)
        
        # Обновляем JSONB поле
        if not progress.modules_progress:
            progress.modules_progress = {}
        
        progress.modules_progress[module_key] = status
        
        # Обновляем общий статус курса
        modules_statuses = list(progress.modules_progress.values())
        if all(s == 'completed' for s in modules_statuses):
            progress.status = 'completed'
            progress.completed_at = timezone.now()
        elif any(s in ['in_progress', 'completed'] for s in modules_statuses):
            progress.status = 'in_progress'
            if not progress.started_at:
                progress.started_at = timezone.now()
        else:
            progress.status = 'not_started'
        
        progress.last_accessed_at = timezone.now()
        progress.save()
        
        return JsonResponse({
            'success': True,
            'new_status': progress.status,
            'message': 'Прогресс обновлён'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@custom_login_required
def course_progress_detail(request, progress_id):
    """Детальный просмотр прогресса по курсу"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('login')
    
    from .models import Users, CourseProgress
    user = get_object_or_404(Users, user_id=user_id)
    progress = get_object_or_404(CourseProgress, progress_id=progress_id, user=user)
    
    course = progress.course
    modules_progress = progress.modules_progress if progress.modules_progress else {}
    
    # Парсим программу курса
    modules = parse_course_program_to_modules(course.course_program)
    
    for module in modules:
        module_key = module['key']
        module['status'] = modules_progress.get(module_key, 'not_started')
    
    context = {
        'title': f'Прогресс: {course.title}',
        'progress': progress,
        'course': course,
        'modules': modules,
    }
    return render(request, 'courses/course_progress_detail.html', context)