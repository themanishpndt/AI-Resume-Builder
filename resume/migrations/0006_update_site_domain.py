"""
Fix Site domain for production
"""
from django.db import migrations


def update_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site = Site.objects.get(id=1)
    site.domain = 'ai-resume-builder-6jan.onrender.com'
    site.name = 'AI Resume Builder'
    site.save()
    print(f"✅ Updated Site: {site.domain} - {site.name}")


def revert_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site = Site.objects.get(id=1)
    site.domain = 'example.com'
    site.name = 'example.com'
    site.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0005_coverletter_template'),  # Latest migration
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site_domain, revert_site_domain),
    ]
