from django.db import migrations, models


class Migration(migrations.Migration):
    """Backfill the ``BaseModel`` mixin fields that the stale ``0001_initial``
    migration never created (it predates ``FriendLink`` inheriting
    ``TimestampMixin`` / ``SoftDeleteMixin``).

    Adds ``created_time`` / ``updated_time`` (non-null, auto-managed) and
    ``is_deleted`` (default ``False``, indexed) so the table matches the
    current model and inserts stop failing with "no column named created_time".
    """

    dependencies = [
        ('friendlink', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendlink',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='friendlink',
            name='updated_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AddField(
            model_name='friendlink',
            name='is_deleted',
            field=models.BooleanField(
                db_index=True, default=False, verbose_name='是否删除'
            ),
        ),
    ]
