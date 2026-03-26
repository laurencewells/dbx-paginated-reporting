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

// ---- Reports (for dropdown) ------------------------------------------------

const { data: reports } = useQuery({
  queryKey: computed(() => ['project-reports', activeProjectId.value]),
  queryFn: () => apiGet<ProjectReport[]>(`/api/v1/projects/${activeProjectId.value}/reports`),
  enabled: computed(() => !!activeProjectId.value),
})

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

// ---- Selected schedule (for executions panel) ------------------------------

const selectedScheduleId = ref<string | null>(null)

// ---- Execution history (all runs for the project) --------------------------

const { data: allExecutions, isLoading: executionsLoading } = useQuery({
  queryKey: computed(() => ['executions', activeProjectId.value]),
  queryFn: () =>
    apiGet<ScheduleExecution[]>('/api/v1/schedules/executions', { project_id: activeProjectId.value }),
  enabled: computed(() => !!activeProjectId.value),
  refetchInterval: 10000,
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

// ---- Create / Edit modal ---------------------------------------------------

const showModal = ref(false)
const editingSchedule = ref<Schedule | null>(null)
const isSubmitting = ref(false)

// Form fields
const form = ref({
  name: '',
  template_id: '',
  cron_expression: '',
  is_active: true,
  useSimple: true,
  simpleEvery: 1,
  simpleInterval: 'day' as Interval,
  simpleTime: '09:00',
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
  }
  showModal.value = true
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
      })
    }
    showModal.value = false
  } finally {
    isSubmitting.value = false
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
                <td class="text-muted small">{{ s.created_by }}</td>
                <td>
                  <span class="badge rounded-pill" :class="s.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ s.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="text-end text-nowrap" @click.stop>
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
                <th>Error</th>
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
                <td class="small text-danger text-truncate" style="max-width: 250px" :title="e.error_message ?? ''">
                  {{ e.error_message ?? '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Create / Edit Modal -->
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
