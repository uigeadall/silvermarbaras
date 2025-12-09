from django.core.management.base import BaseCommand
from ecommerce.models import BlogPost


class Command(BaseCommand):
    help = 'Create initial blog posts'

    def handle(self, *args, **options):
        blog_posts_data = [
            {
                'title': 'Take Care of Your Silver',
                'slug': 'take-care-of-your-silver',
                'excerpt': 'Learn essential tips to keep your silver jewelry looking beautiful and prevent tarnishing.',
                'content': '''<h2>How to Take Care of Your Silver Jewelry</h2>

<p>Silver jewelry is timeless and elegant, but it requires proper care to maintain its beautiful shine. Here are essential tips to keep your silver pieces looking their best:</p>

<h3>1. Regular Cleaning</h3>
<p>Clean your silver jewelry regularly with a soft, lint-free cloth. For deeper cleaning, use a specialized silver polishing cloth or a mild soap solution. Gently rub the surface to remove tarnish and restore shine.</p>

<h3>2. Proper Storage</h3>
<p>Store silver jewelry in a cool, dry place away from sunlight. Keep pieces separated to prevent scratching. Use anti-tarnish strips or store in airtight containers to minimize exposure to air and moisture.</p>

<h3>3. Avoid Harsh Chemicals</h3>
<p>Remove silver jewelry before swimming, showering, or using household cleaners. Chlorine, bleach, and other chemicals can damage silver and cause discoloration.</p>

<h3>4. Wear It Regularly</h3>
<p>Surprisingly, wearing your silver jewelry regularly can help prevent tarnishing. The natural oils in your skin create a protective barrier. However, always remove jewelry before exercising or doing manual work.</p>

<h3>5. Professional Cleaning</h3>
<p>For heavily tarnished pieces or valuable items, consider professional cleaning. Jewelers have specialized tools and solutions to restore silver without damaging delicate details.</p>

<p>By following these simple care tips, your silver jewelry will maintain its luster and beauty for years to come!</p>''',
                'order': 1,
            },
            {
                'title': 'Why the Silver Gets Dark',
                'slug': 'why-the-silver-gets-dark',
                'excerpt': 'Understanding the science behind silver tarnishing and how to prevent it.',
                'content': '''<h2>Why Does Silver Get Dark? Understanding Tarnishing</h2>

<p>Have you ever wondered why your beautiful silver jewelry turns dark over time? This process, called tarnishing, is a natural chemical reaction. Let's explore why it happens and how to prevent it.</p>

<h3>What Causes Silver to Tarnish?</h3>
<p>Silver tarnishes when it reacts with sulfur compounds in the air. This reaction forms silver sulfide, a dark layer on the surface of your jewelry. The main culprits include:</p>

<ul>
<li><strong>Air Pollution:</strong> Industrial areas and cities have higher sulfur dioxide levels, accelerating tarnishing</li>
<li><strong>Humidity:</strong> Moist air speeds up the chemical reaction</li>
<li><strong>Household Items:</strong> Foods like eggs, onions, and rubber contain sulfur compounds</li>
<li><strong>Perfumes and Lotions:</strong> Some personal care products contain chemicals that react with silver</li>
<li><strong>Chlorine:</strong> Found in swimming pools and household cleaners</li>
</ul>

<h3>The Science Behind Tarnishing</h3>
<p>When silver comes into contact with hydrogen sulfide (H₂S) in the air, a chemical reaction occurs:</p>
<p><strong>2Ag + H₂S → Ag₂S + H₂</strong></p>
<p>This creates silver sulfide (Ag₂S), which appears as a dark, grayish-black film on the surface.</p>

<h3>How to Prevent Tarnishing</h3>
<ul>
<li>Store silver in airtight containers with anti-tarnish strips</li>
<li>Keep jewelry away from humidity and moisture</li>
<li>Remove jewelry before cooking, cleaning, or swimming</li>
<li>Wipe pieces with a soft cloth after wearing</li>
<li>Use silica gel packets in storage containers to absorb moisture</li>
</ul>

<h3>Removing Tarnish</h3>
<p>If your silver has already tarnished, don't worry! You can restore its shine using:</p>
<ul>
<li>Silver polishing cloths</li>
<li>Baking soda and aluminum foil method</li>
<li>Commercial silver cleaners</li>
<li>Professional cleaning for valuable pieces</li>
</ul>

<p>Remember, tarnishing is completely normal and reversible. With proper care, your silver jewelry can maintain its beautiful appearance for generations!</p>''',
                'order': 2,
            },
            {
                'title': 'How to Choose Your Size',
                'slug': 'how-to-choose-your-size',
                'excerpt': 'A comprehensive guide to finding the perfect ring size for comfortable wear.',
                'content': '''<h2>How to Choose Your Ring Size: A Complete Guide</h2>

<p>Finding the perfect ring size is crucial for comfort and style. Whether you're shopping for yourself or someone else, this guide will help you determine the correct size.</p>

<h3>Method 1: Measure at Home</h3>
<p><strong>Using a String or Paper Strip:</strong></p>
<ol>
<li>Wrap a piece of string or paper around the base of your finger</li>
<li>Mark where the string overlaps</li>
<li>Measure the length in millimeters</li>
<li>Use a ring size chart to convert to your size</li>
</ol>

<p><strong>Best Time to Measure:</strong> Measure your finger at the end of the day when it's at its largest size. Avoid measuring when your hands are cold, as fingers shrink in cold temperatures.</p>

<h3>Method 2: Use an Existing Ring</h3>
<p>If you have a ring that fits perfectly:</p>
<ol>
<li>Place it on a ring sizer or measure the inside diameter</li>
<li>Compare with a ring size chart</li>
<li>Note which finger the ring fits (sizes vary between fingers)</li>
</ol>

<h3>Ring Size Chart</h3>
<p>Common ring sizes range from 3 to 13 for women and 6 to 14 for men. European sizes typically range from 44 to 70. Here's a quick reference:</p>

<ul>
<li><strong>Size 5:</strong> Inside diameter 15.7mm, Circumference 49.3mm</li>
<li><strong>Size 6:</strong> Inside diameter 16.5mm, Circumference 51.9mm</li>
<li><strong>Size 7:</strong> Inside diameter 17.3mm, Circumference 54.4mm</li>
<li><strong>Size 8:</strong> Inside diameter 18.1mm, Circumference 56.9mm</li>
<li><strong>Size 9:</strong> Inside diameter 19.0mm, Circumference 59.5mm</li>
</ul>

<h3>Important Tips</h3>
<ul>
<li><strong>Finger Size Varies:</strong> Your ring finger size differs from your index or middle finger</li>
<li><strong>Temperature Matters:</strong> Fingers are smaller in cold weather and larger in warm weather</li>
<li><strong>Time of Day:</strong> Fingers tend to be slightly larger in the evening</li>
<li><strong>Wide Bands:</strong> If choosing a wide band (over 6mm), consider going up half a size</li>
<li><strong>Knuckle Size:</strong> Ensure the ring can pass over your knuckle comfortably</li>
</ul>

<h3>Professional Sizing</h3>
<p>For the most accurate measurement, visit a jeweler. They use professional ring sizers and can account for factors like knuckle size and band width.</p>

<h3>International Size Conversion</h3>
<p>Ring sizes vary by country. Make sure to check if you're using US, UK, European, or Asian sizing systems when shopping online.</p>

<p>Remember: It's better to have a ring slightly loose than too tight. You can always use ring adjusters or resize professionally if needed!</p>''',
                'order': 3,
            },
        ]

        for post_data in blog_posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults=post_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created blog post: {post.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Blog post already exists: {post.title}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Blog posts created successfully!'))

