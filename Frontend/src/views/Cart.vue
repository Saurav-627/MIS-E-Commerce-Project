<template>
  <div class="cart">
    <div class="container">
      <div class="cart-header">
        <h1>Shopping Cart</h1>
        <p v-if="cartItems.length > 0">{{ cartItemCount }} item(s) in your cart</p>
        <p v-else>Your cart is empty</p>
      </div>
      
      <div v-if="cartItems.length === 0" class="empty-cart">
        <div class="empty-cart-icon">🛒</div>
        <h2>Your cart is empty</h2>
        <p>Add some items to your cart to get started!</p>
        <router-link to="/" class="btn-primary">Continue Shopping</router-link>
      </div>
      
      <div v-else class="cart-content">
        <div class="cart-items">
          <div v-for="item in cartItems" :key="item.product.id" class="cart-item">
            <div class="item-image">
              <img :src="item.product.image" :alt="item.product.name" />
            </div>
            
            <div class="item-info">
              <h3 class="item-name">{{ item.product.name }}</h3>
              <p class="item-description">{{ item.product.shortDescription }}</p>
              <div class="item-price">NPR {{ (item.product.price || 0).toLocaleString() }} each</div>
              <div class="stock-info">
                <span class="stock-available">{{ getAvailableStock(item.product.id) + item.quantity }} available</span>
              </div>
            </div>
            
            <div class="item-quantity">
              <label>Quantity:</label>
              <div class="quantity-controls">
                <button @click="decrementQuantity(item.product.id, item.quantity)" class="qty-btn">-</button>
                <span class="qty-display">{{ item.quantity }}</span>
                <button 
                  @click="incrementQuantity(item.product.id, item.quantity)" 
                  class="qty-btn"
                  :disabled="item.quantity >= item.product.stockQuantity"
                >+</button>
              </div>
            </div>
            
            <div class="item-total">
              <div class="total-price">NPR {{ ((item.product.price || 0) * (item.quantity || 0)).toLocaleString() }}</div>
              <button @click="removeFromCart(item.product.id)" class="remove-btn">
                Remove
              </button>
            </div>
          </div>
        </div>
        
        <div class="cart-summary">
          <h2>Order Summary</h2>
          
          <div class="summary-line">
            <span>Subtotal ({{ cartItemCount }} items)</span>
            <span>NPR {{ (cartTotal || 0).toLocaleString() }}</span>
          </div>
          
          <div class="summary-line">
            <span>Shipping</span>
            <span>{{ (cartTotal || 0) >= 5000 ? 'Free' : 'NPR 150' }}</span>
          </div>
          
          <div class="summary-line">
            <span>Tax (13%)</span>
            <span>NPR {{ Math.round((cartTotal || 0) * 0.13).toLocaleString() }}</span>
          </div>
          
          <div class="summary-total">
            <span>Total</span>
            <span>NPR {{ Math.round(finalTotal || 0).toLocaleString() }}</span>
          </div>
          
          <div class="cart-actions">
            <button @click="clearCart" class="btn-secondary clear-btn">
              Clear Cart
            </button>
            <button class="btn-primary checkout-btn">
              Proceed to Checkout
            </button>
          </div>
          
          <div class="continue-shopping">
            <router-link to="/" class="continue-link">← Continue Shopping</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useCart } from '@/composables/useCart';

const { cartItems, cartTotal, cartItemCount, removeFromCart, updateQuantity, clearCart, getAvailableStock } = useCart();

const finalTotal = computed(() => {
  const total = cartTotal.value || 0;
  const shipping = total >= 5000 ? 0 : 150; // Free shipping over NPR 5000
  const tax = total * 0.13; // 13% VAT in Nepal
  return total + shipping + tax;
});

const incrementQuantity = (productId, currentQuantity) => {
  updateQuantity(productId, currentQuantity + 1);
};

const decrementQuantity = (productId, currentQuantity) => {
  if (currentQuantity > 1) {
    updateQuantity(productId, currentQuantity - 1);
  }
};
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.cart-header {
  text-align: center;
  margin-bottom: 3rem;
}

.cart-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.cart-header p {
  color: #6b7280;
  font-size: 1.125rem;
  margin: 0;
}

.empty-cart {
  text-align: center;
  padding: 4rem 2rem;
  background: #f9fafb;
  border-radius: 12px;
}

.empty-cart-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-cart h2 {
  font-size: 1.5rem;
  color: #374151;
  margin: 0 0 0.5rem 0;
}

.empty-cart p {
  color: #6b7280;
  margin: 0 0 2rem 0;
}

.cart-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3rem;
  align-items: start;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cart-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: grid;
  grid-template-columns: 100px 1fr auto auto;
  gap: 1.5rem;
  align-items: center;
}

.item-image img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.item-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.item-price {
  color: #3b82f6;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.stock-info {
  font-size: 0.75rem;
  color: #6b7280;
}

.stock-available {
  background: #f0f9ff;
  color: #0369a1;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
}

.item-quantity {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.item-quantity label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.quantity-controls {
  display: flex;
  align-items: center;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.qty-btn {
  background: #f9fafb;
  border: none;
  width: 32px;
  height: 32px;
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
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.qty-display {
  min-width: 40px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: white;
}

.item-total {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.total-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.remove-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: underline;
  transition: color 0.2s ease;
}

.remove-btn:hover {
  color: #dc2626;
}

.cart-summary {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 2rem;
}

.cart-summary h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 1.5rem 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  color: #6b7280;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-top: 2px solid #e5e7eb;
  margin-top: 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.cart-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
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

.continue-shopping {
  margin-top: 1.5rem;
  text-align: center;
}

.continue-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.continue-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .cart-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .cart-item {
    grid-template-columns: 80px 1fr;
    grid-template-rows: auto auto;
    gap: 1rem;
  }
  
  .item-image {
    grid-row: 1 / 3;
  }
  
  .item-info {
    grid-column: 2;
    grid-row: 1;
  }
  
  .item-quantity,
  .item-total {
    grid-column: 2;
    grid-row: 2;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .item-total {
    text-align: left;
  }
  
  .cart-summary {
    position: static;
  }
}
</style>