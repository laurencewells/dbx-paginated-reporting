<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import axios from 'axios'
import CronDescription from '@/components/CronDescription.vue'

const projectsStore = useProjectsStore()
const toastStore = useToastStore()
const queryClient = useQueryClient()

const activeProjectId = computed(() => projectsStore.activeProjectId)

// ---- Tabs ------------------------------------------------------------------

const activeTab = ref<'schedules' | 'send-lists'>('schedules')

// ---- API helpers -----------------------------------------------------------

async function apiGet<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const { data } = await axios.get(url, { params })
  return data
}
async function apiPost<T>(url: string, body: unknown): Promise<T> {
  const { data } = await axios.post(url, body)
  return data
}
async function apiPut<T>(url: string, body: unknown): Promise<T> {
  const { data } = await axios.put(url, body)
  return data
}
async function apiDelete(url: string): Promise<void> {
  await axios.delete(url)
}

// ---- Types -----------------------------------------------------------------

interface Schedule {
  id: string
  name: string
  project_id: string
  structure_id: string
  template_id: string
  cron_expression: string
  is_active: boolean
  created_by: string
  created_at: string
  updated_at: string
  send_list_ids: string[]
}

interface ScheduleExecution {
  id: string
  schedule_id: string
  status: 'pending' | 'running' | 'success' | 'failed'
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  created_at: string
}

interface ProjectReport {
  template_id: string
  template_name: string
  page_size: string
  structure_id: string
  structure_name: string
}

interface SmtpConnection {
  id: string
  name: string
  provider: string
}

interface EmailSendList {
  id: string
  name: string
  project_id: string
  smtp_connection_id: string
  emails: string[]
  created_by: string
  created_at: string
  updated_at: string
}

// ---- Reports (for dropdown) ------------------------------------------------

const { data: reports } = useQuery({
  queryKey: computed(() => ['project-reports', activeProjectId.value]),
  queryFn: () => apiGet<ProjectReport[]>(`/api/v1/projects/${activeProjectId.value}/reports`),
  enabled: computed(() => !!activeProjectId.value),
})

// ---- SMTP connections (for send list dropdown) ----------------------------

const { data: smtpConnections } = useQuery({
  queryKey: ['smtp-connections'],
  queryFn: () => apiGet<SmtpConnection[]>('/api/v1/smtp-connections/'),
})

function smtpConnectionName(id: string) {
  return smtpConnections.value?.find((c) => c.id === id)?.name ?? id
}

// ---- Schedules query -------------------------------------------------------

const schedulesQueryKey = computed(() => ['schedules', activeProjectId.value])

const { data: schedules, isLoading: schedulesLoading } = useQuery({
  queryKey: schedulesQueryKey,
  queryFn: () => apiGet<Schedule[]>('/api/v1/schedules/', { project_id: activeProjectId.value }),
  enabled: computed(() => !!activeProjectId.value),
})

function invalidateSchedules() {
  queryClient.invalidateQueries({ queryKey: schedulesQueryKey.value })
}

// ---- Send Lists query ------------------------------------------------------

const sendListsQueryKey = computed(() => ['send-lists', activeProjectId.value])

const { data: sendLists, isLoading: sendListsLoading } = useQuery({
  queryKey: sendListsQueryKey,
  queryFn: () => apiGet<EmailSendList[]>('/api/v1/send-lists/', { project_id: activeProjectId.value }),
  enabled: computed(() => !!activeProjectId.value),
})

function invalidateSendLists() {
  queryClient.invalidateQueries({ queryKey: sendListsQueryKey.value })
}

function sendListName(id: string) {
  return sendLists.value?.find((sl) => sl.id === id)?.name ?? id
}

// ---- Selected schedule (for executions panel) ------------------------------

const selectedScheduleId = ref<string | null>(null)

// ---- Execution history (all runs for the project) --------------------------

const { data: allExecutions, isLoading: executionsLoading } = useQuery({
  queryKey: computed(() => ['executions', activeProjectId.value]),
  queryFn: () =>
    apiGet<ScheduleExecution[]>('/api/v1/schedules/executions', { project_id: activeProjectId.value }),
  enabled: computed(() => !!activeProjectId.value),
})

