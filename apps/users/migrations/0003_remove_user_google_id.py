from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_is_staff_user_is_superuser_user_password_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="google_id",
        ),
    ]
