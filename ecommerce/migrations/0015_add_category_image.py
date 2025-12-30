# Generated manually for adding image field to Category model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0014_add_subcategories"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image",
            field=models.ImageField(blank=True, help_text="Image for sub-category display", null=True, upload_to="categories/"),
        ),
    ]

