# Generated by Django 2.2.4 on 2019-09-02 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flash_cards', '0004_attempt_lesson_lessonentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='attempt',
            name='lesson_entry',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='flash_cards.LessonEntry'),
            preserve_default=False,
        ),
    ]