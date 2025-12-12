from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0018_rename_used_words_gamelobbychallenge_letters_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="public_profile",
            field=models.BooleanField(default=False),
        ),
    ]
