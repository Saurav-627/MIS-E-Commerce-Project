<template>
  <div class="register">
    <div class="container">
      <div class="register-form-container" :class="{ 'form-loading': isLoading }">
        <div class="form-header">
          <div class="logo-section">
            <div class="logo-icon">🎉</div>
            <h1>Join ShopVue</h1>
            <p>Create your account and start shopping amazing products</p>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
          </div>
        </div>
        
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-row">
            <div class="form-group" :class="{ 'has-error': errors.firstName }">
              <label for="firstName">First Name</label>
              <div class="input-wrapper">
                <span class="input-icon">👤</span>
                <input
                  v-model="form.firstName"
                  type="text"
                  id="firstName"
                  required
                  placeholder="Enter your first name"
                  class="form-input"
                  :class="{ 'error': errors.firstName, 'valid': form.firstName && !errors.firstName }"
                  @blur="validateFirstName"
                  @input="clearError('firstName')"
                />
                <span v-if="form.firstName && !errors.firstName" class="validation-icon valid">✓</span>
                <span v-if="errors.firstName" class="validation-icon error">✗</span>
              </div>
              <div v-if="errors.firstName" class="error-message">{{ errors.firstName }}</div>
            </div>
            
            <div class="form-group" :class="{ 'has-error': errors.lastName }">
              <label for="lastName">Last Name</label>
              <div class="input-wrapper">
                <span class="input-icon">👤</span>
                <input
                  v-model="form.lastName"
                  type="text"
                  id="lastName"
                  required
                  placeholder="Enter your last name"
                  class="form-input"
                  :class="{ 'error': errors.lastName, 'valid': form.lastName && !errors.lastName }"
                  @blur="validateLastName"
                  @input="clearError('lastName')"
                />
                <span v-if="form.lastName && !errors.lastName" class="validation-icon valid">✓</span>
                <span v-if="errors.lastName" class="validation-icon error">✗</span>
              </div>
              <div v-if="errors.lastName" class="error-message">{{ errors.lastName }}</div>
            </div>
          </div>
          
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
                placeholder="Create a password"
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
            <div class="password-strength">
              <div class="strength-bar">
                <div 
                  class="strength-fill" 
                  :class="passwordStrength.class"
                  :style="{ width: passwordStrength.width + '%' }"
                ></div>
              </div>
              <span class="strength-text" :class="passwordStrength.class">
                {{ passwordStrength.text }}
              </span>
            </div>
            <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
          </div>
          
          <div class="form-group" :class="{ 'has-error': errors.confirmPassword }">
            <label for="confirmPassword">Confirm Password</label>
            <div class="input-wrapper">
              <span class="input-icon">🔐</span>
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                id="confirmPassword"
                required
                placeholder="Confirm your password"
                class="form-input"
                :class="{ 'error': errors.confirmPassword, 'valid': form.confirmPassword && !errors.confirmPassword }"
                @blur="validateConfirmPassword"
                @input="clearError('confirmPassword')"
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
              <span v-if="form.confirmPassword && !errors.confirmPassword" class="validation-icon valid">✓</span>
              <span v-if="errors.confirmPassword" class="validation-icon error">✗</span>
            </div>
            <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label" :class="{ 'error': errors.agreeToTerms }">
              <input type="checkbox" v-model="form.agreeToTerms" required>
              <span class="custom-checkbox"></span>
              I agree to the <a href="#" class="terms-link" @click.prevent="showTerms = true">Terms of Service</a> 
              and <a href="#" class="terms-link" @click.prevent="showPrivacy = true">Privacy Policy</a>
            </label>
            <div v-if="errors.agreeToTerms" class="error-message">{{ errors.agreeToTerms }}</div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.newsletter">
              <span class="custom-checkbox"></span>
              <span class="newsletter-text">
                Subscribe to our newsletter for exclusive offers and updates
                <span class="newsletter-badge">🎁 Get 10% off</span>
              </span>
            </label>
          </div>
          
          <button 
            type="submit" 
            class="btn-primary register-btn" 
            :disabled="isLoading || !isFormValid"
            :class="{ 'loading': isLoading }"
          >
            <span v-if="isLoading" class="loading-content">
              <span class="spinner"></span>
              Creating Account...
            </span>
            <span v-else class="button-content">
              <span class="button-icon">🚀</span>
              Create Account
            </span>
          </button>
          
          <div class="form-divider">
            <span>or sign up with</span>
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
            <p>Already have an account? 
              <router-link to="/login" class="login-link">Sign in here</router-link>
            </p>
          </div>
        </form>
      </div>
      
      <!-- Terms Modal -->
      <div v-if="showTerms" class="modal-overlay" @click="showTerms = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Terms of Service</h3>
            <button class="modal-close" @click="showTerms = false">×</button>
          </div>
          <div class="modal-body">
            <p>Welcome to ShopVue! By using our service, you agree to these terms.</p>
            <h4>1. Account Responsibility</h4>
            <p>You are responsible for maintaining the security of your account.</p>
            <h4>2. Product Information</h4>
            <p>We strive to provide accurate product information and pricing.</p>
            <h4>3. Payment Terms</h4>
            <p>All payments are processed securely through our payment partners.</p>
            <button class="btn-primary" @click="showTerms = false">I Understand</button>
          </div>
        </div>
      </div>
      
      <!-- Privacy Modal -->
      <div v-if="showPrivacy" class="modal-overlay" @click="showPrivacy = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Privacy Policy</h3>
            <button class="modal-close" @click="showPrivacy = false">×</button>
          </div>
          <div class="modal-body">
            <p>Your privacy is important to us. Here's how we protect your data.</p>
            <h4>Data Collection</h4>
            <p>We collect only necessary information to provide our services.</p>
            <h4>Data Usage</h4>
            <p>Your data is used to improve your shopping experience.</p>
            <h4>Data Protection</h4>
            <p>We use industry-standard security measures to protect your information.</p>
            <button class="btn-primary" @click="showPrivacy = false">Got It</button>
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
const showConfirmPassword = ref(false);
const showTerms = ref(false);
const showPrivacy = ref(false);

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false,
  newsletter: false
});

