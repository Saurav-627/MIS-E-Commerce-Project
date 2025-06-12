import { ref, computed } from 'vue';
import { products } from '@/data/products';

const cartItems = ref([]);

// Load cart from localStorage on app start
const loadCart = () => {
  const savedCart = localStorage.getItem('ecommerce-cart');
  if (savedCart) {
    try {
      const parsedCart = JSON.parse(savedCart);
      // Validate and sanitize cart data
      cartItems.value = parsedCart.map((item) => ({
        product: {
          ...item.product,
          price: Number(item.product.price) || 0
        },
        quantity: Number(item.quantity) || 1
      }));
    } catch (error) {
      console.error('Error loading cart from localStorage:', error);
      cartItems.value = [];
    }
  }
};

// Save cart to localStorage
const saveCart = () => {
  localStorage.setItem('ecommerce-cart', JSON.stringify(cartItems.value));
};

// Get available stock for a product
const getAvailableStock = (productId) => {
  const product = products.find(p => p.id === productId);
  if (!product) return 0;
  
  const cartItem = cartItems.value.find(item => item.product.id === productId);
  const quantityInCart = cartItem ? cartItem.quantity : 0;
  
  return Math.max(0, product.stockQuantity - quantityInCart);
};

export const useCart = () => {
  // Initialize cart from localStorage
  if (cartItems.value.length === 0) {
    loadCart();
  }

  const addToCart = (product, quantity = 1) => {
    const availableStock = getAvailableStock(product.id);
    
    if (availableStock <= 0) {
      alert('Sorry, this product is out of stock!');
      return false;
    }
    
    if (quantity > availableStock) {
      alert(`Only ${availableStock} items available in stock!`);
      return false;
    }
    
    const existingItem = cartItems.value.find(item => item.product.id === product.id);
    
    if (existingItem) {
      const newQuantity = existingItem.quantity + quantity;
      if (newQuantity > product.stockQuantity) {
        alert(`Cannot add more items. Only ${product.stockQuantity} available in stock!`);
        return false;
      }
      existingItem.quantity = newQuantity;
    } else {
      cartItems.value.push({
        product: {
          ...product,
          price: Number(product.price) || 0
        },
        quantity: Number(quantity) || 1
      });
    }
    
    saveCart();
    return true;
  };

  const removeFromCart = (productId) => {
    const index = cartItems.value.findIndex(item => item.product.id === productId);
    if (index > -1) {
      cartItems.value.splice(index, 1);
      saveCart();
    }
  };

  const updateQuantity = (productId, quantity) => {
    const item = cartItems.value.find(item => item.product.id === productId);
    if (item) {
      if (quantity <= 0) {
        removeFromCart(productId);
      } else {
        const product = products.find(p => p.id === productId);
        if (product && quantity > product.stockQuantity) {
          alert(`Cannot set quantity to ${quantity}. Only ${product.stockQuantity} available in stock!`);
          return false;
        }
        item.quantity = Number(quantity) || 1;
        saveCart();
      }
    }
    return true;
  };

  const clearCart = () => {
    cartItems.value = [];
    saveCart();
  };

  const cartTotal = computed(() => {
    return cartItems.value.reduce((total, item) => {
      const price = Number(item.product.price) || 0;
      const quantity = Number(item.quantity) || 0;
      return total + (price * quantity);
    }, 0);
  });

  const cartItemCount = computed(() => {
    return cartItems.value.reduce((count, item) => count + (Number(item.quantity) || 0), 0);
  });

  const isInCart = (productId) => {
    return cartItems.value.some(item => item.product.id === productId);
  };

  return {
    cartItems: computed(() => cartItems.value),
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    cartTotal,
    cartItemCount,
    isInCart,
    getAvailableStock
  };
};