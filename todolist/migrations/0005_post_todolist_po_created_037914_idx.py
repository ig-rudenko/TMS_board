# Generated by Django 4.2.1 on 2023-06-06 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0004_alter_comment_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['created'], name='todolist_po_created_037914_idx'),
        ),
    ]
