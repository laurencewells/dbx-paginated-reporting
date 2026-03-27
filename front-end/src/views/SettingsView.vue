<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { useGetMe } from '@/api/generated/default/default'
import {
  listSmtpConnectionsApiV1SmtpConnectionsGet,
  createSmtpConnectionApiV1SmtpConnectionsPost,
  updateSmtpConnectionApiV1SmtpConnectionsConnectionIdPut,
  deleteSmtpConnectionApiV1SmtpConnectionsConnectionIdDelete,
} from '@/api/generated/smtp-connections/smtp-connections'
import type { SmtpConnectionPublic, SmtpConnectionCreate, SmtpConnectionUpdate } from '@/api/generated'

const toastStore = useToastStore()
const queryClient = useQueryClient()
const { data: me } = useGetMe()
const isAdmin = computed(() => me.value?.is_admin ?? false)

const providerOptions = [
  { value: 'gsuite', label: 'Google Workspace (Gmail)' },
  { value: 'sendgrid', label: 'SendGrid' },
]

const providerDefaults: Record<string, { smtp_host: string; smtp_port: number }> = {
  gsuite: { smtp_host: 'smtp.gmail.com', smtp_port: 587 },
}

const isSmtpProvider = computed(() => form.value.provider !== 'sendgrid')

// ---- Connections query -----------------------------------------------------

const connectionsQueryKey = ['smtp-connections']

const { data: connections, isLoading } = useQuery({
  queryKey: connectionsQueryKey,
  queryFn: () => listSmtpConnectionsApiV1SmtpConnectionsGet(),
})

function invalidateConnections() {
  queryClient.invalidateQueries({ queryKey: connectionsQueryKey })
}

// ---- Modal state -----------------------------------------------------------

const showModal = ref(false)
const editingConnection = ref<SmtpConnectionPublic | null>(null)
const isSubmitting = ref(false)

const form = ref({
  name: '',
  provider: 'sendgrid',
  from_email: '',
  smtp_host: '',
  smtp_port: 587,
  username: '',
  password: '',
})

function applyProviderDefaults() {
  if (form.value.provider === 'sendgrid') {
    form.value.smtp_host = ''
    form.value.smtp_port = 587
    form.value.username = ''
  } else {
    const defaults = providerDefaults[form.value.provider]
    if (defaults) {
      form.value.smtp_host = defaults.smtp_host
      form.value.smtp_port = defaults.smtp_port
    }
  }
}

function openCreate() {
  editingConnection.value = null
  form.value = { name: '', provider: 'sendgrid', from_email: '', smtp_host: '', smtp_port: 587, username: '', password: '' }
  showModal.value = true
}

function openEdit(c: SmtpConnectionPublic) {
  editingConnection.value = c
  form.value = {
    name: c.name,
    provider: c.provider,
    from_email: c.from_email,
    smtp_host: c.smtp_host,
    smtp_port: c.smtp_port,
    username: c.username,
    password: '',
  }
  showModal.value = true
}

// ---- Mutations -------------------------------------------------------------

const createMutation = useMutation({
  mutationFn: (data: SmtpConnectionCreate) => createSmtpConnectionApiV1SmtpConnectionsPost(data),
  onSuccess: () => { invalidateConnections(); toastStore.success('SMTP connection created') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to create SMTP connection')
  },
})

const updateMutation = useMutation({
  mutationFn: ({ id, body }: { id: string; body: SmtpConnectionUpdate }) =>
    updateSmtpConnectionApiV1SmtpConnectionsConnectionIdPut(id, body),
  onSuccess: () => { invalidateConnections(); toastStore.success('SMTP connection updated') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to update SMTP connection')
  },
})

const deleteMutation = useMutation({
  mutationFn: (id: string) => deleteSmtpConnectionApiV1SmtpConnectionsConnectionIdDelete(id),
  onSuccess: () => { invalidateConnections(); toastStore.success('SMTP connection deleted') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to delete SMTP connection')
  },
})

