<template>
  <div class="login">
    <div class="container">
      <div class="login-form-container" :class="{ 'form-loading': isLoading }">
        <div class="form-header">
          <div class="logo-section">
            <div class="logo-icon">🛍️</div>
            <h1>Welcome Back</h1>
            <p>Sign in to continue your shopping journey</p>
          </div>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group" :class="{ 'has-error': errors.email }">
            <label for="email">Email Address</label>
            <div class="input-wrapper">
              <span class="input-icon">📧</span>
              <input
                v-model="form.email"
                type="email"
                id="email"
                required
                placeholder="Enter your email"
                class="form-input"
                :class="{ 'error': errors.email, 'valid': form.email && !errors.email }"
                @blur="validateEmail"
                @input="clearError('email')"
              />
              <span v-if="form.email && !errors.email" class="validation-icon valid">✓</span>
              <span v-if="errors.email" class="validation-icon error">✗</span>
            </div>
            <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
          </div>
          
          <div class="form-group" :class="{ 'has-error': errors.password }">
            <label for="password">Password</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                id="password"
                required
                placeholder="Enter your password"
                class="form-input"
                :class="{ 'error': errors.password, 'valid': form.password && !errors.password }"
                @blur="validatePassword"
                @input="clearError('password')"
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
              <span v-if="form.password && !errors.password" class="validation-icon valid">✓</span>
            </div>
            <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
          </div>
          
          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.rememberMe">
              <span class="custom-checkbox"></span>
              Remember me
            </label>
            <a href="#" class="forgot-password" @click.prevent="showForgotPassword = true">
              Forgot password?
            </a>
          </div>
          
          <button 
            type="submit" 
            class="btn-primary login-btn" 
            :disabled="isLoading || !isFormValid"
            :class="{ 'loading': isLoading }"
          >
            <span v-if="isLoading" class="loading-content">
              <span class="spinner"></span>
              Signing in...
            </span>
            <span v-else class="button-content">
              <span class="button-icon">🚀</span>
              Sign In
            </span>
          </button>
          
          <div class="form-divider">
            <span>or continue with</span>
          </div>
          
          <div class="social-login">
            <button type="button" class="btn-social google-btn" @click="handleSocialLogin('google')">
              <span class="social-icon">🔍</span>
              Google
            </button>
            <button type="button" class="btn-social facebook-btn" @click="handleSocialLogin('facebook')">
              <span class="social-icon">👤</span>
              Facebook
            </button>
            <button type="button" class="btn-social apple-btn" @click="handleSocialLogin('apple')">
              <span class="social-icon">🍎</span>
              Apple
            </button>
          </div>
          
          <div class="form-footer">
            <p>Don't have an account? 
              <router-link to="/register" class="register-link">Create one now</router-link>
            </p>
          </div>
        </form>
      </div>
      
      <!-- Forgot Password Modal -->
      <div v-if="showForgotPassword" class="modal-overlay" @click="showForgotPassword = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Reset Password</h3>
            <button class="modal-close" @click="showForgotPassword = false">×</button>
          </div>
          <div class="modal-body">
            <p>Enter your email address and we'll send you a link to reset your password.</p>
            <div class="form-group">
              <input
                v-model="forgotEmail"
                type="email"
                placeholder="Enter your email"
                class="form-input"
              />
            </div>
            <button class="btn-primary" @click="handleForgotPassword">
              Send Reset Link
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoading = ref(false);
const showPassword = ref(false);
const showForgotPassword = ref(false);
const forgotEmail = ref('');

const form = ref({
  email: '',
  password: '',
  rememberMe: false
});

const errors = ref({
  email: '',
  password: ''
});

const isFormValid = computed(() => {
  return form.value.email && 
         form.value.password && 
         !errors.value.email && 
         !errors.value.password;
});

const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!form.value.email) {
    errors.value.email = 'Email is required';
  } else if (!emailRegex.test(form.value.email)) {
    errors.value.email = 'Please enter a valid email address';
  } else {
    errors.value.email = '';
  }
};

const validatePassword = () => {
  if (!form.value.password) {
    errors.value.password = 'Password is required';
  } else if (form.value.password.length < 6) {
    errors.value.password = 'Password must be at least 6 characters';
  } else {
    errors.value.password = '';
  }
};

