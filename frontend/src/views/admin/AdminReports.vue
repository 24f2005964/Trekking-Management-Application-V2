<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h3 class="fw-bold text-dark mb-0">
          <i class="bi bi-file-earmark-bar-graph text-primary me-2"></i>Activity Reports, Logs & Dispatcher
        </h3>
        <p class="text-muted small mb-0">Scheduled monthly performance reports, PDF generation, and automated trek reminder scheduler</p>
      </div>

      <!-- Navigation Tabs -->
      <ul class="nav nav-pills bg-white p-1 rounded-pill shadow-sm border">
        <li class="nav-item">
          <button
            class="nav-link rounded-pill px-3 py-1 small fw-semibold"
            :class="{ active: activeTab === 'reports' }"
            @click="activeTab = 'reports'"
          >
            <i class="bi bi-file-earmark-pdf me-1"></i>Monthly Reports (PDF)
          </button>
        </li>
        <li class="nav-item">
          <button
            class="nav-link rounded-pill px-3 py-1 small fw-semibold"
            :class="{ active: activeTab === 'reminders' }"
            @click="activeTab = 'reminders'"
          >
            <i class="bi bi-bell-fill me-1"></i>Reminders & Schedule
          </button>
        </li>
      </ul>
    </div>

    <!-- Feedback Alerts -->
    <div v-if="successMsg" class="alert alert-success d-flex align-items-center justify-content-between py-2 small mb-3 shadow-sm">
      <div>
        <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
      </div>
      <button
        v-if="latestPdfFile && activeTab === 'reports'"
        class="btn btn-sm btn-success py-1 px-3"
        @click="downloadReport(latestPdfFile)"
      >
        <i class="bi bi-download me-1"></i>Download PDF Again
      </button>
      <button v-else type="button" class="btn-close btn-sm" @click="successMsg = ''"></button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger py-2 small mb-3 shadow-sm d-flex justify-content-between align-items-center">
      <div><i class="bi bi-exclamation-triangle-fill me-1"></i>{{ errorMsg }}</div>
      <button type="button" class="btn-close btn-sm" @click="errorMsg = ''"></button>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 1: MONTHLY REPORTS (PDF & HTML) -->
    <!-- ============================================================= -->
    <div v-show="activeTab === 'reports'">
      <div class="d-flex justify-content-end mb-3">
        <button
          class="btn btn-primary rounded-pill px-4 shadow-sm d-flex align-items-center"
          @click="generateReport"
          :disabled="generating"
        >
          <span v-if="generating" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-file-earmark-pdf-fill text-danger bg-white p-1 rounded-circle me-2"></i>
          <span>{{ generating ? 'Generating PDF...' : 'Generate & Download PDF Report' }}</span>
        </button>
      </div>

      <!-- Monthly Reports Archive Card -->
      <div class="card border-0 shadow-sm rounded-3 mb-4">
        <div class="card-header bg-white py-3 border-0 d-flex justify-content-between align-items-center">
          <h5 class="fw-bold text-dark mb-0">
            <i class="bi bi-folder-check me-2 text-primary"></i>Generated Monthly Reports Archive
          </h5>
          <button class="btn btn-sm btn-outline-secondary rounded-pill px-3" @click="fetchReportsList">
            <i class="bi bi-arrow-clockwise me-1"></i>Refresh
          </button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive" v-if="reportsList.length > 0">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-3">Report Document</th>
                  <th>Format</th>
                  <th>File Size</th>
                  <th>Generated On</th>
                  <th class="text-end pe-3">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in reportsList" :key="r.filename">
                  <td class="ps-3">
                    <div class="d-flex align-items-center">
                      <i
                        :class="r.type === 'PDF' ? 'bi bi-file-earmark-pdf-fill text-danger fs-4 me-2' : 'bi bi-filetype-html text-primary fs-4 me-2'"
                      ></i>
                      <div>
                        <div class="fw-semibold text-dark">{{ r.filename }}</div>
                        <div class="small text-muted">Monthly Trekking Activity & Performance</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span
                      class="badge"
                      :class="r.type === 'PDF' ? 'bg-danger' : 'bg-primary'"
                    >{{ r.type }}</span>
                  </td>
                  <td class="small text-muted">{{ formatBytes(r.size_bytes) }}</td>
                  <td class="small">{{ r.created_at }}</td>
                  <td class="text-end pe-3">
                    <button
                      class="btn btn-sm"
                      :class="r.type === 'PDF' ? 'btn-outline-danger' : 'btn-outline-primary'"
                      @click="downloadReport(r.filename)"
                      :disabled="downloadingFile === r.filename"
                    >
                      <span v-if="downloadingFile === r.filename" class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-download me-1"></i>
                      Download {{ r.type }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-4 text-muted small">
            <i class="bi bi-inbox fs-2 text-muted d-block mb-1"></i>
            No reports generated yet. Click <b>"Generate & Download PDF Report"</b> above to generate one now.
          </div>
        </div>
      </div>

      <!-- Master Reservations Log Table -->
      <div class="card border-0 shadow-sm rounded-3 mb-4">
        <div class="card-header bg-white py-3 border-0">
          <h5 class="fw-bold text-dark mb-0">
            <i class="bi bi-ticket-perforated me-2 text-primary"></i>Master Reservations Log
          </h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-3">Booking ID</th>
                  <th>Trekker Name</th>
                  <th>Trek Route</th>
                  <th>Seats</th>
                  <th>Date Reserved</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td class="ps-3 fw-bold text-muted">#{{ b.id }}</td>
                  <td>
                    <div class="fw-bold text-dark">{{ b.user_name }}</div>
                    <div class="small text-muted">{{ b.user_email }}</div>
                  </td>
                  <td>
                    <div class="fw-semibold">{{ b.trek_name }}</div>
                    <div class="small text-muted">{{ b.trek_location }}</div>
                  </td>
                  <td><span class="badge bg-secondary">{{ b.seats_booked }}</span></td>
                  <td class="small">{{ b.booking_date }}</td>
                  <td><StatusBadge :status="b.status" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 2: TREK REMINDERS & AUTOMATED SCHEDULE DISPATCHER -->
    <!-- ============================================================= -->
    <div v-show="activeTab === 'reminders'">
      <!-- Unified Trek Reminder Dispatcher & Schedule Controls -->
      <div class="card border-0 shadow-sm rounded-3 mb-4 bg-white overflow-hidden">
        <!-- Header & Action Row -->
        <div class="p-3 px-md-4 bg-light-subtle d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
          <div>
            <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
              <h5 class="fw-bold text-dark mb-0 d-flex align-items-center">
                <i class="bi bi-broadcast text-primary me-2"></i>Trek Reminder Dispatcher
              </h5>
              <span class="badge" :class="reminderConfig.is_active ? 'bg-success-subtle text-success border border-success' : 'bg-secondary-subtle text-secondary border'">
                <i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i>{{ reminderConfig.is_active ? 'Scheduler Active' : 'Scheduler Paused' }}
              </span>
              <span class="badge" :class="reminderConfig.smtp_enabled && reminderConfig.smtp_user ? 'bg-success-subtle text-success border border-success' : 'bg-primary-subtle text-primary border border-primary'">
                <i class="bi bi-envelope-check me-1"></i>{{ reminderConfig.smtp_enabled && reminderConfig.smtp_user ? 'Gmail SMTP Live' : 'Email Archive Active' }}
              </span>
            </div>
            <p class="text-muted small mb-0">
              Trigger instant notifications or configure automated daily departure alerts for booked trekkers.
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="d-flex align-items-center gap-2 flex-wrap flex-shrink-0">
            <button
              class="btn btn-primary rounded-pill px-3 py-2 small shadow-sm d-flex align-items-center gap-2"
              @click="sendRemindersNow"
              :disabled="sendingNow"
            >
              <span v-if="sendingNow" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bi bi-lightning-charge-fill text-warning"></i>
              <span class="fw-semibold">{{ sendingNow ? 'Dispatching...' : 'Dispatch Reminders Now' }}</span>
            </button>
            <button
              class="btn btn-outline-success rounded-pill px-3 py-2 small d-flex align-items-center gap-2"
              @click="openCustomModal"
            >
              <i class="bi bi-megaphone"></i>
              <span class="fw-semibold">Compose Notice</span>
            </button>
          </div>
        </div>

        <!-- Schedule & Delivery Settings Form -->
        <div class="p-3 px-md-4">
          <form @submit.prevent="saveReminderConfig">
            <div class="row g-3 align-items-end">
              <!-- Scheduler Active Toggle -->
              <div class="col-sm-6 col-lg-3">
                <label class="form-label small fw-semibold text-secondary mb-1">Daily Automated Scheduler</label>
                <div class="form-check form-switch p-2 bg-light rounded-3 border d-flex align-items-center justify-content-between ps-3 pe-3 mb-0">
                  <label class="form-check-label small fw-semibold text-dark mb-0" for="schedulerSwitch" style="cursor: pointer;">
                    <i class="bi bi-clock-history text-primary me-1"></i>{{ reminderConfig.is_active ? 'Active' : 'Paused' }}
                  </label>
                  <input class="form-check-input ms-2" type="checkbox" id="schedulerSwitch" v-model="reminderConfig.is_active" />
                </div>
              </div>

              <!-- Trigger Time -->
              <div class="col-sm-6 col-lg-2">
                <label class="form-label small fw-semibold text-secondary mb-1">Trigger Time</label>
                <input type="time" class="form-control form-control-sm" v-model="reminderConfig.scheduled_time" required />
              </div>

              <!-- Departure Window -->
              <div class="col-sm-6 col-lg-2">
                <label class="form-label small fw-semibold text-secondary mb-1">Departure Window</label>
                <select class="form-select form-select-sm" v-model.number="reminderConfig.days_before">
                  <option :value="1">1 Day Prior</option>
                  <option :value="2">2 Days Prior (Standard)</option>
                  <option :value="3">3 Days Prior</option>
                  <option :value="5">5 Days Prior</option>
                </select>
              </div>

              <!-- Delivery Channel -->
              <div class="col-sm-6 col-lg-3">
                <label class="form-label small fw-semibold text-secondary mb-1">Delivery Channel</label>
                <select class="form-select form-select-sm" v-model="reminderConfig.channel">
                  <option value="Email">Email (Gmail SMTP & In-App Server Archive)</option>
                  <option value="SMS">SMS / Text Notification Log</option>
                </select>
              </div>

              <!-- Save Settings Button -->
              <div class="col-12 col-lg-2">
                <button type="submit" class="btn btn-sm btn-outline-primary rounded-pill w-100 py-2 fw-semibold d-flex align-items-center justify-content-center" :disabled="savingConfig">
                  <span v-if="savingConfig" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-check2 me-1"></i>Save Settings
                </button>
              </div>
            </div>

            <!-- Email Delivery Configuration Bar -->
            <div class="mt-3 pt-3 border-top d-flex flex-wrap align-items-center justify-content-between gap-2">
              <div class="d-flex align-items-center gap-3">
                <div class="form-check form-switch mb-0">
                  <input class="form-check-input" type="checkbox" id="smtpSwitch" v-model="reminderConfig.smtp_enabled" />
                  <label class="form-check-label small fw-semibold text-dark" for="smtpSwitch" style="cursor: pointer;">
                    Live Gmail SMTP Delivery
                  </label>
                </div>
                <span class="small text-muted d-none d-sm-inline">
                  {{ reminderConfig.smtp_enabled ? 'Delivering directly to recipient Gmail inboxes.' : 'Reminders are archived to server archive & trekker inbox.' }}
                </span>
              </div>

              <button
                v-if="reminderConfig.smtp_enabled"
                type="button"
                class="btn btn-sm btn-link text-decoration-none p-0 text-primary small fw-semibold"
                @click="showSmtpFields = !showSmtpFields"
              >
                <i :class="showSmtpFields ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" class="me-1"></i>{{ showSmtpFields ? 'Hide SMTP Credentials' : 'Configure SMTP Credentials' }}
              </button>
            </div>

            <!-- Expandable SMTP Credentials Card -->
            <div v-if="reminderConfig.smtp_enabled && showSmtpFields" class="row g-2 mt-2 p-3 bg-light rounded-3 border small">
              <div class="col-md-4">
                <label class="form-label mb-1 text-secondary fw-semibold">Gmail Sender Account</label>
                <input type="email" class="form-control form-control-sm bg-white" v-model="reminderConfig.smtp_user" placeholder="your-email@gmail.com" />
              </div>
              <div class="col-md-3">
                <label class="form-label mb-1 text-secondary fw-semibold">App Password</label>
                <input type="password" class="form-control form-control-sm bg-white" v-model="reminderConfig.smtp_pass" :placeholder="reminderConfig.has_smtp_password ? '•••••••• (Saved)' : '16-char code'" />
              </div>
              <div class="col-md-5">
                <label class="form-label mb-1 text-secondary fw-semibold">Test Live Delivery</label>
                <div class="input-group input-group-sm">
                  <input type="email" class="form-control bg-white" v-model="testEmailRecipient" placeholder="Recipient email address..." />
                  <button class="btn btn-outline-primary" type="button" @click="sendTestLiveEmail" :disabled="testingEmail || !testEmailRecipient">
                    <span v-if="testingEmail" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-send me-1"></i>Send Test
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>

      <!-- Unified Activity & Delivery Logs Card with Sub-Tabs -->
      <div class="card border-0 shadow-sm rounded-3 mb-4 bg-white">
        <div class="card-header bg-white py-2 px-3 border-bottom d-flex flex-wrap justify-content-between align-items-center gap-2">
          <ul class="nav nav-pills small gap-1">
            <li class="nav-item">
              <button
                class="nav-link rounded-pill py-1 px-3"
                :class="{ active: logsSubTab === 'logs' }"
                @click="logsSubTab = 'logs'"
                type="button"
              >
                <i class="bi bi-journal-text me-1"></i>Dispatch History ({{ notificationLogs.length }})
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link rounded-pill py-1 px-3"
                :class="{ active: logsSubTab === 'emails' }"
                @click="logsSubTab = 'emails'"
                type="button"
              >
                <i class="bi bi-envelope-paper me-1"></i>Delivered Emails Archive ({{ sentEmailsList.length }})
              </button>
            </li>
          </ul>

          <button
            class="btn btn-sm btn-outline-secondary rounded-pill px-3 py-1 small"
            @click="logsSubTab === 'logs' ? fetchReminderLogs() : fetchSentEmails()"
            type="button"
          >
            <i class="bi bi-arrow-clockwise me-1"></i>Refresh
          </button>
        </div>

        <div class="card-body p-0">
          <!-- SUB-TAB 1: Notification Logs Table -->
          <div v-if="logsSubTab === 'logs'">
            <div class="table-responsive" v-if="notificationLogs.length > 0">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light small">
                  <tr>
                    <th class="ps-3">Date & Time</th>
                    <th>Target Trek Route</th>
                    <th>Subject & Message</th>
                    <th>Recipients</th>
                    <th>Dispatch Mode</th>
                    <th>Channel</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody class="small">
                  <tr v-for="l in notificationLogs" :key="l.id">
                    <td class="ps-3 text-muted text-nowrap">{{ l.created_at }}</td>
                    <td>
                      <div class="fw-semibold text-dark">{{ l.trek_name }}</div>
                      <div class="small text-muted">By: {{ l.sent_by }}</div>
                    </td>
                    <td>
                      <div class="fw-bold text-dark">{{ l.subject }}</div>
                      <div class="small text-muted text-truncate" style="max-width: 280px;">{{ l.message }}</div>
                    </td>
                    <td><span class="badge bg-secondary">{{ l.recipient_count }} trekkers</span></td>
                    <td>
                      <span
                        class="badge"
                        :class="{
                          'bg-primary': l.dispatch_type === 'Instant',
                          'bg-info text-dark': l.dispatch_type === 'Automated Daily',
                          'bg-warning text-dark': l.dispatch_type === 'Scheduled Later'
                        }"
                      >
                        {{ l.dispatch_type }}
                      </span>
                      <div v-if="l.scheduled_for" class="small text-muted mt-1">For: {{ l.scheduled_for }}</div>
                    </td>
                    <td><span class="small">{{ l.channel }}</span></td>
                    <td>
                      <span
                        class="badge"
                        :class="l.status === 'Sent' ? 'bg-success' : 'bg-secondary'"
                      >{{ l.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-4 px-3">
              <div class="d-inline-flex align-items-center justify-content-center bg-primary-subtle text-primary rounded-circle mb-2" style="width: 44px; height: 44px;">
                <i class="bi bi-clock-history fs-4"></i>
              </div>
              <h6 class="fw-bold text-dark mb-1">No Dispatch History Recorded</h6>
              <p class="text-muted small mb-3">All scheduled and manual trek reminder events will be logged here with timestamps and recipient counts.</p>
              <button class="btn btn-sm btn-primary rounded-pill px-4 shadow-sm" @click="sendRemindersNow" :disabled="sendingNow">
                <span v-if="sendingNow" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-lightning-charge me-1"></i>Dispatch Reminders Now
              </button>
            </div>
          </div>

          <!-- SUB-TAB 2: Delivered Emails Archive Table -->
          <div v-else-if="logsSubTab === 'emails'">
            <div class="table-responsive" v-if="sentEmailsList.length > 0">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light small">
                  <tr>
                    <th class="ps-3">Dispatched Timestamp</th>
                    <th>Archive File</th>
                    <th>Message Preview / Snippet</th>
                    <th>File Size</th>
                    <th class="text-end pe-3">Action</th>
                  </tr>
                </thead>
                <tbody class="small">
                  <tr v-for="e in sentEmailsList" :key="e.filename">
                    <td class="ps-3 text-muted text-nowrap">{{ e.created_at }}</td>
                    <td class="fw-semibold text-primary">
                      <i class="bi bi-file-text me-1"></i>{{ e.filename }}
                    </td>
                    <td class="text-muted text-truncate" style="max-width: 320px;">
                      {{ e.snippet }}
                    </td>
                    <td class="text-nowrap">{{ formatBytes(e.size_bytes) }}</td>
                    <td class="text-end pe-3">
                      <button class="btn btn-sm btn-outline-primary rounded-pill px-3 py-1 small" @click="viewEmailContent(e.filename)">
                        <i class="bi bi-eye me-1"></i>View Full Email
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-5 px-3">
              <div class="d-inline-flex align-items-center justify-content-center bg-success-subtle text-success rounded-circle mb-3" style="width: 52px; height: 52px;">
                <i class="bi bi-envelope-check fs-3"></i>
              </div>
              <h6 class="fw-bold text-dark mb-1">Delivered Emails Archive Is Empty</h6>
              <p class="text-muted small mb-0">Whenever reminder emails are dispatched to registered trekkers, formatted message transcripts are archived here for inspection.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- POP-UP MODAL: EMAIL CONTENT VIEWER -->
    <div class="modal fade" id="viewEmailModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">
              <i class="bi bi-envelope-open-fill text-primary me-2"></i>Email Message Inspector
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4 bg-white">
            <div class="mb-3 d-flex justify-content-between align-items-center">
              <span class="badge bg-secondary">{{ activeEmailFilename }}</span>
              <span class="small text-muted">Formatted Server Log / MIME Message</span>
            </div>
            <pre class="p-3 bg-light border rounded-3 small text-dark" style="white-space: pre-wrap; font-family: 'SFMono-Regular', Consolas, Menlo, monospace; max-height: 450px; overflow-y: auto;">{{ activeEmailContent }}</pre>
          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- POP-UP MODAL: CUSTOM ANNOUNCEMENT COMPOSER -->
    <!-- ============================================================= -->
    <div class="modal fade" id="customNotifModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">
              <i class="bi bi-megaphone-fill text-success me-2"></i>Compose Trek Notice / Announcement
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="submitCustomNotification">
            <div class="modal-body p-4">
              <!-- Target Trek Selection -->
              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Target Trek Route</label>
                <select class="form-select" v-model="customForm.trek_id">
                  <option :value="null">📢 Broadcast to All Active Expeditions (All Confirmed Trekkers)</option>
                  <option v-for="t in allTreks" :key="t.id" :value="t.id">
                    🏔️ {{ t.name }} ({{ t.location }} - Starts {{ t.start_date }})
                  </option>
                </select>
                <div class="form-text small">Select a specific trek route or broadcast to all active expeditions.</div>
              </div>

              <!-- Subject Line -->
              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Notification Subject</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="customForm.subject"
                  placeholder="e.g. Packing Advisory: Waterproof Jackets & Sturdy Hiking Boots Required"
                  required
                />
              </div>

              <!-- Message Body -->
              <div class="mb-3">
                <label class="form-label small fw-semibold text-dark">Message / Special Instructions Body</label>
                <textarea
                  class="form-control"
                  rows="4"
                  v-model="customForm.message"
                  placeholder="Write instructions, meeting point guidelines, weather alerts, or general notices..."
                  required
                ></textarea>
              </div>

              <div class="row g-3">
                <!-- Delivery Channel -->
                <div class="col-md-6">
                  <label class="form-label small fw-semibold text-dark">Delivery Channel</label>
                  <select class="form-select" v-model="customForm.channel">
                    <option value="Email">Email (Primary / Gmail SMTP & Server Log)</option>
                    <option value="SMS">SMS Notice Log</option>
                  </select>
                </div>

                <!-- Timing Mode -->
                <div class="col-md-6">
                  <label class="form-label small fw-semibold text-dark">Dispatch Timing</label>
                  <div class="d-flex gap-3 pt-2">
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="radio"
                        id="timingNow"
                        value="Instant"
                        v-model="customForm.dispatch_type"
                      />
                      <label class="form-check-label small fw-semibold" for="timingNow">
                        🚀 Send Immediately
                      </label>
                    </div>
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="radio"
                        id="timingLater"
                        value="Scheduled Later"
                        v-model="customForm.dispatch_type"
                      />
                      <label class="form-check-label small fw-semibold" for="timingLater">
                        🕒 Schedule for Later
                      </label>
                    </div>
                  </div>
                </div>

                <!-- Scheduled Date / Time (shown when 'Scheduled Later' selected) -->
                <div class="col-md-12" v-if="customForm.dispatch_type === 'Scheduled Later'">
                  <label class="form-label small fw-semibold text-dark">
                    <i class="bi bi-calendar-event me-1 text-primary"></i>Schedule Execution Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    class="form-control"
                    v-model="customForm.scheduled_for"
                    required
                  />
                  <div class="form-text small">The notification will be queued and scheduled for this exact timestamp.</div>
                </div>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-success rounded-pill px-4" :disabled="sendingCustom">
                <span v-if="sendingCustom" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-send-fill me-1"></i>
                {{ customForm.dispatch_type === 'Instant' ? 'Send Immediately' : 'Confirm Schedule' }}
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

const activeTab = ref('reports')
const logsSubTab = ref('logs')

// Tab 1 state
const bookings = ref([])
const reportsList = ref([])
const generating = ref(false)
const downloadingFile = ref(null)
const successMsg = ref('')
const errorMsg = ref('')
const latestPdfFile = ref('')

// Tab 2 state: Reminders & Scheduler
const reminderConfig = ref({
  scheduled_time: '08:00',
  days_before: 2,
  channel: 'Email',
  webhook_url: '',
  is_active: true
})
const notificationLogs = ref([])
const allTreks = ref([])
const showSmtpFields = ref(false)
const savingConfig = ref(false)
const sendingNow = ref(false)
const sendingCustom = ref(false)

const customForm = ref({
  trek_id: null,
  subject: '',
  message: '',
  channel: 'Email',
  dispatch_type: 'Instant',
  scheduled_for: ''
})

const testEmailRecipient = ref('')
const testingEmail = ref(false)
const sentEmailsList = ref([])
const activeEmailFilename = ref('')
const activeEmailContent = ref('')
const dispatchFeedback = ref(null)

let customModalInstance = null
let viewEmailModalInstance = null

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const fetchBookings = async () => {
  try {
    const res = await api.get('/admin/bookings')
    bookings.value = res.data.bookings || []
  } catch (err) {
    console.error(err)
  }
}

const fetchReportsList = async () => {
  try {
    const res = await api.get('/admin/reports/list')
    reportsList.value = res.data.reports || []
    if (reportsList.value.length > 0 && !latestPdfFile.value) {
      const pdf = reportsList.value.find(r => r.type === 'PDF')
      if (pdf) latestPdfFile.value = pdf.filename
    }
  } catch (err) {
    console.error(err)
  }
}

const fetchTreks = async () => {
  try {
    const res = await api.get('/admin/treks')
    allTreks.value = res.data.treks || []
  } catch (err) {
    console.error(err)
  }
}

const fetchReminderConfig = async () => {
  try {
    const res = await api.get('/admin/reminders/config')
    if (res.data.config) {
      reminderConfig.value = res.data.config
      if (!['Email', 'SMS'].includes(reminderConfig.value.channel)) {
        reminderConfig.value.channel = 'Email'
      }
    }
  } catch (err) {
    console.error(err)
  }
}

const fetchReminderLogs = async () => {
  try {
    const res = await api.get('/admin/reminders/logs')
    notificationLogs.value = res.data.logs || []
  } catch (err) {
    console.error(err)
  }
}

const downloadReport = async (filename) => {
  if (!filename) return
  downloadingFile.value = filename
  try {
    const res = await api.get(`/admin/reports/download/${filename}`, {
      responseType: 'blob'
    })
    const isPdf = filename.endsWith('.pdf')
    const blob = new Blob([res.data], { type: isPdf ? 'application/pdf' : 'text/html' })
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  } catch (err) {
    errorMsg.value = `Failed to download ${filename}. Please try again.`
  } finally {
    downloadingFile.value = null
  }
}

const generateReport = async () => {
  generating.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    const res = await api.post('/admin/reports/generate')
    const pdfFile = res.data.pdf_file
    successMsg.value = res.data.message || 'Monthly activity report (PDF) generated successfully!'
    if (pdfFile) {
      latestPdfFile.value = pdfFile
      await downloadReport(pdfFile)
    }
    await fetchReportsList()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to generate PDF report. Please try again.'
  } finally {
    generating.value = false
  }
}

// =============================================================================
// REMINDERS & SCHEDULER ACTIONS
// =============================================================================

const saveReminderConfig = async () => {
  savingConfig.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    const res = await api.put('/admin/reminders/config', reminderConfig.value)
    successMsg.value = res.data.message || 'Schedule configuration updated successfully!'
    if (res.data.config) reminderConfig.value = res.data.config
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to save reminder schedule.'
  } finally {
    savingConfig.value = false
  }
}

