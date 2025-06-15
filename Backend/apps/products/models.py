from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.core.utils import upload_to_path, generate_unique_slug

User = get_user_model()


class Category(BaseModel):
    """
    Product categories
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to_path, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Brand(BaseModel):
    """
    Product brands
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to=upload_to_path, blank=True, null=True)
    website = models.URLField(blank=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    """
    Main product model
    """
    PRODUCT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    track_inventory = models.BooleanField(default=True)
    
    # Physical attributes
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    # Status and features
    status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    requires_shipping = models.BooleanField(default=True)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)
        super().save(*args, **kwargs)

    @property
    def is_on_sale(self):
        return self.compare_price and self.price < self.compare_price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold


class ProductImage(BaseModel):
    """
    Product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=upload_to_path)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductAttribute(BaseModel):
    """
    Product attributes (e.g., Color, Size, Material)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    class Meta:
        db_table = 'product_attributes'
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Product Attributes'
        unique_together = ['name', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ProductAttribute, self.name)
        super().save(*args, **kwargs)


class ProductAttributeValue(BaseModel):
    """
    Product attribute values (e.g., Red, Large, Cotton)
    """
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    class Meta:
        db_table = 'product_attribute_values'
        verbose_name = 'Product Attribute Value'
        verbose_name_plural = 'Product Attribute Values'
        unique_together = ['attribute', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ProductAttributeValue, self.value)
        super().save(*args, **kwargs)


class ProductVariant(BaseModel):
    """
    Product variants (combinations of attributes)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to=upload_to_path, blank=True, null=True)
    
    # Variant attributes
    attributes = models.ManyToManyField(ProductAttributeValue, related_name='variants')

    class Meta:
        db_table = 'product_variants'
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    @property
    def display_name(self):
        attributes = self.attributes.all()
        if attributes:
            attr_names = [f"{attr.attribute.name}: {attr.value}" for attr in attributes]
            return f"{self.product.name} ({', '.join(attr_names)})"
        return self.product.name

    @property
    def effective_price(self):
        return self.price if self.price else self.product.price


class Review(BaseModel):
    """
    Product reviews
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user.email}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        # Update product rating after deletion
        product.update_rating()


# Add method to Product model to update rating
def update_rating(self):
    """Update product average rating and review count"""
    reviews = self.reviews.filter(is_approved=True)
    if reviews.exists():
        self.average_rating = reviews.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating'] or 0
        self.review_count = reviews.count()
    else:
        self.average_rating = 0
        self.review_count = 0
    self.save(update_fields=['average_rating', 'review_count'])

# Add the method to Product model
Product.update_rating = update_rating