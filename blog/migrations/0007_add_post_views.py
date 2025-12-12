from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0006_moderationreport_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="views",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