const filteredExecutions = computed(() => {
  if (!allExecutions.value) return []
  if (!selectedScheduleId.value) return allExecutions.value
  return allExecutions.value.filter((e) => e.schedule_id === selectedScheduleId.value)
})

// ---- Simple schedule builder -----------------------------------------------

type Interval = 'minute' | 'hour' | 'day' | 'week' | 'month'

const intervalOptions: { label: string; value: Interval }[] = [
  { label: 'Minute(s)', value: 'minute' },
  { label: 'Hour(s)', value: 'hour' },
  { label: 'Day(s)', value: 'day' },
  { label: 'Week(s)', value: 'week' },
  { label: 'Month(s)', value: 'month' },
]

function buildCron(every: number, interval: Interval, time: string): string {
  const [hh, mm] = time.split(':').map(Number)
  switch (interval) {
    case 'minute': return `*/${every} * * * *`
    case 'hour':   return `0 */${every} * * *`
    case 'day':    return `${mm} ${hh} */${every} * *`
    case 'week':   return `${mm} ${hh} * * 0/${every}`
    case 'month':  return `${mm} ${hh} 1 */${every} *`
    default:       return '0 9 * * *'
  }
}

// ---- Download render -------------------------------------------------------

const downloadingId = ref<string | null>(null)

async function downloadRender(s: Schedule) {
  if (downloadingId.value) return
  downloadingId.value = s.id
  const report = reports.value?.find((r) => r.template_id === s.template_id)
  const isPdf = report?.page_size !== 'email'
  const url = `/api/v1/templates/${s.template_id}/${isPdf ? 'render-pdf' : 'render'}`
  try {
    const response = await axios.get(url, { responseType: 'blob' })
    const blob = new Blob([response.data], { type: isPdf ? 'application/pdf' : 'text/html' })
    const disposition: string = response.headers['content-disposition'] ?? ''
    const filename = disposition.match(/filename="([^"]+)"/)?.[1] ?? `report.${isPdf ? 'pdf' : 'html'}`
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
  } catch {
    toastStore.error('Failed to render report for download')
  } finally {
    downloadingId.value = null
  }
}

// ---- Create / Edit schedule modal ------------------------------------------

const showModal = ref(false)
const editingSchedule = ref<Schedule | null>(null)
const isSubmitting = ref(false)

const form = ref({
  name: '',
  template_id: '',
  cron_expression: '',
  is_active: true,
  useSimple: true,
  simpleEvery: 1,
  simpleInterval: 'day' as Interval,
  simpleTime: '09:00',
  send_list_ids: [] as string[],
})

const selectedFormReport = computed(() =>
  reports.value?.find((r) => r.template_id === form.value.template_id) ?? null
)

function openCreate() {
  editingSchedule.value = null
  form.value = {
    name: '',
    template_id: '',
    cron_expression: '',
    is_active: true,
    useSimple: true,
    simpleEvery: 1,
    simpleInterval: 'day',
    simpleTime: '09:00',
    send_list_ids: [],
  }
  showModal.value = true
}

function openEdit(s: Schedule) {
  editingSchedule.value = s
  form.value = {
    name: s.name,
    template_id: s.template_id,
    cron_expression: s.cron_expression,
    is_active: s.is_active,
    useSimple: false,
    simpleEvery: 1,
    simpleInterval: 'day',
    simpleTime: '09:00',
    send_list_ids: [...(s.send_list_ids ?? [])],
  }
  showModal.value = true
}

function toggleSendList(id: string) {
  const idx = form.value.send_list_ids.indexOf(id)
  if (idx === -1) form.value.send_list_ids.push(id)
  else form.value.send_list_ids.splice(idx, 1)
}

function resolvedCron(): string {
  if (form.value.useSimple) {
    return buildCron(form.value.simpleEvery, form.value.simpleInterval, form.value.simpleTime)
  }
  return form.value.cron_expression.trim()
}

