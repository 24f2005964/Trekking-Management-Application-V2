<template>
  <nav class="custom-navbar navbar navbar-expand-lg sticky-top">
    <div class="container-fluid container-xl">
      <!-- BRAND LOGO -->
      <router-link class="navbar-brand d-flex align-items-center gap-2 text-decoration-none" :to="homePath">
        <div class="brand-icon-wrapper">
          <i class="bi bi-compass-fill"></i>
        </div>
        <div class="d-flex align-items-baseline">
          <span class="brand-text">Trek<span class="brand-gradient">Sync</span></span>
          <span class="version-tag ms-1">v2</span>
        </div>
      </router-link>

      <!-- MOBILE TOGGLER -->
      <button
        class="navbar-toggler custom-toggler border-0 p-2"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="custom-toggler-icon">
          <i class="bi bi-list fs-4 text-white"></i>
        </span>
      </button>

      <!-- NAVIGATION CONTENT -->
      <div class="collapse navbar-collapse mt-3 mt-lg-0" id="navbarNav">
        <!-- ROLE SPECIFIC NAVIGATION LINKS -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 nav-pills-custom gap-1" v-if="auth.isAuthenticated">
          <!-- Admin Links -->
          <template v-if="auth.isAdmin">
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/admin/dashboard">
                <i class="bi bi-speedometer2 me-1"></i><span>Dashboard</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/admin/treks">
                <i class="bi bi-map me-1"></i><span>Manage Treks</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/admin/users">
                <i class="bi bi-people me-1"></i><span>Manage Users</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/admin/reports">
                <i class="bi bi-file-earmark-bar-graph me-1"></i><span>Reports & Alerts</span>
              </router-link>
            </li>
          </template>

          <!-- Staff Links -->
          <template v-if="auth.isStaff">
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/staff/dashboard">
                <i class="bi bi-person-badge me-1"></i><span>Assigned Treks</span>
              </router-link>
            </li>
          </template>

          <!-- Trekker Links -->
          <template v-if="auth.isTrekker">
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/trekker/dashboard">
                <i class="bi bi-binoculars me-1"></i><span>Explore Treks</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link custom-nav-link" to="/trekker/bookings">
                <i class="bi bi-ticket-perforated me-1"></i><span>My Bookings</span>
              </router-link>
            </li>
          </template>
        </ul>

        <!-- RIGHT CONTROLS & USER PROFILE -->
        <div class="d-flex flex-column flex-lg-row align-items-lg-center gap-2 gap-lg-3 ms-auto pt-2 pt-lg-0 border-0" v-if="auth.isAuthenticated">
          <!-- Trekker Notification Bell -->
          <button
            v-if="auth.isTrekker"
            class="inbox-pill-btn d-flex align-items-center gap-2"
            @click="openInboxModal"
            title="My Notifications & Email Inbox"
          >
            <i class="bi bi-bell-fill"></i>
            <span class="d-none d-sm-inline">Inbox</span>
            <span v-if="unreadCount > 0" class="badge-pulse">
              {{ unreadCount }}
            </span>
          </button>

          <!-- Trekker Profile Link -->
          <router-link v-if="auth.isTrekker" to="/trekker/profile" class="user-profile-chip text-decoration-none">
            <div class="user-avatar-circle">
              <i class="bi bi-person-fill"></i>
            </div>
            <div class="d-flex flex-column text-start">
              <span class="user-role-label trekker">TREKKER</span>
              <span class="user-display-name text-truncate">{{ auth.user?.name || auth.user?.email }}</span>
            </div>
          </router-link>

          <!-- Admin / Staff User Chip -->
          <div v-else class="user-profile-chip">
            <div class="user-avatar-circle" :class="auth.isAdmin ? 'admin-avatar' : 'staff-avatar'">
              <i :class="auth.isAdmin ? 'bi bi-shield-shaded' : 'bi bi-person-badge'"></i>
            </div>
            <div class="d-flex flex-column text-start">
              <span class="user-role-label" :class="auth.isAdmin ? 'admin' : 'staff'">
                {{ auth.userRole?.toUpperCase() }}
              </span>
              <span class="user-display-name text-truncate" :title="auth.user?.name">
                {{ auth.user?.name || 'Administrator' }}
              </span>
            </div>
          </div>

          <!-- LOGOUT BUTTON -->
          <button @click="handleLogout" class="logout-btn d-flex align-items-center gap-1" title="Sign out of TrekSync">
            <i class="bi bi-box-arrow-right"></i>
            <span>Logout</span>
          </button>
        </div>

        <!-- GUEST LINKS -->
        <div v-else class="d-flex gap-2 ms-auto pt-2 pt-lg-0">
          <router-link to="/login" class="guest-btn-outline">
            <i class="bi bi-box-arrow-in-right me-1"></i>Login
          </router-link>
          <router-link to="/register" class="guest-btn-solid">
            <i class="bi bi-person-plus me-1"></i>Register
          </router-link>
        </div>
      </div>
    </div>
  </nav>

  <!-- TREKKER INBOX & NOTIFICATIONS MODAL -->
  <div class="modal fade" id="trekkerInboxModal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-light">
          <div class="d-flex align-items-center gap-2">
            <i class="bi bi-bell-fill text-primary fs-5"></i>
            <h5 class="modal-title fw-bold text-dark mb-0">My Notifications & Trek Notices</h5>
            <span v-if="unreadCount > 0" class="badge bg-warning text-dark">{{ unreadCount }} Unread</span>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body p-0 bg-white">
          <div v-if="loadingNotifs" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div v-else-if="notifications.length === 0" class="text-center py-5 px-3 text-muted">
            <i class="bi bi-envelope-open display-4 text-muted d-block mb-3"></i>
            <h6 class="fw-semibold">No Notifications Yet</h6>
            <p class="small text-muted mb-0">When trek reminders, departure alerts, or staff announcements are sent, they will appear here in your inbox.</p>
          </div>

          <div v-else class="list-group list-group-flush">
            <div
              v-for="n in notifications"
              :key="n.id"
              class="list-group-item p-3 border-bottom list-group-item-action"
              :class="{ 'bg-light': !n.is_read }"
              @click="toggleNotificationDetail(n)"
              style="cursor: pointer;"
            >
              <div class="d-flex w-100 justify-content-between align-items-start mb-1">
                <div class="d-flex align-items-center gap-2">
                  <span v-if="!n.is_read" class="badge bg-primary rounded-circle p-1" style="width: 8px; height: 8px;"></span>
                  <h6 class="mb-0 fw-bold" :class="!n.is_read ? 'text-primary' : 'text-dark'">
                    {{ n.subject }}
                  </h6>
                </div>
                <small class="text-muted text-nowrap ms-2">{{ n.created_at }}</small>
              </div>

              <div class="d-flex justify-content-between align-items-center mb-2">
                <small class="text-secondary">
                  <i class="bi bi-person-fill me-1"></i>From: <strong>{{ n.sender }}</strong>
                  <span v-if="n.trek_name" class="ms-2 badge bg-secondary-subtle text-dark">
                    🏔️ {{ n.trek_name }}
                  </span>
                </small>
                <button
                  v-if="!n.is_read"
                  class="btn btn-sm btn-outline-primary py-0 px-2 rounded-pill small"
                  @click.stop="markAsRead(n.id)"
                  title="Mark as Read"
                >
                  Mark Read
                </button>
              </div>

              <!-- Message preview or expanded body -->
              <div class="p-3 bg-white border rounded-3 mt-2 text-dark" style="white-space: pre-line; font-size: 0.92rem; line-height: 1.5;">
                {{ n.message }}
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer bg-light d-flex justify-content-between">
          <div>
            <button
              v-if="unreadCount > 0"
              class="btn btn-sm btn-outline-secondary rounded-pill px-3"
              @click="markAllAsRead"
            >
              <i class="bi bi-check2-all me-1"></i>Mark All as Read
            </button>
          </div>
          <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { Modal } from 'bootstrap'

