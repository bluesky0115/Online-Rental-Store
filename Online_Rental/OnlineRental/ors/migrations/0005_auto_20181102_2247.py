# Generated by Django 2.1.2 on 2018-11-02 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ors', '0004_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='roll_no',
            field=models.CharField(default='000000000', help_text='Unique identifier for the student', max_length=12),
        ),
    ]