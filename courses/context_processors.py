from .models import Users, Profile

def user_profile(request):
    """Добавляет данные пользователя и профиля в контекст всех страниц"""
    context = {}
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            user = Users.objects.get(user_id=user_id)
            profile, created = Profile.objects.get_or_create(user=user)
            context['user'] = user
            context['profile'] = profile
        except Users.DoesNotExist:
            pass
    
    return context