const errors = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: ''
});

const progressPercentage = computed(() => {
  const fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword'];
  const filledFields = fields.filter(field => form.value[field] && !errors.value[field]);
  const termsAgreed = form.value.agreeToTerms ? 1 : 0;
  return ((filledFields.length + termsAgreed) / (fields.length + 1)) * 100;
});

const passwordStrength = computed(() => {
  const password = form.value.password;
  if (!password) return { width: 0, class: '', text: '' };
  
  let score = 0;
  let feedback = [];
  
  if (password.length >= 8) score += 1;
  else feedback.push('8+ characters');
  
  if (/[a-z]/.test(password)) score += 1;
  else feedback.push('lowercase');
  
  if (/[A-Z]/.test(password)) score += 1;
  else feedback.push('uppercase');
  
  if (/[0-9]/.test(password)) score += 1;
  else feedback.push('number');
  
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  else feedback.push('special char');
  
  const strengthLevels = [
    { width: 20, class: 'very-weak', text: 'Very Weak' },
    { width: 40, class: 'weak', text: 'Weak' },
    { width: 60, class: 'fair', text: 'Fair' },
    { width: 80, class: 'good', text: 'Good' },
    { width: 100, class: 'strong', text: 'Strong' }
  ];
  
  return strengthLevels[score] || strengthLevels[0];
});

const isFormValid = computed(() => {
  return form.value.firstName && 
         form.value.lastName &&
         form.value.email && 
         form.value.password && 
         form.value.confirmPassword &&
         form.value.agreeToTerms &&
         !Object.values(errors.value).some(error => error);
});

const validateFirstName = () => {
  if (!form.value.firstName) {
    errors.value.firstName = 'First name is required';
  } else if (form.value.firstName.length < 2) {
    errors.value.firstName = 'First name must be at least 2 characters';
  } else {
    errors.value.firstName = '';
  }
};