const createMutation = useMutation({
  mutationFn: (body: object) => apiPost<Schedule>('/api/v1/schedules/', body),
  onSuccess: () => { invalidateSchedules(); toastStore.success('Schedule created') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to create schedule')
  },
})

const updateMutation = useMutation({
  mutationFn: ({ id, body }: { id: string; body: object }) =>
    apiPut<Schedule>(`/api/v1/schedules/${id}`, body),
  onSuccess: () => { invalidateSchedules(); toastStore.success('Schedule updated') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to update schedule')
  },
})

const deleteMutation = useMutation({
  mutationFn: (id: string) => apiDelete(`/api/v1/schedules/${id}`),
  onSuccess: () => { invalidateSchedules(); toastStore.success('Schedule deleted') },
  onError: () => toastStore.error('Failed to delete schedule'),
})

const triggerMutation = useMutation({
  mutationFn: (id: string) => apiPost(`/api/v1/schedules/${id}/trigger`, {}),
  onSuccess: (_data, id) => {
    toastStore.success('Execution triggered')
    selectedScheduleId.value = id
    queryClient.invalidateQueries({ queryKey: ['executions', activeProjectId.value] })
  },
  onError: () => toastStore.error('Failed to trigger execution'),
})

async function submitForm() {
  if (!form.value.name.trim() || !form.value.template_id) {
    toastStore.warning('Please fill in all required fields')
    return
  }
  if (isSubmitting.value) return
  isSubmitting.value = true
  try {
    const cron = resolvedCron()
    if (editingSchedule.value) {
      await updateMutation.mutateAsync({
        id: editingSchedule.value.id,
        body: {
          name: form.value.name.trim(),
          cron_expression: cron,
          is_active: form.value.is_active,
          expected_updated_at: editingSchedule.value.updated_at,
          send_list_ids: form.value.send_list_ids,
        },
      })
    } else {
      await createMutation.mutateAsync({
        name: form.value.name.trim(),
        project_id: activeProjectId.value,
        structure_id: selectedFormReport.value!.structure_id,
        template_id: form.value.template_id,
        cron_expression: cron,
        is_active: form.value.is_active,
        send_list_ids: form.value.send_list_ids,
      })
    }
    showModal.value = false
  } finally {
    isSubmitting.value = false
  }
}

// ---- Send List modal -------------------------------------------------------

const showSendListModal = ref(false)
const editingSendList = ref<EmailSendList | null>(null)
const isSendListSubmitting = ref(false)
const newEmailInput = ref('')

const sendListForm = ref({
  name: '',
  smtp_connection_id: '',
  emails: [] as string[],
})

function openCreateSendList() {
  editingSendList.value = null
  sendListForm.value = { name: '', smtp_connection_id: '', emails: [] }
  newEmailInput.value = ''
  showSendListModal.value = true
}

function openEditSendList(sl: EmailSendList) {
  editingSendList.value = sl
  sendListForm.value = { name: sl.name, smtp_connection_id: sl.smtp_connection_id, emails: [...sl.emails] }
  newEmailInput.value = ''
  showSendListModal.value = true
}

function addEmail() {
  const email = newEmailInput.value.trim()
  if (!email) return
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    toastStore.warning(`"${email}" is not a valid email address`)
    return
  }
  if (sendListForm.value.emails.includes(email)) return
  sendListForm.value.emails.push(email)
  newEmailInput.value = ''
}

function removeEmail(email: string) {
  sendListForm.value.emails = sendListForm.value.emails.filter((e) => e !== email)
}

function handleEmailKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addEmail()
  }
}

const createSendListMutation = useMutation({
  mutationFn: (body: object) => apiPost<EmailSendList>('/api/v1/send-lists/', body),
  onSuccess: () => { invalidateSendLists(); toastStore.success('Send list created') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to create send list')
  },
})

const updateSendListMutation = useMutation({
  mutationFn: ({ id, body }: { id: string; body: object }) =>
    apiPut<EmailSendList>(`/api/v1/send-lists/${id}`, body),
  onSuccess: () => { invalidateSendLists(); toastStore.success('Send list updated') },
  onError: (err: unknown) => {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to update send list')
  },
})

