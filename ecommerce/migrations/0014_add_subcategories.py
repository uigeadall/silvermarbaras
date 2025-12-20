# Generated manually for adding sub-categories support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0013_blogpost_video_file_alter_blogpost_video_url"),
    ]

    operations = [
        # First, remove the unique constraint on slug (change unique=True to unique=False)
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(blank=True, unique=False),
        ),
        # Add parent field
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="Select a parent category to make this a sub-category",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subcategories",
                to="ecommerce.category",
            ),
        ),
        # Add unique_together constraint for slug and parent
        migrations.AlterUniqueTogether(
            name="category",
            unique_together={("slug", "parent")},
        ),
    ]

