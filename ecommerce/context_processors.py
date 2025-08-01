from django.urls import resolve
from ecommerce.models import Product, Category

def breadcrumbs(request):
    breadcrumbs = [{'name': 'Home', 'url': '/'}]

    try:
        match = resolve(request.path_info)
    except:
        return {}

    if match.url_name == 'products_by_category':
        cat_id = match.kwargs.get('pk')
        category = Category.objects.filter(pk=cat_id).first()
        if category:
            breadcrumbs.append({'name': category.name, 'url': request.path})

    elif match.url_name == 'product_detail':
        product_id = match.kwargs.get('pk')
        product = Product.objects.select_related('category').filter(pk=product_id).first()
        if product:
            breadcrumbs.append({'name': product.category.name, 'url': f"/category/{product.category.pk}/"})
            breadcrumbs.append({'name': product.name, 'url': request.path})

    return {'breadcrumbs': breadcrumbs}
