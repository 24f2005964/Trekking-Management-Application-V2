<template>
  <div>
    <!-- Hero Header Banner -->
    <div class="card mb-4 border-0 shadow-sm overflow-hidden text-white rounded-3">
      <div
        class="p-4 d-flex flex-column justify-content-center"
        style="background: linear-gradient(90deg, rgba(20, 83, 45, 0.88) 0%, rgba(22, 101, 52, 0.75) 100%), url('/images/staff_bg.jpg') center/cover no-repeat; min-height: 140px;"
      >
        <h2 class="fw-bold mb-1"><i class="bi bi-person-badge me-2"></i> Staff Coordinator Dashboard</h2>
        <p class="mb-0 text-white-75">Manage your assigned trekking expeditions, capacity slots, and participant rosters</p>
      </div>
    </div>

    <!-- Alert Banner -->
    <div v-if="alertMsg" class="alert alert-dismissible fade show py-2 small shadow-sm mb-3" :class="'alert-' + alertType">
      <i class="bi me-1" :class="alertType === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'"></i>
      {{ alertMsg }}
      <button type="button" class="btn-close" @click="alertMsg = ''"></button>
    </div>

    <div v-if="loading" class="py-5 text-center">
      <div class="spinner-border text-success" role="status"></div>
    </div>

    <div v-else>
      <!-- Stat Cards Row -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card text-center border-success shadow-sm p-3 bg-white h-100">
            <div class="text-success fs-3 mb-1"><i class="bi bi-map"></i></div>
            <h6 class="text-uppercase text-muted fw-bold mb-1 small">Assigned Treks</h6>
            <h2 class="fw-bold text-dark mb-0">{{ counts.total_assigned }}</h2>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-center border-primary shadow-sm p-3 bg-white h-100">
            <div class="text-primary fs-3 mb-1"><i class="bi bi-compass"></i></div>
            <h6 class="text-uppercase text-muted fw-bold mb-1 small">Open Expeditions</h6>
            <h2 class="fw-bold text-dark mb-0">{{ counts.open_treks }}</h2>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-center border-warning shadow-sm p-3 bg-white h-100">
            <div class="text-warning fs-3 mb-1"><i class="bi bi-people"></i></div>
            <h6 class="text-uppercase text-muted fw-bold mb-1 small">Total Participants</h6>
            <h2 class="fw-bold text-dark mb-0">{{ counts.total_participants }}</h2>
          </div>
        </div>
      </div>

      <!-- Assigned Treks List -->
      <h4 class="fw-bold text-dark mb-3"><i class="bi bi-list-check me-2 text-success"></i>Your Assigned Trek Routes</h4>
      <div class="row g-4" v-if="treks.length > 0">
        <div class="col-md-6" v-for="t in treks" :key="t.id">
          <div class="card border-0 shadow-sm rounded-3 p-4 h-100">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <StatusBadge :status="t.difficulty" />
              <StatusBadge :status="t.status" />
            </div>

            <h5 class="fw-bold text-dark mt-2 mb-1">{{ t.name }}</h5>
            <p class="text-muted small mb-3"><i class="bi bi-geo-alt me-1"></i>{{ t.location }} ({{ t.duration_days }} days)</p>

            <div class="bg-light p-3 rounded-2 mb-3">
              <div class="d-flex justify-content-between small mb-1">
                <span class="text-muted">Dates:</span>
                <span class="fw-bold">{{ t.start_date }} to {{ t.end_date }}</span>
              </div>
              <div class="d-flex justify-content-between small mb-1">
                <span class="text-muted">Capacity Slots:</span>
                <span class="fw-bold text-success">{{ t.available_slots }} / {{ t.total_slots }} available</span>
              </div>
              <div class="d-flex justify-content-between small">
                <span class="text-muted">Registered Trekkers:</span>
                <span class="fw-bold text-primary">{{ t.confirmed_participants }} confirmed</span>
              </div>
            </div>

            <!-- Management Controls -->
            <div class="d-flex gap-1 flex-wrap mt-auto pt-2 border-top">
              <router-link :to="`/staff/treks/${t.id}/participants`" class="btn btn-sm btn-outline-primary rounded-pill px-3">
                <i class="bi bi-people me-1"></i>Roster
              </router-link>

              <!-- Button triggering the Pop-up Window Modal -->
              <button class="btn btn-sm btn-outline-secondary rounded-pill px-3" @click="openSlotsModal(t)">
                <i class="bi bi-sliders me-1"></i>Slots
              </button>

              <!-- Button triggering Custom Notice/Reminder Modal -->
              <button class="btn btn-sm btn-outline-info rounded-pill px-3" @click="openNoticeModal(t)">
                <i class="bi bi-megaphone me-1"></i>Notify
              </button>

              <!-- Button triggering the Status Change Modal -->
              <button class="btn btn-sm btn-success rounded-pill px-3 ms-auto d-flex align-items-center gap-1 shadow-sm" @click="openStatusModal(t)">
                <i class="bi bi-arrow-repeat"></i>
                <span>Status</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-5 bg-white rounded-3 shadow-sm">
        <p class="text-muted mb-0">No treks are currently assigned to you by the Admin.</p>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- POP-UP MODAL WINDOW: UPDATE AVAILABLE SLOTS -->
    <!-- ============================================================= -->
    <div class="modal fade" id="slotsModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">
              <i class="bi bi-sliders text-success me-2"></i>Update Available Slots
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveSlots">
            <div class="modal-body p-4" v-if="selectedTrek">
              <div class="mb-3">
                <h6 class="fw-bold mb-1">{{ selectedTrek.name }}</h6>
                <p class="text-muted small mb-0"><i class="bi bi-geo-alt me-1"></i>{{ selectedTrek.location }}</p>
              </div>

              <div class="alert alert-light border small py-2 mb-3">
                <div class="d-flex justify-content-between mb-1">
                  <span class="text-muted">Total Route Capacity:</span>
                  <strong>{{ selectedTrek.total_slots }} seats</strong>
                </div>
                <div class="d-flex justify-content-between">
                  <span class="text-muted">Currently Available:</span>
                  <strong class="text-success">{{ selectedTrek.available_slots }} seats</strong>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold">New Available Slots</label>
                <input
                  type="number"
                  class="form-control form-control-lg"
                  v-model.number="newSlots"
                  min="0"
                  :max="selectedTrek.total_slots"
                  required
                />
                <div class="form-text small">Enter any value between 0 and total capacity ({{ selectedTrek.total_slots }}).</div>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary rounded-pill px-3" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-success rounded-pill px-4" :disabled="savingSlots">
                <span v-if="savingSlots" class="spinner-border spinner-border-sm me-1"></span>
                Save Slots
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- POP-UP MODAL WINDOW: UPDATE TREK STATUS -->
    <!-- ============================================================= -->
    <div class="modal fade" id="statusModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">
              <i class="bi bi-arrow-repeat text-success me-2"></i>Update Expedition Status
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveStatus">
            <div class="modal-body p-4" v-if="statusTrek">
              <div class="mb-3">
                <h6 class="fw-bold mb-1">{{ statusTrek.name }}</h6>
                <p class="text-muted small mb-2"><i class="bi bi-geo-alt me-1"></i>{{ statusTrek.location }} ({{ statusTrek.duration_days }} days)</p>
                <div class="d-flex align-items-center gap-2 small">
                  <span class="text-muted">Current Status:</span>
                  <StatusBadge :status="statusTrek.status" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Select New Status</label>
                <div class="list-group">
                  <label class="list-group-item list-group-item-action d-flex align-items-center gap-3 p-3" :class="{ 'bg-success-subtle border-success': newStatusValue === 'Open' }" style="cursor: pointer;">
                    <input class="form-check-input flex-shrink-0 mt-0" type="radio" name="trekStatusRadio" value="Open" v-model="newStatusValue" />
                    <div>
                      <div class="fw-bold text-success"><i class="bi bi-play-circle-fill me-1"></i>Open</div>
                      <small class="text-muted">Expedition is open and actively accepting trekker reservations.</small>
                    </div>
                  </label>

                  <label class="list-group-item list-group-item-action d-flex align-items-center gap-3 p-3" :class="{ 'bg-warning-subtle border-warning': newStatusValue === 'Closed' }" style="cursor: pointer;">
                    <input class="form-check-input flex-shrink-0 mt-0" type="radio" name="trekStatusRadio" value="Closed" v-model="newStatusValue" />
                    <div>
                      <div class="fw-bold text-warning-emphasis"><i class="bi bi-pause-circle-fill me-1"></i>Closed</div>
                      <small class="text-muted">Booking registrations are frozen / closed to new participants.</small>
                    </div>
                  </label>

                  <label class="list-group-item list-group-item-action d-flex align-items-center gap-3 p-3" :class="{ 'bg-info-subtle border-info': newStatusValue === 'Completed' }" style="cursor: pointer;">
                    <input class="form-check-input flex-shrink-0 mt-0" type="radio" name="trekStatusRadio" value="Completed" v-model="newStatusValue" />
                    <div>
                      <div class="fw-bold text-info-emphasis"><i class="bi bi-check2-circle me-1"></i>Completed</div>
                      <small class="text-muted">Trek has successfully concluded and participant bookings are fulfilled.</small>
                    </div>
                  </label>
                </div>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary rounded-pill px-3" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-success rounded-pill px-4" :disabled="savingStatus">
                <span v-if="savingStatus" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-check-lg me-1"></i>Update Status
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- POP-UP MODAL WINDOW: STAFF CUSTOM NOTICE / REMINDER -->
    <!-- ============================================================= -->
    <div class="modal fade" id="noticeModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">
              <i class="bi bi-megaphone-fill text-info me-2"></i>Send Notice to Trekkers
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="sendStaffNotice">
            <div class="modal-body p-4" v-if="noticeTrek">
              <div class="alert alert-info py-2 small mb-3">
                <i class="bi bi-info-circle me-1"></i>
                Sending to all confirmed trekkers registered for <strong>{{ noticeTrek.name }}</strong>.
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Notice Subject</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="noticeForm.subject"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Instructions / Message Content</label>
                <textarea
                  class="form-control"
                  rows="4"
                  v-model="noticeForm.message"
                  placeholder="e.g. Please carry waterproof shoes, extra socks, and arrive at base camp by 6:00 AM..."
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Timing Mode</label>
                <div class="d-flex gap-3 pt-1">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      id="staffNow"
                      value="Instant"
                      v-model="noticeForm.dispatch_type"
                    />
                    <label class="form-check-label small fw-semibold" for="staffNow">
                      🚀 Send Now (Turant)
                    </label>
                  </div>
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      id="staffLater"
                      value="Scheduled Later"
                      v-model="noticeForm.dispatch_type"
                    />
                    <label class="form-check-label small fw-semibold" for="staffLater">
                      🕒 Schedule for Later
                    </label>
                  </div>
                </div>
              </div>

              <div class="mb-3" v-if="noticeForm.dispatch_type === 'Scheduled Later'">
                <label class="form-label small fw-semibold text-dark">Scheduled Execution Time</label>
                <input
                  type="datetime-local"
                  class="form-control"
                  v-model="noticeForm.scheduled_for"
                  required
                />
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary rounded-pill px-3" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-info rounded-pill px-4 text-white" :disabled="sendingNotice">
                <span v-if="sendingNotice" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-send-fill me-1"></i>
                {{ noticeForm.dispatch_type === 'Instant' ? 'Send Immediately' : 'Confirm Schedule' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import StatusBadge from '@/components/StatusBadge.vue'
import { Modal } from 'bootstrap'

const loading = ref(true)
const counts = ref({})
const treks = ref([])
const alertMsg = ref('')
const alertType = ref('success')

const selectedTrek = ref(null)
const newSlots = ref(0)
const savingSlots = ref(false)
let slotsModalInstance = null

const noticeTrek = ref(null)
const sendingNotice = ref(false)
const noticeForm = ref({
  subject: '',
  message: '',
  channel: 'Email',
  dispatch_type: 'Instant',
  scheduled_for: ''
})
let noticeModalInstance = null

const statusTrek = ref(null)
const newStatusValue = ref('Open')
const savingStatus = ref(false)
let statusModalInstance = null

const openStatusModal = (trek) => {
  statusTrek.value = trek
  newStatusValue.value = trek.status
  const modalEl = document.getElementById('statusModal')
  if (modalEl) {
    statusModalInstance = Modal.getOrCreateInstance(modalEl)
    statusModalInstance.show()
  }
}

const saveStatus = async () => {
  if (!statusTrek.value) return
  savingStatus.value = true
  try {
    await api.put(`/staff/treks/${statusTrek.value.id}/status`, {
      status: newStatusValue.value
    })
    statusModalInstance?.hide()
    showAlert(`Expedition status updated to "${newStatusValue.value}" successfully!`, 'success')
    fetchStaffDashboard()
  } catch (err) {
    showAlert(err.response?.data?.error || 'Failed to update trek status.', 'danger')
  } finally {
    savingStatus.value = false
  }
}

const showAlert = (msg, type = 'success') => {
  alertMsg.value = msg
  alertType.value = type
  setTimeout(() => { alertMsg.value = '' }, 4000)
}

const fetchStaffDashboard = async () => {
  loading.value = true
  try {
    const [dashRes, treksRes] = await Promise.all([
      api.get('/staff/dashboard'),
      api.get('/staff/treks')
    ])
    counts.value = dashRes.data.counts || {}
    treks.value = treksRes.data.treks || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openSlotsModal = (trek) => {
  selectedTrek.value = trek
  newSlots.value = trek.available_slots
  const modalEl = document.getElementById('slotsModal')
  if (modalEl) {
    slotsModalInstance = new Modal(modalEl)
    slotsModalInstance.show()
  }
}

const saveSlots = async () => {
  if (!selectedTrek.value) return
  savingSlots.value = true
  try {
    await api.put(`/staff/treks/${selectedTrek.value.id}/slots`, {
      available_slots: parseInt(newSlots.value)
    })
    slotsModalInstance?.hide()
    showAlert(`Available slots for "${selectedTrek.value.name}" updated to ${newSlots.value}.`, 'success')
    fetchStaffDashboard()
  } catch (err) {
    showAlert(err.response?.data?.error || 'Failed to update slots.', 'danger')
  } finally {
    savingSlots.value = false
  }
}

const setStatus = async (trekId, status) => {
  try {
    await api.put(`/staff/treks/${trekId}/status`, { status })
    showAlert(`Trek status successfully changed to "${status}".`, 'success')
    fetchStaffDashboard()
  } catch (err) {
    showAlert(err.response?.data?.error || 'Failed to update status.', 'danger')
  }
}

const openNoticeModal = (trek) => {
  noticeTrek.value = trek
  noticeForm.value = {
    subject: `Guide Notice: ${trek.name}`,
    message: '',
    channel: 'Email',
    dispatch_type: 'Instant',
    scheduled_for: ''
  }
  const modalEl = document.getElementById('noticeModal')
  if (modalEl) {
    noticeModalInstance = Modal.getOrCreateInstance(modalEl)
    noticeModalInstance.show()
  }
}

const sendStaffNotice = async () => {
  if (!noticeTrek.value) return
  sendingNotice.value = true
  try {
    const res = await api.post(`/staff/treks/${noticeTrek.value.id}/send-reminder`, noticeForm.value)
    noticeModalInstance?.hide()
    showAlert(res.data.message || 'Notice dispatched to trek participants!', 'success')
  } catch (err) {
    showAlert(err.response?.data?.error || 'Failed to dispatch notice.', 'danger')
  } finally {
    sendingNotice.value = false
  }
}

onMounted(fetchStaffDashboard)
</script>
