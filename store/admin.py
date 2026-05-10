from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Address, Category, Product, ProductReview, Cart, Order, News, NewsComment

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'stock', 'product_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'category', 'stock', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'category__title', 'short_description')
    prepopulated_fields = {"slug": ("title",)}

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user__username', 'product__title')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'ordered_date')
    list_editable = ('quantity', 'status')
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user__username', 'product__title')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'is_published', 'views')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    list_per_page = 20
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'short_description', 'content', 'image', 'author')
        }),
        ('Настройки публикации', {
            'fields': ('is_published', 'views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'news', 'created_at', 'is_active', 'sentiment_preview')
    list_filter = ('is_active', 'created_at', 'sentiment_label', 'sentiment_analyzed')
    search_fields = ('content', 'user__username', 'news__title')
    readonly_fields = ('sentiment_label', 'sentiment_score', 'sentiment_analyzed', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    actions = ['activate_comments', 'deactivate_comments']

    def sentiment_preview(self, obj):
        if not obj.sentiment_analyzed:
            return "⏳ не проанализирован"
        if obj.sentiment_label == 'POSITIVE':
            return "🟢 положительный"
        elif obj.sentiment_label == 'NEGATIVE':
            return "🔴 негативный"
        return "⚪ нейтральный"
    sentiment_preview.short_description = "Тональность"

    def activate_comments(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} комментариев')
    activate_comments.short_description = 'Активировать выбранные комментарии'

    def deactivate_comments(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} комментариев')
    deactivate_comments.short_description = 'Деактивировать выбранные комментарии'

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'sentiment_preview', 'created_at', 'is_active')
    list_filter = ('rating', 'sentiment_label', 'sentiment_analyzed', 'is_active')
    search_fields = ('user__username', 'product__title', 'comment')
    readonly_fields = ('sentiment_label', 'sentiment_score', 'sentiment_analyzed', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    actions = ['approve_reviews', 'disapprove_reviews']

    def sentiment_preview(self, obj):
        if not obj.sentiment_analyzed:
            return "⏳ не проанализирован"
        if obj.sentiment_label == 'POSITIVE':
            return "🟢 положительный"
        elif obj.sentiment_label == 'NEGATIVE':
            return "🔴 негативный"
        return "⚪ нейтральный"
    sentiment_preview.short_description = "Тональность"

    def approve_reviews(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} отзывов")
    approve_reviews.short_description = "Активировать выбранные отзывы"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {queryset.count()} отзывов")
    disapprove_reviews.short_description = "Деактивировать выбранные отзывы"

class CustomAdminSite(AdminSite):
    site_header = 'Ювелирный магазин – Административная панель'
    site_title = 'Админ-панель'
    index_title = 'Управление магазином'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['stats'] = {
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
            'total_orders': Order.objects.count(),
            'total_users': User.objects.count(),
            'total_news': News.objects.count(),
            'products_no_image': Product.objects.filter(product_image='').count(),
            'inactive_products': Product.objects.filter(is_active=False).count(),
            'recent_orders': Order.objects.select_related('user', 'product').order_by('-ordered_date')[:5],
            'popular_products': Product.objects.filter(order__isnull=False)
                                    .annotate(order_count=Count('order'))
                                    .order_by('-order_count')[:5],
            'recent_news': News.objects.filter(is_published=True).order_by('-created_at')[:5],
        }
        return super().index(request, extra_context)

custom_admin_site = CustomAdminSite(name='admin')

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Address, AddressAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(ProductReview, ProductReviewAdmin)
custom_admin_site.register(Cart, CartAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(News, NewsAdmin)
custom_admin_site.register(NewsComment, NewsCommentAdmin)