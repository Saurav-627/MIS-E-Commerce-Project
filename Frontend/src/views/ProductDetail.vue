<template>
  <div class="product-detail" v-if="product">
    <div class="container">
      <nav class="breadcrumb">
        <router-link to="/">Home</router-link>
        <span class="separator">></span>
        <span>{{ product.name }}</span>
      </nav>
      
      <div class="product-content">
        <div class="product-image-section">
          <div class="main-image">
            <img :src="product.image" :alt="product.name" />
            <div v-if="!product.inStock" class="out-of-stock-overlay">
              <span class="out-of-stock-text">Out of Stock</span>
            </div>
          </div>
        </div>
        
        <div class="product-info-section">
          <div class="product-category">{{ product.category }}</div>
          <h1 class="product-title">{{ product.name }}</h1>
          
          <div class="product-rating">
            <div class="stars">
              <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= Math.floor(product.rating) }">
                ★
              </span>
            </div>
            <span class="rating-text">{{ product.rating }} out of 5</span>
          </div>
          
          <div class="price-section">
            <span class="current-price">NPR {{ product.price.toLocaleString() }}</span>
          </div>
          
          <div class="stock-section">
            <div class="stock-info">
              <span v-if="product.inStock && product.stockQuantity > 0" class="stock-available">
                {{ getAvailableStock(product.id) }} available in stock
              </span>
              <span v-else class="stock-unavailable">Out of stock</span>
            </div>
          </div>
          
          <div class="description-section">
            <h3>Description</h3>
            <p>{{ product.fullDescription }}</p>
          </div>
          
          <div class="quantity-section" v-if="product.inStock && getAvailableStock(product.id) > 0">
            <label for="quantity">Quantity:</label>
            <div class="quantity-controls">
              <button @click="decrementQuantity" :disabled="quantity <= 1" class="qty-btn">-</button>
              <input 
                v-model.number="quantity" 
                id="quantity" 
                type="number" 
                :min="1" 
                :max="getAvailableStock(product.id)" 
                class="qty-input"
              >
              <button 
                @click="incrementQuantity" 
                :disabled="quantity >= getAvailableStock(product.id)" 
                class="qty-btn"
              >+</button>
            </div>
            <span class="max-quantity">Max: {{ getAvailableStock(product.id) }}</span>
          </div>
          
          <div class="action-buttons">
            <button 
              @click="handleAddToCart" 
              class="btn-primary add-to-cart"
              :disabled="!product.inStock || getAvailableStock(product.id) <= 0"
              :class="{ 'in-cart': isInCart(product.id) }"
            >
              {{ getButtonText() }}
            </button>
            <router-link to="/cart" class="btn-secondary">View Cart</router-link>
          </div>
          
          <div class="product-features">
            <div class="feature">
              <span class="feature-icon">🚚</span>
              <span>Free shipping on orders over NPR 5,000</span>
            </div>
            <div class="feature">
              <span class="feature-icon">↩️</span>
              <span>30-day return policy</span>
            </div>
            <div class="feature">
              <span class="feature-icon">🔒</span>
              <span>Secure payment</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else class="not-found">
    <div class="container">
      <h1>Product Not Found</h1>
      <p>The product you're looking for doesn't exist.</p>
      <router-link to="/" class="btn-primary">Back to Home</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { products } from '@/data/products';
import { useCart } from '@/composables/useCart';

const route = useRoute();
const quantity = ref(1);

const product = computed(() => {
  const id = parseInt(route.params.id);
  return products.find(p => p.id === id);
});

const { addToCart, isInCart, getAvailableStock } = useCart();

// Reset quantity when product changes or when available stock changes
watch([product, () => getAvailableStock(product.value?.id || 0)], () => {
  if (product.value) {
    const maxAvailable = getAvailableStock(product.value.id);
    if (quantity.value > maxAvailable) {
      quantity.value = Math.max(1, maxAvailable);
    }
  }
});

const incrementQuantity = () => {
  if (product.value && quantity.value < getAvailableStock(product.value.id)) {
    quantity.value++;
  }
};

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--;
  }
};

const handleAddToCart = () => {
  if (product.value) {
    const success = addToCart(product.value, quantity.value);
    if (success) {
      // Reset quantity after successful add
      quantity.value = 1;
    }
  }
};

const getButtonText = () => {
  if (!product.value) return 'Add to Cart';
  if (!product.value.inStock) return 'Out of Stock';
  if (getAvailableStock(product.value.id) <= 0) return 'No Stock Available';
  if (isInCart(product.value.id)) return 'Added to Cart ✓';
  return 'Add to Cart';
};
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.breadcrumb a {
  color: #3b82f6;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.separator {
  color: #9ca3af;
}

.product-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: start;
}

.product-image-section {
  position: relative;
}

.main-image {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.main-image img {
  width: 100%;
  height: 500px;
  object-fit: cover;
}

.out-of-stock-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.out-of-stock-text {
  background: #ef4444;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.125rem;
}

.product-info-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.product-category {
  color: #3b82f6;
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.product-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
  line-height: 1.2;
}

.product-rating {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stars {
  display: flex;
  gap: 2px;
}

.star {
  color: #d1d5db;
  font-size: 1.25rem;
}

.star.filled {
  color: #fbbf24;
}

.rating-text {
  color: #6b7280;
  font-weight: 500;
}

.price-section {
  padding: 1rem 0;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

.current-price {
  font-size: 2.5rem;
  font-weight: 700;
  color: #3b82f6;
}

.stock-section {
  padding: 0.5rem 0;
}

.stock-available {
  background: #dcfce7;
  color: #166534;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
}

.stock-unavailable {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
}

.description-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.75rem 0;
}

.description-section p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.quantity-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.quantity-section label {
  font-weight: 600;
  color: #374151;
}

.quantity-controls {
  display: flex;
  align-items: center;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.qty-btn {
  background: #f9fafb;
  border: none;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  transition: background-color 0.2s ease;
}

.qty-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-input {
  border: none;
  width: 60px;
  height: 40px;
  text-align: center;
  font-weight: 600;
  outline: none;
}

.max-quantity {
  font-size: 0.875rem;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  flex: 1;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.btn-primary.in-cart {
  background: #10b981;
}

.btn-primary.in-cart:hover {
  background: #059669;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #e5e7eb;
  transform: translateY(-1px);
}

.product-features {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #374151;
  font-weight: 500;
}

.feature-icon {
  font-size: 1.25rem;
}

.not-found {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.not-found h1 {
  font-size: 2rem;
  color: #111827;
  margin-bottom: 1rem;
}

.not-found p {
  color: #6b7280;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .product-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .product-title {
    font-size: 2rem;
  }
  
  .current-price {
    font-size: 2rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .main-image img {
    height: 300px;
  }
  
  .quantity-section {
    justify-content: space-between;
  }
}
</style>