const deleteSendListMutation = useMutation({
  mutationFn: (id: string) => apiDelete(`/api/v1/send-lists/${id}`),
  onSuccess: () => { invalidateSendLists(); toastStore.success('Send list deleted') },
  onError: () => toastStore.error('Failed to delete send list'),
})

async function submitSendListForm() {
  if (!sendListForm.value.name.trim() || !sendListForm.value.smtp_connection_id) {
    toastStore.warning('Name and SMTP connection are required')
    return
  }
  if (isSendListSubmitting.value) return
  isSendListSubmitting.value = true
  try {
    const body = {
      name: sendListForm.value.name.trim(),
      smtp_connection_id: sendListForm.value.smtp_connection_id,
      emails: sendListForm.value.emails,
      project_id: activeProjectId.value,
    }
    if (editingSendList.value) {
      await updateSendListMutation.mutateAsync({ id: editingSendList.value.id, body })
    } else {
      await createSendListMutation.mutateAsync(body)
    }
    showSendListModal.value = false
  } finally {
    isSendListSubmitting.value = false
  }
}

// ---- Helpers ---------------------------------------------------------------

const statusBadge: Record<string, string> = {
  pending: 'bg-secondary',
  running: 'bg-primary',
  success: 'bg-success',
  failed: 'bg-danger',
}

function fmtDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleString()
}