const clearError = (field) => {
  errors.value[field] = '';
};

const handleLogin = async () => {
  validateEmail();
  validatePassword();
  
  if (!isFormValid.value) return;
  
  isLoading.value = true;
  
  // Simulate API call
  setTimeout(() => {
    isLoading.value = false;
    alert('Login successful! Welcome back to ShopVue.');
    router.push('/');
  }, 2000);
};

const handleSocialLogin = (provider) => {
  alert(`${provider} login functionality is for UI demo only. In a real app, this would authenticate via ${provider}.`);
};

const handleForgotPassword = () => {
  if (!forgotEmail.value) {
    alert('Please enter your email address');
    return;
  }
  alert('Password reset link sent! Check your email.');
  showForgotPassword.value = false;
  forgotEmail.value = '';
};
</script>

<style scoped>
.login {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  position: relative;
}

.login::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  pointer-events: none;
}

.container {
  max-width: 650px;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
  position: relative;
  z-index: 1;
}

.login-form-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 
    0 32px 64px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.login-form-container.form-loading {
  transform: scale(0.98);
}

.form-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 3rem 2rem 2rem;
  text-align: center;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  font-size: 3rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.form-header h1 {
  font-size: 2.25rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1a202c, #4a5568);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: -0.025em;
}

.form-header p {
  color: #64748b;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.login-form {
  padding: 2.5rem;
}

.form-group {
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.form-group.has-error {
  margin-bottom: 2.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 700;
  color: #374151;
  font-size: 0.95rem;
  letter-spacing: 0.025em;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  font-size: 1.1rem;
  z-index: 2;
  opacity: 0.7;
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 
    0 0 0 4px rgba(59, 130, 246, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.1);
  background: white;
  transform: translateY(-1px);
}

.form-input.valid {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.form-input.error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.validation-icon {
  position: absolute;
  right: 1rem;
  font-size: 1.1rem;
  font-weight: bold;
}

.validation-icon.valid {
  color: #10b981;
}

.validation-icon.error {
  color: #ef4444;
}

.password-toggle {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.password-toggle:hover {
  background: rgba(0, 0, 0, 0.05);
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-message::before {
  content: '⚠️';
  font-size: 0.8rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  color: #6b7280;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.custom-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: white;
}

.checkbox-label input[type="checkbox"]:checked + .custom-checkbox {
  background: #3b82f6;
  border-color: #3b82f6;
}

.checkbox-label input[type="checkbox"]:checked + .custom-checkbox::after {
  content: '✓';
  color: white;
  font-size: 0.8rem;
  font-weight: bold;
}

.forgot-password {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.forgot-password:hover {
  color: #2563eb;
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-primary.loading {
  pointer-events: none;
}

.loading-content, .button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.button-icon {
  font-size: 1.1rem;
}

.form-divider {
  text-align: center;
  margin: 2rem 0;
  position: relative;
}

.form-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
}

.form-divider span {
  background: rgba(255, 255, 255, 0.95);
  padding: 0 1.5rem;
  color: #9ca3af;
  font-size: 0.9rem;
  font-weight: 500;
}

.social-login {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.btn-social {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  color: #374151;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
}

.btn-social:hover {
  background: white;
  border-color: #d1d5db;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.social-icon {
  font-size: 1.5rem;
}

.form-footer {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(229, 231, 235, 0.5);
}

.form-footer p {
  color: #6b7280;
  margin: 0;
  font-weight: 500;
}

.register-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 700;
  transition: all 0.2s ease;
}

.register-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 640px) {
  .container {
    max-width: 100%;
    padding: 0 0.5rem;
  }
  
  .login-form-container {
    margin: 0.5rem;
    border-radius: 16px;
  }
  
  .form-header,
  .login-form {
    padding: 2rem 1.5rem;
  }
  
  .form-header h1 {
    font-size: 1.75rem;
  }
  
  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .social-login {
    grid-template-columns: 1fr;
  }
  
  .btn-social {
    flex-direction: row;
    justify-content: center;
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .login {
    padding: 1rem 0;
  }
  
  .form-header,
  .login-form {
    padding: 1.5rem 1rem;
  }
  
  .form-input {
    padding: 0.875rem 0.875rem 0.875rem 2.5rem;
  }
  
  .input-icon {
    left: 0.75rem;
  }
}
</style>