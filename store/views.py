import decimal
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views import View
from .forms import (
    RegistrationForm,
    AddressForm,
    NewsCommentForm,
    NewsCommentEditForm,
    ProductReviewForm,
    ProductReviewEditForm,
)
from .models import (
    Address,
    Cart,
    Category,
    Order,
    Product,
    ProductReview,
    News,
    NewsComment,
    Wishlist,
)

# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    context = {
        'categories': categories,
        'products': products,
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'store/index.html', context)


def about(request):
    context = {
        'title': 'О нас',
    }
    return render(request, 'store/about.html', context)


def news_list(request):
    news_list = News.objects.filter(is_published=True).order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(news_list, 6) 
    
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    
    recent_news = News.objects.filter(is_published=True).order_by('-created_at')[:5]
    
    context = {
        'news': news,
        'recent_news': recent_news,
        'page_obj': news,  
    }
    return render(request, 'store/news_list.html', context)


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    news.increase_views()
    
    recent_news = News.objects.filter(
        is_published=True
    ).exclude(id=news.id).order_by('-created_at')[:5]
    
    comments = news.comments.filter(is_active=True).order_by('-created_at')
    
    comment_form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = NewsCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.news = news
                comment.user = request.user
                comment.save()
                messages.success(request, "Ваш комментарий успешно добавлен!")
                return redirect('store:news_detail', slug=news.slug)
        else:
            comment_form = NewsCommentForm()
    
    context = {
        'news': news,
        'recent_news': recent_news,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'store/news_detail.html', context)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(NewsComment, id=comment_id)
    if request.user != comment.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = NewsCommentEditForm(request.POST, instance=comment)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.is_edited = True
            updated.sentiment_analyzed = False  
            updated.save()
            
            return JsonResponse({
                'status': 'ok',
                'content': updated.content,
                'updated_at': updated.updated_at.strftime('%d.%m.%Y %H:%M'),
                'is_edited': True,
                'sentiment_label': updated.sentiment_label,
                'sentiment_analyzed': updated.sentiment_analyzed,
                'sentiment_score': updated.sentiment_score,
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Ошибка валидации'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'}, status=400)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(NewsComment, id=comment_id)
    if request.user != comment.user and not request.user.is_staff:
        messages.error(request, "Вы не можете удалить чужой комментарий.")
        return redirect('store:news_detail', slug=comment.news.slug)
    
    news_slug = comment.news.slug
    comment.delete()
    messages.success(request, "Комментарий удалён.")
    return redirect('store:news_detail', slug=news_slug)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)[:4]

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    reviews = ProductReview.objects.filter(product=product, is_active=True).order_by('-created_at')

    review_form = ProductReviewForm()
    can_review = False
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = ProductReview.objects.get(user=request.user, product=product)
        except ProductReview.DoesNotExist:
            can_review = True

    if request.method == 'POST' and request.user.is_authenticated and can_review:
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.user = request.user
            new_review.product = product
            new_review.save()
            messages.success(request, "Спасибо! Ваш отзыв успешно добавлен.")
            return redirect('store:product-detail', slug=product.slug) 
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")

    context = {
        'product': product,
        'related_products': related_products,
        'is_in_wishlist': is_in_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
        'avg_rating': avg_rating,
        'reviews': reviews,
        'review_form': review_form,
        'can_review': can_review,
        'user_review': user_review,
    }
    return render(request, 'store/detail.html', context)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    if request.user != review.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ProductReviewEditForm(request.POST, instance=review)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.is_edited = True
            updated.sentiment_analyzed = False
            updated.save()
            
            rating_stars = ''.join([
                '<i class="fas fa-star text-warning small"></i>' if i <= updated.rating else '<i class="far fa-star text-warning small"></i>'
                for i in range(1, 6)
            ])
            
            return JsonResponse({
                'status': 'ok',
                'content': updated.comment,
                'rating': updated.rating,
                'rating_stars': rating_stars,
                'updated_at': updated.updated_at.strftime('%d.%m.%Y %H:%M'),
                'is_edited': True,
                'sentiment_label': updated.sentiment_label,    
                'sentiment_analyzed': updated.sentiment_analyzed, 
                'sentiment_score': updated.sentiment_score,
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Ошибка валидации', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'}, status=400)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    if request.user != review.user and not request.user.is_staff:
        messages.error(request, "Вы не можете удалить чужой отзыв.")
        return redirect('store:product-detail', slug=review.product.slug)
    
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Отзыв удалён.")
    return redirect('store:product-detail', slug=product_slug)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products_list = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)

    sort = request.GET.get('sort', 'default')
    if sort == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort == 'newest':
        products_list = products_list.order_by('-created_at')

    paginator = Paginator(products_list, 6)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'user_wishlist_ids': user_wishlist_ids,  
    }
    return render(request, 'store/category_products.html', context)


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:home') 
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "Добавлен новый адрес")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Адрес удален")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    if request.method == 'GET':
        product_id = request.GET.get('prod_id')
        quantity = int(request.GET.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            messages.error(request, f"Недостаточно товара на складе. Доступно: {product.stock} шт.")
            return redirect('store:detail', slug=product.slug)

        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock < new_quantity:
                messages.error(request, f"Нельзя добавить больше {product.stock} шт. товара.")
                return redirect('store:detail', slug=product.slug)
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Товар добавлен в корзину")
        return redirect('store:cart')

@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    amount = decimal.Decimal(0)
    for item in cart_products:
        amount += item.product.price * item.quantity

    nds_amount = amount * decimal.Decimal('20') / decimal.Decimal('120')
    nds_amount = nds_amount.quantize(decimal.Decimal('0.00'))
    shipping_amount = decimal.Decimal(0)  
    total_amount = amount                  

    addresses = Address.objects.filter(user=user).exclude(locality='Самовывоз')

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'nds_amount': nds_amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Товар убран из корзины")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')

@login_required
def update_cart_quantity(request, cart_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity < 1:
                new_quantity = 1
            cart_item.quantity = new_quantity
            cart_item.save()

            user_cart = Cart.objects.filter(user=request.user)
            amount = sum(item.product.price * item.quantity for item in user_cart)
            nds_amount = amount * decimal.Decimal('20') / decimal.Decimal('120')
            nds_amount = nds_amount.quantize(decimal.Decimal('0.00'))
            shipping_amount = decimal.Decimal(0)
            total_amount = amount

            item_total = cart_item.product.price * cart_item.quantity

            return JsonResponse({
                'status': 'ok',
                'item_total': float(item_total),
                'amount': float(amount),
                'nds_amount': float(nds_amount),
                'shipping_amount': float(shipping_amount),
                'total_amount': float(total_amount),
                'quantity': cart_item.quantity,
            })
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'}, status=400)

@login_required
def toggle_wishlist(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            if not created:
                wishlist_item.delete()
                is_in_wishlist = False
                message = "Товар удалён из избранного"
            else:
                is_in_wishlist = True
                message = "Товар добавлен в избранное"
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({
                'status': 'ok',
                'is_in_wishlist': is_in_wishlist,
                'message': message,
                'wishlist_count': wishlist_count
            })
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Недопустимый запрос'}, status=400)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, product_id):
    if request.method == 'POST':
        deleted_count, _ = Wishlist.objects.filter(
            user=request.user, 
            product_id=product_id
        ).delete()
        
        if deleted_count:
            messages.success(request, "Товар удалён из избранного.")
        else:
            messages.warning(request, "Товар не найден в избранном.")
    
    return redirect('store:wishlist')

@login_required
def checkout(request):
    user = request.user
    address_param = request.GET.get('address')

    if address_param == 'pickup':
        pickup_address, created = Address.objects.get_or_create(
            user=user,
            locality='Самовывоз',
            city='Курск',
            state='Магазин'
        )
        address = pickup_address
    else:
        address = get_object_or_404(Address, id=address_param, user=user)

    cart = Cart.objects.filter(user=user)
    if not cart.exists():
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('store:cart')

    errors = []
    for cart_item in cart:
        if cart_item.quantity > cart_item.product.stock:
            errors.append({
                'title': cart_item.product.title,
                'requested': cart_item.quantity,
                'available': cart_item.product.stock
            })
    if errors:
        for err in errors:
            messages.error(
                request,
                f'Товара "{err["title"]}" недостаточно на складе. '
                f'Доступно: {err["available"]} шт., запрошено: {err["requested"]} шт.'
            )
        return redirect('store:cart')

    for cart_item in cart:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

        Order.objects.create(
            user=user,
            address=address,
            product=cart_item.product,
            quantity=cart_item.quantity
        )
    cart.delete()

    messages.success(request, "Заказ успешно оформлен!")
    return redirect('store:orders')

@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})

