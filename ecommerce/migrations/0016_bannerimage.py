# Generated manually for adding BannerImage model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0015_add_category_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="BannerImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(help_text="Banner image for carousel", upload_to="banners/")),
                ("title", models.CharField(blank=True, help_text="Optional title/alt text", max_length=200)),
                ("link_url", models.URLField(blank=True, help_text="Optional link URL when banner is clicked", null=True)),
                ("is_active", models.BooleanField(default=True, help_text="Show this banner in carousel")),
                ("order", models.IntegerField(default=0, help_text="Display order (lower numbers first)")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Banner Image",
                "verbose_name_plural": "Banner Images",
                "ordering": ["order", "-created_at"],
            },
        ),
    ]