const auth = useAuthStore()
const router = useRouter()

const notifications = ref([])
const unreadCount = ref(0)
const loadingNotifs = ref(false)
let inboxModalInstance = null

const homePath = computed(() => {
  if (!auth.isAuthenticated) return '/login'
  if (auth.isAdmin) return '/admin/dashboard'
  if (auth.isStaff) return '/staff/dashboard'
  if (auth.isTrekker) return '/trekker/dashboard'
  return '/login'
})

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

const fetchNotifications = async () => {
  if (!auth.isTrekker) return
  try {
    const res = await api.get('/trekker/notifications')
    notifications.value = res.data.notifications || []
    unreadCount.value = res.data.unread_count || 0
  } catch (err) {
    // Graceful fallback if endpoint not accessible
  }
}

const openInboxModal = async () => {
  loadingNotifs.value = true
  const modalEl = document.getElementById('trekkerInboxModal')
  if (modalEl) {
    inboxModalInstance = Modal.getOrCreateInstance(modalEl)
    inboxModalInstance.show()
  }
  await fetchNotifications()
  loadingNotifs.value = false
}

const markAsRead = async (notifId) => {
  try {
    await api.put(`/trekker/notifications/${notifId}/read`)
    const n = notifications.value.find(item => item.id === notifId)
    if (n && !n.is_read) {
      n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch (err) {
    console.error(err)
  }
}

const markAllAsRead = async () => {
  try {
    await api.put('/trekker/notifications/read-all')
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
  } catch (err) {
    console.error(err)
  }
}

const toggleNotificationDetail = (n) => {
  if (!n.is_read) {
    markAsRead(n.id)
  }
}

onMounted(() => {
  if (auth.isTrekker) {
    fetchNotifications()
  }
})

watch(() => auth.isAuthenticated, (newVal) => {
  if (newVal && auth.isTrekker) {
    fetchNotifications()
  }
})
</script>

<style scoped>
/* Topbar Container with Modern Frosted Glass Dark Slate Styling */
.custom-navbar {
  background: linear-gradient(135deg, #0b132b 0%, #172554 50%, #0f172a 100%);
  border: none !important;
  border-bottom: none !important;
  box-shadow: 0 4px 20px -2px rgba(11, 19, 43, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 0.65rem 0;
  transition: all 0.3s ease;
  z-index: 1030;
}

/* Brand Logo */
.brand-icon-wrapper {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 1.25rem;
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.4);
  transition: transform 0.25s ease;
}

.custom-navbar .navbar-brand:hover .brand-icon-wrapper {
  transform: rotate(20deg) scale(1.05);
}

.brand-text {
  font-size: 1.3rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #ffffff;
}

.brand-gradient {
  color: #38bdf8;
  font-weight: 800;
}

.version-tag {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 6px;
  padding: 2px 6px;
  line-height: 1;
}

/* Navigation Links */
.custom-nav-link {
  color: #cbd5e1 !important;
  font-size: 0.92rem;
  font-weight: 500;
  padding: 0.48rem 0.85rem !important;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
}

.custom-nav-link i {
  font-size: 1rem;
  opacity: 0.85;
  transition: transform 0.2s ease;
}

.custom-nav-link:hover {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
}

.custom-nav-link:hover i {
  opacity: 1;
  transform: scale(1.1);
}

/* Active Nav Route */
.router-link-active.custom-nav-link {
  color: #ffffff !important;
  background: rgba(2, 132, 199, 0.25) !important;
  border: 1px solid rgba(56, 189, 248, 0.35);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
}

.router-link-active.custom-nav-link i {
  color: #38bdf8;
  opacity: 1;
}

/* User Profile Chip */
.user-profile-chip {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 0.35rem 0.85rem;
  border-radius: 50px;
  transition: all 0.2s ease;
}

.user-profile-chip:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.user-avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.admin-avatar {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.staff-avatar {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.user-role-label {
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  line-height: 1;
  text-transform: uppercase;
}

.user-role-label.admin {
  color: #fbbf24;
}

.user-role-label.staff {
  color: #34d399;
}

.user-role-label.trekker {
  color: #38bdf8;
}

.user-display-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #f1f5f9;
  max-width: 140px;
  line-height: 1.2;
}

/* Inbox Pill */
.inbox-pill-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #e2e8f0;
  padding: 0.4rem 0.85rem;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.inbox-pill-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  transform: translateY(-1px);
}

.badge-pulse {
  background: #f59e0b;
  color: #1e293b;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 20px;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.6);
}

/* Logout Button */
.logout-btn {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 0.4rem 0.95rem;
  border-radius: 50px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.logout-btn:hover {
  background: #ef4444;
  border-color: #ef4444;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.35);
}

/* Guest Buttons */
.guest-btn-outline {
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.4rem 1rem;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}

.guest-btn-outline:hover {
  color: #ffffff;
  border-color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
}

.guest-btn-solid {
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
  color: #ffffff;
  padding: 0.4rem 1.15rem;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
  transition: all 0.2s ease;
}

.guest-btn-solid:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45);
  color: #ffffff;
}

/* Custom Toggler for Mobile */
.custom-toggler {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}
.custom-toggler:focus {
  box-shadow: none;
}
</style>