const sendRemindersNow = async () => {
  sendingNow.value = true
  successMsg.value = ''
  errorMsg.value = ''
  dispatchFeedback.value = null
  try {
    const res = await api.post('/admin/reminders/send-now')
    successMsg.value = res.data.message || 'Reminders dispatched successfully!'
    dispatchFeedback.value = res.data
    await fetchReminderLogs()
    await fetchSentEmails()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to dispatch reminders.'
  } finally {
    sendingNow.value = false
  }
}

const fetchSentEmails = async () => {
  try {
    const res = await api.get('/admin/reminders/sent-emails')
    sentEmailsList.value = res.data.emails || []
  } catch (err) {
    console.error(err)
  }
}

const viewEmailContent = async (filename) => {
  try {
    const res = await api.get(`/admin/reminders/sent-emails/${encodeURIComponent(filename)}`)
    activeEmailFilename.value = res.data.filename
    activeEmailContent.value = res.data.content
    const modalEl = document.getElementById('viewEmailModal')
    if (modalEl) {
      viewEmailModalInstance = Modal.getOrCreateInstance(modalEl)
      viewEmailModalInstance.show()
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to load email content.'
  }
}

const sendTestLiveEmail = async () => {
  if (!testEmailRecipient.value) return
  testingEmail.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    const res = await api.post('/admin/reminders/test-live-email', {
      email: testEmailRecipient.value
    })
    successMsg.value = res.data.message || `Test email dispatched to ${testEmailRecipient.value}!`
    await fetchSentEmails()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'SMTP delivery failed. Please verify credentials.'
  } finally {
    testingEmail.value = false
  }
}

const openCustomModal = () => {
  customForm.value = {
    trek_id: null,
    subject: '',
    message: '',
    channel: 'Email',
    dispatch_type: 'Instant',
    scheduled_for: ''
  }
  const modalEl = document.getElementById('customNotifModal')
  if (modalEl) {
    customModalInstance = Modal.getOrCreateInstance(modalEl)
    customModalInstance.show()
  }
}

const submitCustomNotification = async () => {
  sendingCustom.value = true
  successMsg.value = ''
  errorMsg.value = ''
  dispatchFeedback.value = null
  try {
    const res = await api.post('/admin/reminders/custom', customForm.value)
    customModalInstance?.hide()
    successMsg.value = res.data.message || 'Custom notification dispatched successfully!'
    dispatchFeedback.value = res.data
    await fetchReminderLogs()
    await fetchSentEmails()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to dispatch custom notification.'
  } finally {
    sendingCustom.value = false
  }
}

onMounted(() => {
  fetchBookings()
  fetchReportsList()
  fetchTreks()
  fetchReminderConfig()
  fetchReminderLogs()
  fetchSentEmails()
})
</script>
