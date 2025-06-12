<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-brand">
        <h2>ShopVue</h2>
      </router-link>
      
      <div class="nav-links">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/cart" class="nav-link cart-link">
          <span class="cart-icon">🛒</span>
          Cart
          <span v-if="cartItemCount > 0" class="cart-badge">
            {{ cartItemCount }}
          </span>
        </router-link>
        <router-link to="/login" class="nav-link">Login</router-link>
        <router-link to="/register" class="nav-link btn-primary">Sign Up</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useCart } from '@/composables/useCart';

const { cartItemCount } = useCart();
</script>

<style scoped>
.navbar {
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #e5e7eb;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-brand h2 {
  color: #3b82f6;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.nav-brand {
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.nav-brand:hover {
  opacity: 0.8;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #374151;
  font-weight: 500;
  transition: color 0.2s ease;
  position: relative;
}

.nav-link:hover {
  color: #3b82f6;
}

.cart-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.cart-icon {
  font-size: 1.2rem;
}

.cart-badge {
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  position: absolute;
  top: -8px;
  right: -8px;
  animation: bounce 0.3s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-primary:hover {
  background: #2563eb;
  color: white;
  transform: translateY(-1px);
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }
  
  .nav-links {
    gap: 1rem;
  }
  
  .nav-link {
    font-size: 0.9rem;
  }
  
  .nav-brand h2 {
    font-size: 1.25rem;
  }
}
</style>