<template>
  <div class="row justify-content-center py-4">
    <div class="col-md-7 col-lg-6 col-xl-5">
      <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
        <!-- Hero Header with Trekking Background -->
        <div
          class="p-4 text-center text-white"
          style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 58, 138, 0.75) 100%), url('/images/auth_bg.jpg') center/cover no-repeat; min-height: 140px;"
        >
          <div class="display-6 text-warning mb-2"><i class="bi bi-person-plus-fill"></i></div>
          <h3 class="fw-bold text-white mb-1">Create Your Account</h3>
          <p class="text-white-50 small mb-0">Join certified Himalayan expeditions & adventures</p>
        </div>

        <div class="card-body p-4 bg-white">
          <div v-if="error" class="alert alert-danger py-2 small">
            <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
          </div>
          <div v-if="successMsg" class="alert alert-success py-2 small">
            <i class="bi bi-check-circle me-1"></i>{{ successMsg }}
          </div>

        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label class="form-label small fw-semibold text-muted">Account Type</label>
            <div class="btn-group w-100" role="group">
              <button
                type="button"
                class="btn btn-sm"
                :class="role === 'user' ? 'btn-primary' : 'btn-outline-primary'"
                @click="role = 'user'"
              >
                <i class="bi bi-person me-1"></i>Trekker (Participant)
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="role === 'staff' ? 'btn-primary' : 'btn-outline-primary'"
                @click="role = 'staff'"
              >
                <i class="bi bi-person-badge me-1"></i>Trek Staff (Guide)
              </button>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label small fw-semibold text-muted">Full Name</label>
            <input type="text" class="form-control" v-model="name" placeholder="Enter your full name" required />
          </div>

          <div class="mb-3">
            <label class="form-label small fw-semibold text-muted">Email Address</label>
            <input type="email" class="form-control" v-model="email" placeholder="Enter your email address" required />
          </div>

          <div class="mb-3">
            <label class="form-label small fw-semibold text-muted">Phone Number</label>
            <input type="tel" class="form-control" v-model="phone" placeholder="10-digit mobile number" />
          </div>

          <div class="mb-3">
            <label class="form-label small fw-semibold text-muted">Password</label>
            <input type="password" class="form-control" v-model="password" placeholder="Create a password (min. 6 characters)" required />
          </div>

          <div v-if="role === 'staff'" class="alert alert-info py-2 small">
            <i class="bi bi-info-circle me-1"></i>
            Staff registrations require <strong>Administrator Approval</strong> before you can log in.
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100 rounded-pill py-2 mt-2 fw-semibold"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Creating Account...' : 'Register' }}
          </button>
        </form>

        <div class="mt-4 pt-3 border-top text-center small text-muted">
          Already registered?
          <router-link to="/login" class="text-primary fw-semibold text-decoration-none">Sign in here</router-link>
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

const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const role = ref('user')
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const handleSubmit = async () => {
  error.value = ''
  successMsg.value = ''
  loading.value = true
  try {
    const user = await auth.register({
      name: name.value,
      email: email.value,
      phone: phone.value,
      password: password.value,
      role: role.value
    })

    if (user.role === 'staff') {
      successMsg.value = 'Staff application submitted! Please wait for Admin approval before signing in.'
      setTimeout(() => router.push('/login'), 2500)
    } else {
      router.push('/trekker/dashboard')
    }
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}
</script>

