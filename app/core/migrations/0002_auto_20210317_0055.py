# Generated by Django 3.1.6 on 2021-03-17 03:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='commenter',
            field=models.ForeignKey(help_text='Autor do comentário.', on_delete=django.db.models.deletion.CASCADE, related_name='comments', related_query_name='comment', to='core.member', verbose_name='comentarista'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='note',
            field=models.ForeignKey(help_text='Anotação comentada.', on_delete=django.db.models.deletion.CASCADE, related_name='comments', related_query_name='comment', to='core.note', verbose_name='anotação'),
        ),
    ]