async function submitForm() {
  if (!form.value.name.trim() || !form.value.from_email.trim()) {
    toastStore.warning('Name and From Email are required')
    return
  }
  if (!editingConnection.value && !form.value.password.trim()) {
    toastStore.warning('Password / API Key is required')
    return
  }
  if (isSubmitting.value) return
  isSubmitting.value = true
  try {
    if (editingConnection.value) {
      const body: SmtpConnectionUpdate = {
        name: form.value.name.trim(),
        from_email: form.value.from_email.trim(),
        smtp_host: form.value.smtp_host.trim(),
        smtp_port: form.value.smtp_port,
        username: form.value.username.trim(),
      }
      if (form.value.password.trim()) {
        body.password = form.value.password.trim()
      }
      await updateMutation.mutateAsync({ id: editingConnection.value.id, body })
    } else {
      const body: SmtpConnectionCreate = {
        name: form.value.name.trim(),
        provider: form.value.provider,
        from_email: form.value.from_email.trim(),
        smtp_host: form.value.smtp_host.trim(),
        smtp_port: form.value.smtp_port,
        username: form.value.username.trim(),
        password: form.value.password.trim(),
      }
      await createMutation.mutateAsync(body)
    }
    showModal.value = false
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="settings-view">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="bi bi-gear me-2 text-primary"></i>
        Settings
      </h2>
    </div>

    <!-- SMTP Connections -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0"><i class="bi bi-envelope-at me-1"></i>SMTP Connections</h6>
        <button v-if="isAdmin" class="btn btn-sm btn-primary" @click="openCreate">
          <i class="bi bi-plus-lg me-1"></i>New Connection
        </button>
      </div>

      <div v-if="!isAdmin" class="alert alert-info m-3 mb-0">
        <i class="bi bi-info-circle me-2"></i>
        SMTP connections are managed by workspace admins. Contact your admin to add or modify connections.
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else-if="!connections?.length" class="text-center py-5 text-muted">
        <i class="bi bi-envelope-slash d-block mb-2" style="font-size: 2rem; opacity: 0.4"></i>
        <span class="small">No SMTP connections configured yet.</span>
        <span v-if="!isAdmin" class="small d-block">Contact your workspace admin to set one up.</span>
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Provider</th>
              <th>From</th>
              <th>Delivery</th>
              <th>Created by</th>
              <th v-if="isAdmin" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in connections" :key="c.id">
              <td class="fw-medium">{{ c.name }}</td>
              <td>
                <span class="badge bg-light text-dark border">{{ c.provider }}</span>
              </td>
              <td class="text-muted small">{{ c.from_email }}</td>
              <td class="text-muted small font-monospace">
                <span v-if="c.provider === 'sendgrid'">API</span>
                <span v-else>{{ c.smtp_host }}:{{ c.smtp_port }}</span>
              </td>
              <td class="text-muted small">{{ c.created_by }}</td>
              <td v-if="isAdmin" class="text-end text-nowrap">
                <button class="btn btn-sm btn-outline-secondary me-1" @click="openEdit(c)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteMutation.mutate(c.id)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="showModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showModal = false">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-envelope-at me-2"></i>
              {{ editingConnection ? 'Edit Connection' : 'New Connection' }}
            </h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold">Name <span class="text-danger">*</span></label>
                <input v-model="form.name" type="text" class="form-control" placeholder="e.g., Company SendGrid" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Provider</label>
                <select v-model="form.provider" class="form-select" @change="applyProviderDefaults">
                  <option v-for="p in providerOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">From Email <span class="text-danger">*</span></label>
                <input v-model="form.from_email" type="email" class="form-control" placeholder="noreply@yourcompany.com" />
              </div>
              <template v-if="isSmtpProvider">
                <div class="col-md-4">
                  <label class="form-label fw-semibold">SMTP Host</label>
                  <input v-model="form.smtp_host" type="text" class="form-control font-monospace" />
                </div>
                <div class="col-md-2">
                  <label class="form-label fw-semibold">Port</label>
                  <input v-model.number="form.smtp_port" type="number" class="form-control" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Username</label>
                  <input v-model="form.username" type="text" class="form-control" />
                </div>
              </template>
              <div class="col-md-6">
                <label class="form-label fw-semibold">
                  {{ isSmtpProvider ? 'Password' : 'API Key' }}
                  <span v-if="!editingConnection" class="text-danger">*</span>
                </label>
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  :placeholder="editingConnection ? 'Leave blank to keep existing' : (isSmtpProvider ? 'Enter password' : 'Enter SendGrid API key')"
                />
                <div v-if="editingConnection" class="form-text">Leave blank to keep the current credential.</div>
                <div v-else-if="!isSmtpProvider" class="form-text">
                  Find your API key in the SendGrid dashboard under Settings &rsaquo; API Keys.
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isSubmitting" @click="submitForm">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              {{ editingConnection ? 'Save Changes' : 'Create Connection' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  max-width: 1000px;
}
</style>