function fmtDuration(start: string | null, end: string | null) {
  if (!start || !end) return '—'
  const ms = new Date(end).getTime() - new Date(start).getTime()
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`
}

function structureName(id: string) {
  return reports.value?.find((r) => r.structure_id === id)?.structure_name ?? id
}

const selectedSchedule = computed(
  () => schedules.value?.find((s) => s.id === selectedScheduleId.value) ?? null,
)
</script>

<template>
  <div class="schedules-view">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="bi bi-clock-history me-2 text-primary"></i>
        Schedules
      </h2>
    </div>

    <!-- No active project warning -->
    <div v-if="!activeProjectId" class="alert alert-info">
      <i class="bi bi-info-circle me-2"></i>
      Select an active project from the sidebar to manage its schedules.
    </div>

    <template v-else>
      <!-- Privilege warning -->
      <div class="alert alert-warning d-flex align-items-start gap-2 mb-3">
        <i class="bi bi-exclamation-triangle-fill flex-shrink-0 mt-1"></i>
        <div>
          <strong>Service principal access required.</strong>
          The app's service principal must have <code>SELECT</code> privilege on all Unity Catalog
          tables used by a report's data structure. Without this, scheduled executions will fail.
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-3">
        <li class="nav-item">
          <button class="nav-link" :class="{ active: activeTab === 'schedules' }" @click="activeTab = 'schedules'">
            <i class="bi bi-calendar-check me-1"></i>Schedules
          </button>
        </li>
        <li class="nav-item">
          <button class="nav-link" :class="{ active: activeTab === 'send-lists' }" @click="activeTab = 'send-lists'">
            <i class="bi bi-envelope-check me-1"></i>Send Lists
          </button>
        </li>
      </ul>

      <!-- ===== Schedules tab ===== -->
      <template v-if="activeTab === 'schedules'">
        <!-- Schedules card -->
        <div class="card mb-3">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0"><i class="bi bi-calendar-check me-1"></i>Schedules</h6>
            <button class="btn btn-sm btn-primary" @click="openCreate">
              <i class="bi bi-plus-lg me-1"></i>New Schedule
            </button>
          </div>

          <div v-if="schedulesLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div v-else-if="!schedules?.length" class="text-center py-5 text-muted">
            <i class="bi bi-calendar-x d-block mb-2" style="font-size: 2rem; opacity: 0.4"></i>
            <span class="small">No schedules yet. Click <strong>New Schedule</strong> to get started.</span>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Name</th>
                  <th>Report</th>
                  <th>Cron</th>
                  <th>Send Lists</th>
                  <th>Created by</th>
                  <th>Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="s in schedules"
                  :key="s.id"
                  class="schedule-row"
                  :class="{ 'table-primary': selectedScheduleId === s.id }"
                  @click="selectedScheduleId = s.id"
                >
                  <td class="fw-medium">{{ s.name }}</td>
                  <td class="text-muted small">{{ structureName(s.structure_id) }}</td>
                  <td>
                    <CronDescription :cron="s.cron_expression" />
                    <div><code class="text-muted" style="font-size: 0.7rem">{{ s.cron_expression }}</code></div>
                  </td>
                  <td>
                    <span v-if="!s.send_list_ids?.length" class="text-muted small">—</span>
                    <div v-else class="d-flex flex-wrap gap-1">
                      <span
                        v-for="slId in s.send_list_ids"
                        :key="slId"
                        class="badge bg-light text-dark border small"
                      >{{ sendListName(slId) }}</span>
                    </div>
                  </td>
                  <td class="text-muted small">{{ s.created_by }}</td>
                  <td>
                    <span class="badge rounded-pill" :class="s.is_active ? 'bg-success' : 'bg-secondary'">
                      {{ s.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="text-end text-nowrap" @click.stop>
                    <button
                      class="btn btn-sm btn-outline-success me-1"
                      title="Download render"
                      :disabled="downloadingId === s.id"
                      @click="downloadRender(s)"
                    >
                      <span v-if="downloadingId === s.id" class="spinner-border spinner-border-sm" role="status"></span>
                      <i v-else class="bi bi-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-primary me-1" title="Trigger now" @click="triggerMutation.mutate(s.id)">
                      <i class="bi bi-play-fill"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" title="Edit" @click="openEdit(s)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" title="Delete" @click="deleteMutation.mutate(s.id)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Execution history card -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-list-check me-1"></i>Execution History
              <span v-if="selectedSchedule" class="text-muted fw-normal ms-1 small">— filtered by {{ selectedSchedule.name }}</span>
              <span v-else class="text-muted fw-normal ms-1 small">— all schedules</span>
            </h6>
            <div class="d-flex align-items-center gap-2">
              <span v-if="selectedScheduleId" class="badge bg-light text-secondary border small" style="cursor:pointer" @click="selectedScheduleId = null">
                <i class="bi bi-x me-1"></i>Clear filter
              </span>
              <button
                class="btn btn-sm btn-outline-secondary"
                title="Refresh"
                @click="queryClient.invalidateQueries({ queryKey: ['executions', activeProjectId] })"
              >
                <i class="bi bi-arrow-clockwise"></i>
              </button>
            </div>
          </div>

          <div v-if="executionsLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div v-else-if="!filteredExecutions.length" class="text-center py-5 text-muted">
            <i class="bi bi-inbox d-block mb-2" style="font-size: 1.5rem; opacity: 0.4"></i>
            <span class="small">{{ selectedScheduleId ? 'No executions for this schedule yet.' : 'No executions recorded yet.' }}</span>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Schedule</th>
                  <th>Report</th>
                  <th>Started</th>
                  <th>Completed</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in filteredExecutions" :key="e.id">
                  <td class="fw-medium small">{{ schedules?.find(s => s.id === e.schedule_id)?.name ?? '—' }}</td>
                  <td class="text-muted small">{{ structureName(schedules?.find(s => s.id === e.schedule_id)?.structure_id ?? '') }}</td>
                  <td class="small text-nowrap">{{ fmtDate(e.started_at) }}</td>
                  <td class="small text-nowrap">{{ fmtDate(e.completed_at) }}</td>
                  <td class="small text-nowrap">{{ fmtDuration(e.started_at, e.completed_at) }}</td>
                  <td>
                    <span class="badge rounded-pill" :class="statusBadge[e.status] ?? 'bg-secondary'">
                      {{ e.status }}
                    </span>
                  </td>
                  <td class="small text-truncate" style="max-width: 250px" :title="e.error_message ?? ''">
                    <span v-if="e.error_message" :class="e.status === 'failed' ? 'text-danger' : 'text-muted'">
                      {{ e.error_message }}
                    </span>
                    <span v-else class="text-muted">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- ===== Send Lists tab ===== -->
      <template v-else>
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0"><i class="bi bi-envelope-check me-1"></i>Send Lists</h6>
            <button class="btn btn-sm btn-primary" @click="openCreateSendList">
              <i class="bi bi-plus-lg me-1"></i>New Send List
            </button>
          </div>

          <div v-if="!smtpConnections?.length" class="alert alert-info m-3 mb-0">
            <i class="bi bi-info-circle me-2"></i>
            No SMTP connections configured. Ask your workspace admin to add one in
            <a href="/settings" class="alert-link">Settings</a>.
          </div>

          <div v-if="sendListsLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div v-else-if="!sendLists?.length" class="text-center py-5 text-muted">
            <i class="bi bi-envelope-slash d-block mb-2" style="font-size: 2rem; opacity: 0.4"></i>
            <span class="small">No send lists yet. Create one to attach email recipients to a schedule.</span>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Name</th>
                  <th>SMTP Connection</th>
                  <th>Recipients</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sl in sendLists" :key="sl.id">
                  <td class="fw-medium">{{ sl.name }}</td>
                  <td class="text-muted small">{{ smtpConnectionName(sl.smtp_connection_id) }}</td>
                  <td>
                    <div class="d-flex flex-wrap gap-1">
                      <span
                        v-for="email in sl.emails.slice(0, 3)"
                        :key="email"
                        class="badge bg-light text-dark border small"
                      >{{ email }}</span>
                      <span v-if="sl.emails.length > 3" class="badge bg-secondary small">
                        +{{ sl.emails.length - 3 }} more
                      </span>
                      <span v-if="!sl.emails.length" class="text-muted small">No recipients</span>
                    </div>
                  </td>
                  <td class="text-end text-nowrap">
                    <button class="btn btn-sm btn-outline-secondary me-1" @click="openEditSendList(sl)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteSendListMutation.mutate(sl.id)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </template>

    <!-- Create / Edit Schedule Modal -->
    <div v-if="showModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showModal = false">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-clock me-2"></i>
              {{ editingSchedule ? 'Edit Schedule' : 'New Schedule' }}
            </h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <!-- Name -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Schedule Name <span class="text-danger">*</span></label>
              <input v-model="form.name" type="text" class="form-control" placeholder="e.g., Daily Customer Report" />
            </div>

            <!-- Report picker (only on create) -->
            <template v-if="!editingSchedule">
              <div class="mb-3">
                <label class="form-label fw-semibold">Report <span class="text-danger">*</span></label>
                <select v-model="form.template_id" class="form-select">
                  <option value="" disabled>Select a report…</option>
                  <option v-for="r in reports" :key="r.template_id" :value="r.template_id">
                    {{ r.template_name }} — {{ r.structure_name }}
                  </option>
                </select>
              </div>
            </template>

            <!-- Schedule builder -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Schedule</label>
              <div class="btn-group btn-group-sm mb-2 d-flex" style="max-width: 240px">
                <button
                  type="button"
                  class="btn"
                  :class="form.useSimple ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="form.useSimple = true"
                >Simple</button>
                <button
                  type="button"
                  class="btn"
                  :class="!form.useSimple ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="form.useSimple = false"
                >Cron</button>
              </div>

              <div v-if="form.useSimple" class="d-flex align-items-center gap-2 flex-wrap">
                <span class="text-muted">Every</span>
                <input
                  v-model.number="form.simpleEvery"
                  type="number"
                  min="1"
                  class="form-control form-control-sm"
                  style="width: 70px"
                />
                <select v-model="form.simpleInterval" class="form-select form-select-sm" style="width: 130px">
                  <option v-for="opt in intervalOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
                <template v-if="form.simpleInterval === 'day' || form.simpleInterval === 'week' || form.simpleInterval === 'month'">
                  <span class="text-muted">at</span>
                  <input v-model="form.simpleTime" type="time" class="form-control form-control-sm" style="width: 120px" />
                </template>
                <code class="text-muted small">→ {{ resolvedCron() }}</code>
              </div>

              <div v-else>
                <input
                  v-model="form.cron_expression"
                  type="text"
                  class="form-control font-monospace"
                  placeholder="e.g., 0 9 * * 1-5"
                />
                <div class="form-text">5-field cron: minute hour day month day_of_week</div>
              </div>
            </div>

            <!-- Send Lists -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Send Lists</label>
              <div v-if="!sendLists?.length" class="text-muted small">
                No send lists available for this project.
                <a href="#" @click.prevent="showModal = false; activeTab = 'send-lists'">Create one</a> first.
              </div>
              <div v-else class="border rounded p-2" style="max-height: 160px; overflow-y: auto">
                <div v-for="sl in sendLists" :key="sl.id" class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    :id="`sl-${sl.id}`"
                    :checked="form.send_list_ids.includes(sl.id)"
                    @change="toggleSendList(sl.id)"
                  />
                  <label class="form-check-label" :for="`sl-${sl.id}`">
                    {{ sl.name }}
                    <span class="text-muted small ms-1">({{ sl.emails.length }} recipients · {{ smtpConnectionName(sl.smtp_connection_id) }})</span>
                  </label>
                </div>
              </div>
              <div v-if="form.send_list_ids.length" class="mt-1 d-flex flex-wrap gap-1">
                <span
                  v-for="slId in form.send_list_ids"
                  :key="slId"
                  class="badge bg-primary"
                >{{ sendListName(slId) }}</span>
              </div>
            </div>

            <!-- Active toggle -->
            <div class="form-check form-switch mb-1">
              <input v-model="form.is_active" class="form-check-input" type="checkbox" id="scheduleActive" />
              <label class="form-check-label" for="scheduleActive">Active</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isSubmitting" @click="submitForm">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              {{ editingSchedule ? 'Save Changes' : 'Create Schedule' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit Send List Modal -->
    <div v-if="showSendListModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showSendListModal = false">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-envelope-check me-2"></i>
              {{ editingSendList ? 'Edit Send List' : 'New Send List' }}
            </h5>
            <button type="button" class="btn-close" @click="showSendListModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label fw-semibold">Name <span class="text-danger">*</span></label>
              <input v-model="sendListForm.name" type="text" class="form-control" placeholder="e.g., Finance Team" />
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">SMTP Connection <span class="text-danger">*</span></label>
              <select v-model="sendListForm.smtp_connection_id" class="form-select">
                <option value="" disabled>Select a connection…</option>
                <option v-for="c in smtpConnections" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Recipients</label>
              <div class="input-group mb-2">
                <input
                  v-model="newEmailInput"
                  type="email"
                  class="form-control"
                  placeholder="email@example.com"
                  @keydown="handleEmailKeydown"
                />
                <button class="btn btn-outline-secondary" type="button" @click="addEmail">
                  <i class="bi bi-plus-lg"></i> Add
                </button>
              </div>
              <div class="form-text mb-2">Press Enter or comma to add an email address.</div>
              <div v-if="sendListForm.emails.length" class="d-flex flex-wrap gap-1">
                <span
                  v-for="email in sendListForm.emails"
                  :key="email"
                  class="badge bg-light text-dark border d-flex align-items-center gap-1"
                >
                  {{ email }}
                  <button
                    type="button"
                    class="btn-close btn-close-sm"
                    style="font-size: 0.6rem"
                    @click="removeEmail(email)"
                  ></button>
                </span>
              </div>
              <div v-else class="text-muted small">No recipients added yet.</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showSendListModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isSendListSubmitting" @click="submitSendListForm">
              <span v-if="isSendListSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              {{ editingSendList ? 'Save Changes' : 'Create Send List' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedules-view {
  max-width: 1200px;
}
code {
  font-size: 0.8rem;
}
.schedule-row {
  cursor: pointer;
}
</style>
