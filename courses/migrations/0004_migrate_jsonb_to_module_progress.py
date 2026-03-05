# courses/migrations/0004_migrate_jsonb_to_module_progress.py

from django.db import migrations
from django.db import connection


def migrate_jsonb_to_module_progress(apps, schema_editor):
    """
    Переносит данные из JSONB поля modules_progress в таблицу module_progress
    Использует прямой SQL-запрос для получения course_id
    """
    CourseProgress = apps.get_model('courses', 'CourseProgress')
    ModuleProgress = apps.get_model('courses', 'ModuleProgress')
    Module = apps.get_model('courses', 'Module')
    
    print("\n" + "="*60)
    print("🔄 МИГРАЦИЯ ДАННЫХ: JSONB → module_progress")
    print("="*60)
    
    migrated_count = 0
    error_count = 0
    skipped_count = 0
    
    # Получаем все прогрессы, у которых есть JSONB данные
    for progress in CourseProgress.objects.all():
        if not progress.modules_progress:
            skipped_count += 1
            continue
        
        # Получаем course_id через прямой SQL-запрос
        course_id = None
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT course_id FROM course_progress WHERE progress_id = %s",
                [progress.progress_id]
            )
            row = cursor.fetchone()
            if row:
                course_id = row[0]
        
        if not course_id:
            print(f"   ⚠️ Не удалось определить course_id для прогресса #{progress.progress_id}")
            error_count += 1
            continue
        
        print(f"\n📋 Прогресс #{progress.progress_id} (course_id={course_id})")
        print(f"   JSONB данные: {progress.modules_progress}")
        
        for module_key, status in progress.modules_progress.items():
            module = None
            
            # Вариант 1: ключ - это module_id
            if str(module_key).isdigit():
                module = Module.objects.filter(
                    module_id=int(module_key),
                    course_id=course_id
                ).first()
                if module:
                    print(f"   🔍 Найден по ID: {module_key} → {module.title}")
            
            # Вариант 2: ключ вида "module_1"
            if not module and str(module_key).startswith('module_'):
                try:
                    order_num = int(str(module_key).split('_')[1])
                    module = Module.objects.filter(
                        course_id=course_id,
                        order=order_num
                    ).first()
                    if module:
                        print(f"   🔍 Найден по order={order_num}: {module_key} → {module.title}")
                except (IndexError, ValueError):
                    pass
            
            # Вариант 3: поиск по названию
            if not module:
                search_title = str(module_key).replace('_', ' ').replace('module ', '')
                module = Module.objects.filter(
                    course_id=course_id,
                    title__icontains=search_title
                ).first()
                if module:
                    print(f"   🔍 Найден по названию '{search_title}': {module_key} → {module.title}")
            
            if module:
                ModuleProgress.objects.update_or_create(
                    progress=progress,
                    module=module,
                    defaults={'status': status}
                )
                migrated_count += 1
                print(f"   ✅ {module.title} → {status}")
            else:
                error_count += 1
                print(f"   ❌ НЕ НАЙДЕН модуль для ключа: {module_key}")
    
    print("\n" + "="*60)
    print(f"📊 ИТОГИ МИГРАЦИИ:")
    print(f"   ✅ Перенесено записей: {migrated_count}")
    print(f"   ❌ Ошибок (модуль не найден): {error_count}")
    print(f"   ⏭️ Пропущено (нет JSONB данных): {skipped_count}")
    print("="*60)


def reverse_migration(apps, schema_editor):
    """
    Откат: восстанавливает JSONB поле из module_progress
    """
    CourseProgress = apps.get_model('courses', 'CourseProgress')
    ModuleProgress = apps.get_model('courses', 'ModuleProgress')
    
    for progress in CourseProgress.objects.all():
        modules_progress = {}
        for mp in ModuleProgress.objects.filter(progress=progress).select_related('module'):
            module_key = f"module_{mp.module.order}" if mp.module.order else f"module_{mp.module.module_id}"
            modules_progress[module_key] = mp.status
        
        if modules_progress:
            progress.modules_progress = modules_progress
            progress.save()


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0003_add_module_models'),
    ]

    operations = [
        migrations.RunPython(
            migrate_jsonb_to_module_progress,
            reverse_code=reverse_migration
        ),
        migrations.RemoveField(
            model_name='courseprogress',
            name='modules_progress',
        ),
    ]