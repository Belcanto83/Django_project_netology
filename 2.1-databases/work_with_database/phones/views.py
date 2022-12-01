from django.shortcuts import render, redirect

from phones.models import Phone


def index(request):
    return redirect('catalog')


def show_catalog(request, sort='name'):
    template = 'catalog.html'

    reverse = False
    sort_param = request.GET.get('sort', sort)
    if sort_param == 'min_price':
        sort_field = 'price'
    elif sort_param == 'max_price':
        sort_field = 'price'
        reverse = True
    else:
        sort_field = sort_param

    if not reverse:
        sorted_phones = Phone.objects.all().order_by(sort_field)
    else:
        sorted_phones = Phone.objects.all().order_by(f'-{sort_field}')

    context = {'phones': sorted_phones}
    return render(request, template, context)


def show_product(request, slug):
    template = 'product.html'
    phone = Phone.objects.get(slug=slug)
    context = {'phone': phone}
    return render(request, template, context)
