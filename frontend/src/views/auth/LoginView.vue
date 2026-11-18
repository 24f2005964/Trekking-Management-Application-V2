<template>
  <div class="row justify-content-center py-4">
    <div class="col-md-6 col-lg-5 col-xl-4">
      <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
        <!-- Hero Header with Trekking Background -->
        <div
          class="p-4 text-center text-white"
          style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 58, 138, 0.75) 100%), url('/images/auth_bg.jpg') center/cover no-repeat; min-height: 140px;"
        >
          <div class="display-6 text-warning mb-2"><i class="bi bi-compass-fill"></i></div>
          <h3 class="fw-bold text-white mb-1">Welcome to TrekSync</h3>
          <p class="text-white-50 small mb-0">Sign in to your trekking expedition account</p>
        </div>

        <div class="card-body p-4 bg-white">
          <div v-if="error" class="alert alert-danger py-2 small">
            <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label small fw-semibold text-muted">Email Address</label>
              <input
                type="email"
                class="form-control"
                v-model="email"
                placeholder="Enter your email address"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label small fw-semibold text-muted">Password</label>
              <input
                type="password"
                class="form-control"
                v-model="password"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 rounded-pill py-2 mt-2 fw-semibold"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Signing in...' : 'Sign In' }}
            </button>
          </form>

          <div class="mt-4 pt-3 border-top text-center small text-muted">
            Don't have an account?
            <router-link to="/register" class="text-primary fw-semibold text-decoration-none">Register here</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    const user = await auth.login(email.value, password.value)
    if (user.role === 'admin') router.push('/admin/dashboard')
    else if (user.role === 'staff') router.push('/staff/dashboard')
    else router.push('/trekker/dashboard')
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}
</script>

