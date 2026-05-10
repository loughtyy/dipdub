from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    locality = models.CharField(max_length=150, verbose_name="Населённый пункт")
    city = models.CharField(max_length=150, verbose_name="Город")
    state = models.CharField(max_length=150, verbose_name="Область")

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return self.locality


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок новости")
    slug = models.SlugField(max_length=210, unique=True, verbose_name="Slug новости")
    content = models.TextField(verbose_name="Содержание новости")
    short_description = models.TextField(max_length=300, verbose_name="Краткое описание")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Изображение новости")
    is_featured = models.BooleanField(default=False, verbose_name="Избранная новость")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    views = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', verbose_name="Новость")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    content = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_edited = models.BooleanField(default=False, verbose_name="Отредактировано")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    sentiment_label = models.CharField(max_length=10, blank=True, null=True, verbose_name="Тональность")
    sentiment_score = models.FloatField(blank=True, null=True, verbose_name="Уверенность")
    sentiment_analyzed = models.BooleanField(default=False, verbose_name="Проанализирован")

    class Meta:
        verbose_name = 'Комментарий к новости'
        verbose_name_plural = 'Комментарии к новостям'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Комментарий от {self.user.username} к новости "{self.news.title[:30]}"'

    def save(self, *args, **kwargs):
        print(f"SAVE called for {self.__class__.__name__}, analyzed={self.sentiment_analyzed}")
    
        if self.content and not self.sentiment_analyzed:
            print("Running sentiment analysis...")
            from store.sentiment_service import analyze_sentiment
            label, score = analyze_sentiment(self.content)
            print(f"Result: {label}, {score}")
            if label != 'error':
                self.sentiment_label = label.upper()
                self.sentiment_score = score
                self.sentiment_analyzed = True
        super().save(*args, **kwargs)

class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название категории")
    slug = models.SlugField(max_length=55, verbose_name="Slug категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    category_image = models.ImageField(upload_to='category', blank=True, null=True, verbose_name="Изображение категории")
    is_active = models.BooleanField(verbose_name="Активна?")
    is_featured = models.BooleanField(verbose_name="Рекомендуемая?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название товара")
    slug = models.SlugField(max_length=160, verbose_name="Slug товара")
    sku = models.CharField(max_length=255, unique=True, verbose_name="Артикул (SKU)")
    short_description = models.TextField(verbose_name="Краткое описание")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Детальное описание")
    product_image = models.ImageField(upload_to='product', blank=True, null=True, verbose_name="Изображение товара")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(Category, verbose_name="Категория товара", on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    is_active = models.BooleanField(verbose_name="Активен?")
    is_featured = models.BooleanField(verbose_name="Рекомендуемый?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class ProductReview(models.Model):
    RATING_CHOICES = (
        (5, 'Отлично'), (4, 'Хорошо'), (3, 'Средне'),
        (2, 'Плохо'), (1, 'Ужасно'),
    )

    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(verbose_name="Оценка", choices=RATING_CHOICES, default=5)
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    is_edited = models.BooleanField(verbose_name="Отредактировано", default=False)
    is_active = models.BooleanField(verbose_name="Активен?", default=True)
    sentiment_label = models.CharField(max_length=10, blank=True, null=True, verbose_name="Тональность")
    sentiment_score = models.FloatField(blank=True, null=True, verbose_name="Уверенность")
    sentiment_analyzed = models.BooleanField(default=False, verbose_name="Проанализирован")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('user', 'product')
        ordering = ('-created_at',)

    def __str__(self):
        stars = '★' * int(self.rating) + '☆' * (5 - int(self.rating))
        return f'{self.user} на {self.product}: {stars}'
    
    def save(self, *args, **kwargs):
        print(f"SAVE called for {self.__class__.__name__}, analyzed={self.sentiment_analyzed}")
    
        if self.comment and not self.sentiment_analyzed:
            print("Running sentiment analysis...")
            from store.sentiment_service import analyze_sentiment
            label, score = analyze_sentiment(self.comment)
            print(f"Result: {label}, {score}")
            if label != 'error':
                self.sentiment_label = label.upper()
                self.sentiment_score = score
                self.sentiment_analyzed = True
        super().save(*args, **kwargs)
        

class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    @property
    def total_price(self):
        return self.quantity * self.product.price


STATUS_CHOICES = (
    ('Оформлен', 'Оформлен'),
    ('Принят', 'Принят'),
    ('Отсортирован', 'Отсортирован'),
    ('В пути', 'В пути'),
    ('Доставлен', 'Доставлен'),
    ('Отменен', 'Отменен')
)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар", related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'product') 

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name="Адрес доставки", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=50,
        default="Оформлен",
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-ordered_date',)

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"