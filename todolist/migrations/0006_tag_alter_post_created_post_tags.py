# Generated by Django 4.2.1 on 2023-06-08 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0005_post_todolist_po_created_037914_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(related_name='posts', to='todolist.tag'),
        ),
    ]
