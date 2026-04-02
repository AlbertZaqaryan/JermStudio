from django.db import migrations


def seed_sitecontent_languages(apps, schema_editor):
    SiteContent = apps.get_model("main", "SiteContent")
    for code in ("en", "hy", "ru"):
        SiteContent.objects.get_or_create(language=code)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_sitecontent_booking_error_text_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_sitecontent_languages, migrations.RunPython.noop),
    ]