const validateLastName = () => {
  if (!form.value.lastName) {
    errors.value.lastName = 'Last name is required';
  } else if (form.value.lastName.length < 2) {
    errors.value.lastName = 'Last name must be at least 2 characters';
  } else {
    errors.value.lastName = '';
  }
};

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
  } else if (form.value.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters';
  } else {
    errors.value.password = '';
  }
  
  // Re-validate confirm password if it exists
  if (form.value.confirmPassword) {
    validateConfirmPassword();
  }
};

const validateConfirmPassword = () => {
  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = 'Please confirm your password';
  } else if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match';
  } else {
    errors.value.confirmPassword = '';
  }
};

const clearError = (field) => {
  errors.value[field] = '';
};

const handleRegister = async () => {
  // Validate all fields
  validateFirstName();
  validateLastName();
  validateEmail();
  validatePassword();
  validateConfirmPassword();
  
  if (!form.value.agreeToTerms) {
    errors.value.agreeToTerms = 'You must agree to the terms';
  } else {
    errors.value.agreeToTerms = '';
  }
  
  if (!isFormValid.value) return;
  
  isLoading.value = true;
  
  // Simulate API call
  setTimeout(() => {
    isLoading.value = false;
    alert(`Welcome to ShopVue, ${form.value.firstName}! Your account has been created successfully.`);
    router.push('/login');
  }, 2500);
};

const handleSocialLogin = (provider) => {
  alert(`${provider} registration functionality is for UI demo only. In a real app, this would create an account via ${provider}.`);
};
</script>

<style scoped>
.register {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  position: relative;
}

.register::before {
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

.register-form-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 
    0 32px 64px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.register-form-container.form-loading {
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
  margin-bottom: 2rem;
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
  line-height: 1.5;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.register-form {
  padding: 2.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.form-group.has-error {
  margin-bottom: 2.5rem;
}

.form-group label {
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

.password-strength {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-fill.very-weak { background: #ef4444; }
.strength-fill.weak { background: #f97316; }
.strength-fill.fair { background: #eab308; }
.strength-fill.good { background: #22c55e; }
.strength-fill.strong { background: #10b981; }

.strength-text {
  font-size: 0.8rem;
  font-weight: 600;
  min-width: 60px;
}

.strength-text.very-weak { color: #ef4444; }
.strength-text.weak { color: #f97316; }
.strength-text.fair { color: #eab308; }
.strength-text.good { color: #22c55e; }
.strength-text.strong { color: #10b981; }

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

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.95rem;
  color: #6b7280;
  cursor: pointer;
  font-weight: 500;
  line-height: 1.5;
}

.checkbox-label.error {
  color: #ef4444;
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
  flex-shrink: 0;
  margin-top: 0.1rem;
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

.terms-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
}

.terms-link:hover {
  text-decoration: underline;
}

.newsletter-text {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.newsletter-badge {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  width: fit-content;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.register-btn {
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

.login-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 700;
  transition: all 0.2s ease;
}

.login-link:hover {
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
  max-width: 500px;
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
  margin-bottom: 1rem;
  line-height: 1.6;
}

.modal-body h4 {
  color: #111827;
  margin: 1.5rem 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.modal-body h4:first-of-type {
  margin-top: 1rem;
}

/* Responsive Design */
@media (max-width: 640px) {
  .container {
    max-width: 100%;
    padding: 0 0.5rem;
  }
  
  .register-form-container {
    margin: 0.5rem;
    border-radius: 16px;
  }
  
  .form-header,
  .register-form {
    padding: 2rem 1.5rem;
  }
  
  .form-header h1 {
    font-size: 1.75rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
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
  .register {
    padding: 1rem 0;
  }
  
  .form-header,
  .register-form {
    padding: 1.5rem 1rem;
  }
  
  .form-input {
    padding: 0.875rem 0.875rem 0.875rem 2.5rem;
  }
  
  .input-icon {
    left: 0.75rem;
  }
  
  .password-strength {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>