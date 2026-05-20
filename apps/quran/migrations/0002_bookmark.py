from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quran', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(
                    choices=[('gold', 'Gold'), ('green', 'Green'), ('blue', 'Blue'), ('red', 'Red')],
                    default='gold',
                    max_length=10,
                )),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bookmarks',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('verse', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bookmarks',
                    to='quran.verse',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='bookmark',
            constraint=models.UniqueConstraint(fields=['user', 'verse'], name='unique_user_verse_bookmark'),
        ),
        migrations.AddIndex(
            model_name='bookmark',
            index=models.Index(fields=['user', 'created_at'], name='quran_bookmark_user_created_idx'),
        ),
    ]
