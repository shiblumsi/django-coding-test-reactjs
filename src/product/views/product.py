from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from product.models import Product, ProductVariant, ProductVariantPrice, Variant


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(generic.TemplateView):
    template_name = 'products/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ListProductView, self).get_context_data(**kwargs)

        # Retrieve form data
        title = self.request.GET.get('title')
        variant = self.request.GET.get('variant')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')

        # Query products based on filters
        products = Product.objects.all()

        if title:
            products = products.filter(title__icontains=title)
        
        if date:
                products = products.filter(created_at__date=date)

        product_variant_prices = []

        for product in products:
            prices = ProductVariantPrice.objects.filter(product=product)

            # Apply additional filters based on form data
            if variant:
                prices = prices.filter(product_variant_one__icontains=variant)

            if price_from:
                prices = prices.filter(price__gte=float(price_from))

            if price_to:
                prices = prices.filter(price__lte=float(price_to))

            

            product_variant_prices.append({'product': product, 'prices': prices})

        # Paginate the results
        page = self.request.GET.get('page', 1)
        paginator = Paginator(product_variant_prices, self.paginate_by)
        try:
            product_variant_prices = paginator.page(page)
        except PageNotAnInteger:
            product_variant_prices = paginator.page(1)
        except EmptyPage:
            product_variant_prices = paginator.page(paginator.num_pages)

        variants = Variant.objects.all()
        print(variants)
        product_variants = ProductVariant.objects.all()
        context['variants'] = variants
        context['product_variants'] = product_variants
        context['product_variant_prices'] = product_variant_prices
        context['total_products'] = paginator.count

        return context
    