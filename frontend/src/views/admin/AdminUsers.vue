<template>
  <div>
    <!-- Toast Notification -->
    <div
      v-if="toast.show"
      class="position-fixed top-0 end-0 p-3"
      style="z-index: 1100;"
    >
      <div
        class="toast show align-items-center border-0 text-white"
        :class="toast.type === 'success' ? 'bg-success' : 'bg-danger'"
        role="alert"
      >
        <div class="d-flex">
          <div class="toast-body fw-semibold">
            <i :class="toast.type === 'success' ? 'bi bi-check-circle me-2' : 'bi bi-exclamation-triangle me-2'"></i>
            {{ toast.message }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="toast.show = false"></button>
        </div>
      </div>
    </div>

    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-0"><i class="bi bi-people-fill text-primary me-2"></i>User & Staff Management</h3>
        <p class="text-muted small mb-0">Manage platform users, approve trek staff, and manage account statuses</p>
      </div>
      <button class="btn btn-outline-primary rounded-pill px-3" @click="openAddStaffModal">
        <i class="bi bi-person-plus me-1"></i>Add Staff Member
      </button>
    </div>

    <!-- Filters Row -->
    <div class="row g-3 mb-3">
      <div class="col-md-8">
        <div class="input-group">
          <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control" v-model="searchQuery" @input="fetchUsers" placeholder="Search by name or email..." />
        </div>
      </div>
      <div class="col-md-4">
        <select class="form-select" v-model="roleFilter" @change="fetchUsers">
          <option value="all">All Roles</option>
          <option value="user">Trekkers (Users)</option>
          <option value="staff">Trek Staff</option>
          <option value="admin">Administrators</option>
        </select>
      </div>
    </div>

    <!-- Users Table Card -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-3">Name & Email</th>
                <th>Role</th>
                <th>Phone</th>
                <th>Approval</th>
                <th>Status</th>
                <th class="text-end pe-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td class="ps-3">
                  <div class="fw-bold text-dark">{{ u.name }}</div>
                  <div class="small text-muted">{{ u.email }}</div>
                </td>
                <td>
                  <span class="badge" :class="{
                    'bg-primary': u.role === 'user',
                    'bg-warning text-dark': u.role === 'staff',
                    'bg-dark': u.role === 'admin'
                  }">{{ u.role.toUpperCase() }}</span>
                </td>
                <td class="small">{{ u.phone || 'N/A' }}</td>
                <td>
                  <span v-if="u.role === 'admin'">
                    <span class="badge bg-dark"><i class="bi bi-shield-check me-1"></i>Pre-Approved</span>
                  </span>
                  <span v-else-if="u.role === 'staff'">
                    <span v-if="u.is_approved" class="badge bg-success"><i class="bi bi-check2-circle me-1"></i>Approved</span>
                    <button v-else class="btn btn-sm btn-outline-success py-0 px-2 fw-semibold" @click="approveStaff(u.id)">
                      <i class="bi bi-check-lg me-1"></i>Approve
                    </button>
                  </span>
                  <span v-else class="badge bg-light text-secondary border">
                    Trekker (N/A)
                  </span>
                </td>
                <td>
                  <span :class="u.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ u.is_active ? 'Active' : 'Blacklisted' }}
                  </span>
                </td>
                <td class="text-end pe-3">
                  <div class="d-inline-flex gap-1" v-if="u.role !== 'admin'">
                    <button
                      class="btn btn-sm"
                      :class="u.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                      @click="toggleStatus(u.id)"
                      :title="u.is_active ? 'Deactivate / Blacklist User' : 'Activate User'"
                    >
                      <i :class="u.is_active ? 'bi bi-slash-circle' : 'bi bi-check-circle'"></i>
                      {{ u.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="openDeleteUserModal(u)"
                      title="Permanently Delete User"
                    >
                      <i class="bi bi-trash"></i> Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Staff Modal -->
    <div class="modal fade" id="addStaffModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Add New Trek Staff Member</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="createStaff">
            <div class="modal-body">
              <!-- Inline error inside the modal -->
              <div v-if="modalError" class="alert alert-danger py-2 small mb-3">
                <i class="bi bi-exclamation-triangle me-1"></i>{{ modalError }}
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Staff Name</label>
                <input type="text" class="form-control" v-model="staffForm.name" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Email Address</label>
                <input type="email" class="form-control" v-model="staffForm.email" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Phone Number</label>
                <input type="tel" class="form-control" v-model="staffForm.phone" />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Initial Password</label>
                <input type="text" class="form-control" v-model="staffForm.password" required />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary px-4">Create Staff</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete User Confirmation Modal -->
    <div class="modal fade" id="deleteUserModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="userToDelete">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold text-danger">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>Delete User Account
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body py-3">
            <p class="mb-2">Are you sure you want to permanently delete this user account?</p>
            <div class="p-3 bg-light rounded-3 mb-3 border">
              <div class="fw-bold text-dark">{{ userToDelete.name }}</div>
              <div class="small text-muted">{{ userToDelete.email }}</div>
              <div class="small mt-1">
                <span class="badge" :class="{
                  'bg-primary': userToDelete.role === 'user',
                  'bg-warning text-dark': userToDelete.role === 'staff'
                }">{{ userToDelete.role.toUpperCase() }}</span>
              </div>
            </div>
            <div class="alert alert-warning py-2 small mb-0">
              <i class="bi bi-info-circle me-1"></i>
              This will remove the user permanently. Any active confirmed bookings will release slots back to the trek.
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger px-4" @click="handleDeleteUser" :disabled="deletingUser">
              <span v-if="deletingUser" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-trash me-1"></i>
              Confirm Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import api from '@/services/api'
import { Modal } from 'bootstrap'

const users = ref([])
const roleFilter = ref('all')
const searchQuery = ref('')
const modalError = ref('')

const staffForm = ref({
  name: '',
  email: '',
  phone: '',
  password: 'staff123'
})

const toast = reactive({ show: false, message: '', type: 'success' })
const userToDelete = ref(null)
const deletingUser = ref(false)
let addStaffModal = null
let deleteUserModal = null
let toastTimer = null

const showToast = (message, type = 'success') => {
  if (toastTimer) clearTimeout(toastTimer)
  toast.message = message
  toast.type = type
  toast.show = true
  toastTimer = setTimeout(() => { toast.show = false }, 3500)
}

const fetchUsers = async () => {
  try {
    const res = await api.get(`/admin/users?role=${roleFilter.value}&q=${searchQuery.value}`)
    users.value = res.data.users || []
  } catch (err) {
    console.error(err)
  }
}

const approveStaff = async (id) => {
  try {
    await api.put(`/admin/users/${id}/approve`)
    showToast('Staff member approved successfully!', 'success')
    fetchUsers()
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to approve staff', 'error')
  }
}

const toggleStatus = async (id) => {
  try {
    const res = await api.put(`/admin/users/${id}/toggle-status`)
    showToast(res.data.message || 'User status updated.', 'success')
    fetchUsers()
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to toggle status', 'error')
  }
}

const openAddStaffModal = () => {
  staffForm.value = { name: '', email: '', phone: '', password: 'staff123' }
  modalError.value = ''
  addStaffModal = new Modal(document.getElementById('addStaffModal'))
  addStaffModal.show()
}

const createStaff = async () => {
  modalError.value = ''
  try {
    const res = await api.post('/admin/staff', staffForm.value)
    addStaffModal?.hide()
    showToast(res.data.message || 'Staff member created successfully!', 'success')
    fetchUsers()
  } catch (err) {
    modalError.value = err.response?.data?.error || 'Failed to add staff member.'
  }
}

const openDeleteUserModal = (u) => {
  userToDelete.value = u
  const modalEl = document.getElementById('deleteUserModal')
  if (modalEl) {
    deleteUserModal = Modal.getOrCreateInstance(modalEl)
    deleteUserModal.show()
  }
}

const handleDeleteUser = async () => {
  if (!userToDelete.value) return
  deletingUser.value = true
  try {
    const res = await api.delete(`/admin/users/${userToDelete.value.id}`)
    deleteUserModal?.hide()
    showToast(res.data.message || 'User deleted successfully.', 'success')
    fetchUsers()
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to delete user.', 'error')
  } finally {
    deletingUser.value = false
    userToDelete.value = null
  }
}

onMounted(fetchUsers)
</script>

