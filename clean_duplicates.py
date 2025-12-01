from app.models import Category
from django.db.models import Count

# Find duplicates
duplicates = Category.objects.values('name', 'user').annotate(count=Count('id')).filter(count__gt=1)

for dup in duplicates:
    # Get all categories with same name and user, order by id, keep the first, delete the rest
    cats = Category.objects.filter(name=dup['name'], user=dup['user']).order_by('id')[1:]
    for cat in cats:
        print(f"Deleting duplicate category: {cat}")
        cat.delete()

print("Duplicates cleaned.")
