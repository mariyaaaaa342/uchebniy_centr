from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import Applications, Teachers, Courses, Users, Portfolio
import json

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
def register(request):
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