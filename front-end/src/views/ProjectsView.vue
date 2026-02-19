<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'
import {
  useListProjectsApiV1ProjectsGet,
  useCreateProjectApiV1ProjectsPost,
  useDeleteProjectApiV1ProjectsProjectIdDelete,
  useUpdateProjectApiV1ProjectsProjectIdPut,
  getListProjectsApiV1ProjectsGetQueryKey,
  useListSharesApiV1ProjectsProjectIdSharesGet,
  useCreateShareApiV1ProjectsProjectIdSharesPost,
  useDeleteShareApiV1ProjectsProjectIdSharesShareIdDelete,
  getListSharesApiV1ProjectsProjectIdSharesGetQueryKey,
} from '@/api/generated/projects/projects'
import { useGetMe } from '@/api/generated/default/default'
import type { Project } from '@/api/generated'

const queryClient = useQueryClient()
const router = useRouter()
const projectsStore = useProjectsStore()
const toastStore = useToastStore()

const invalidateProjects = () =>
  queryClient.invalidateQueries({ queryKey: getListProjectsApiV1ProjectsGetQueryKey() })

// -- Current user -------------------------------------------------------------
const { data: me } = useGetMe()
const isOwner = computed(() =>
  !!activeProject.value && !!me.value && activeProject.value.user_email === me.value.email
)

// -- Projects query -----------------------------------------------------------
const { data: projects, isLoading } = useListProjectsApiV1ProjectsGet()

const activeProject = computed<Project | null>(() =>
  projects.value?.find((p) => p.id === projectsStore.activeProjectId) ?? null
)

// -- Mutations ----------------------------------------------------------------
const { mutateAsync: createProjectMutation } = useCreateProjectApiV1ProjectsPost({
  mutation: { onSuccess: invalidateProjects },
})

const { mutateAsync: deleteProjectMutation } = useDeleteProjectApiV1ProjectsProjectIdDelete({
  mutation: { onSuccess: invalidateProjects },
})

const { mutateAsync: updateProjectMutation } = useUpdateProjectApiV1ProjectsProjectIdPut({
  mutation: { onSuccess: invalidateProjects },
})

// -- Shares -------------------------------------------------------------------
const sharesProjectId = computed(() => activeProject.value?.id ?? '')
const { data: shares } = useListSharesApiV1ProjectsProjectIdSharesGet(sharesProjectId, {
  query: { enabled: computed(() => !!activeProject.value && !activeProject.value.is_global) },
})

const invalidateShares = () => {
  if (activeProject.value) {
    queryClient.invalidateQueries({
      queryKey: getListSharesApiV1ProjectsProjectIdSharesGetQueryKey(activeProject.value.id),
    })
  }
}

const { mutateAsync: createShareMutation } = useCreateShareApiV1ProjectsProjectIdSharesPost({
  mutation: { onSuccess: invalidateShares },
})

const { mutateAsync: deleteShareMutation } = useDeleteShareApiV1ProjectsProjectIdSharesShareIdDelete({
  mutation: { onSuccess: invalidateShares },
})

// -- Create project modal -----------------------------------------------------
const showCreateModal = ref(false)
const newProjectName = ref('')
const isCreating = ref(false)

async function createProject() {
  if (!newProjectName.value.trim()) {
    toastStore.warning('Please enter a project name')
    return
  }
  if (isCreating.value) return
  isCreating.value = true
  try {
    const created = await createProjectMutation({ data: { name: newProjectName.value.trim() } })
    projectsStore.setActiveProject(created.id)
    toastStore.success(`Created project "${created.name}"`)
    newProjectName.value = ''
    showCreateModal.value = false
  } finally {
    isCreating.value = false
  }
}

// -- Delete project modal -----------------------------------------------------
const showDeleteModal = ref(false)
const pendingDeleteId = ref<string | null>(null)
const pendingDeleteName = computed(() =>
  projects.value?.find((p) => p.id === pendingDeleteId.value)?.name ?? ''
)

function promptDelete(id: string) {
  pendingDeleteId.value = id
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!pendingDeleteId.value) return
  const id = pendingDeleteId.value
  showDeleteModal.value = false
  pendingDeleteId.value = null
  try {
    await deleteProjectMutation({ projectId: id })
    if (projectsStore.activeProjectId === id) projectsStore.setActiveProject(null)
    toastStore.success('Project deleted')
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to delete project')
  }
}

// -- Rename -------------------------------------------------------------------
const editingNameId = ref<string | null>(null)
const editingNameValue = ref('')

function startRename(project: Project) {
  editingNameId.value = project.id
  editingNameValue.value = project.name
}

async function saveRename() {
  if (!editingNameId.value || !editingNameValue.value.trim()) return
  try {
    await updateProjectMutation({
      projectId: editingNameId.value,
      data: { name: editingNameValue.value.trim() },
    })
    toastStore.success('Project renamed')
    editingNameId.value = null
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to rename project')
  }
}

// -- Lock / unlock ------------------------------------------------------------
async function toggleLock(project: Project) {
  try {
    await updateProjectMutation({
      projectId: project.id,
      data: { is_locked: !project.is_locked },
    })
    toastStore.success(project.is_locked ? 'Project unlocked' : 'Project locked')
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to update project')
  }
}

// -- Global toggle ------------------------------------------------------------
async function toggleGlobal(project: Project) {
  try {
    await updateProjectMutation({
      projectId: project.id,
      data: { is_global: !project.is_global },
    })
    toastStore.success(project.is_global ? 'Project is now private' : 'Project is now global')
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to update project')
  }
}

// -- Share modal --------------------------------------------------------------
const showShareModal = ref(false)
const newShareEmail = ref('')
const isSharing = ref(false)

async function createShare() {
  if (!activeProject.value || !newShareEmail.value.trim()) return
  if (isSharing.value) return
  isSharing.value = true
  try {
    await createShareMutation({
      projectId: activeProject.value.id,
      data: { shared_with_email: newShareEmail.value.trim() },
    })
    toastStore.success(`Shared with ${newShareEmail.value.trim()}`)
    newShareEmail.value = ''
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to share')
  } finally {
    isSharing.value = false
  }
}

async function removeShare(shareId: string) {
  if (!activeProject.value) return
  try {
    await deleteShareMutation({ projectId: activeProject.value.id, shareId })
    toastStore.success('Share removed')
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to remove share')
  }
}

// -- Open project -------------------------------------------------------------
function openProject(project: Project) {
  projectsStore.setActiveProject(project.id)
  router.push('/data-structures')
}
</script>

<template>
  <div class="projects-view">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="bi bi-folder2-open me-2 text-primary"></i>
        Projects
      </h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="bi bi-plus-lg me-1"></i>
        New Project
      </button>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2">Loading projects...</p>
    </div>

    <div v-else-if="!projects?.length" class="text-center py-5">
      <div class="empty-state">
        <i class="bi bi-folder-plus"></i>
        <h5>No projects yet</h5>
        <p class="text-muted">Create your first project to organise your structures and templates.</p>
        <button class="btn btn-primary" @click="showCreateModal = true">
          <i class="bi bi-plus-lg me-1"></i>
          Create Project
        </button>
      </div>
    </div>

    <div v-else class="row">
      <!-- Project list -->
      <div class="col-md-5">
        <div class="card">
          <div class="card-header"><h6 class="mb-0">Your Projects</h6></div>
          <div class="card-body p-0">
            <div
              v-for="project in projects"
              :key="project.id"
              class="project-item"
              :class="{ active: activeProject?.id === project.id, 'global-project': project.is_global }"
              @click="projectsStore.setActiveProject(project.id)"
            >
              <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center gap-2 flex-grow-1 overflow-hidden">
                  <i :class="['flex-shrink-0', 'bi', project.is_global ? 'bi-globe2 text-success' : 'bi-folder2']"></i>
                  <template v-if="editingNameId === project.id">
                    <input
                      v-model="editingNameValue"
                      class="form-control form-control-sm"
                      @keyup.enter="saveRename"
                      @keyup.esc="editingNameId = null"
                      @click.stop
                    />
                    <button class="btn btn-sm btn-success flex-shrink-0" @click.stop="saveRename">
                      <i class="bi bi-check"></i>
                    </button>
                  </template>
                  <template v-else>
                    <strong class="text-truncate">{{ project.name }}</strong>
                    <span v-if="project.is_global" class="badge bg-success flex-shrink-0">Global</span>
                    <i v-else-if="project.is_locked" class="bi bi-lock-fill text-warning flex-shrink-0" title="Locked"></i>
                  </template>
                </div>
                <div class="d-flex align-items-center gap-1 flex-shrink-0 ms-2">
                  <button
                    class="btn btn-sm btn-outline-primary"
                    title="Open project"
                    @click.stop="openProject(project)"
                  >
                    <i class="bi bi-box-arrow-in-right"></i>
                  </button>
                  <button
                    v-if="!project.is_global && me?.email === project.user_email"
                    class="btn btn-sm btn-outline-danger"
                    @click.stop="promptDelete(project.id)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
              <div class="small text-muted mt-1">
                <i class="bi bi-person me-1"></i>{{ project.is_global ? 'Available to everyone' : project.user_email }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Project detail -->
      <div class="col-md-7">
        <div v-if="!activeProject" class="card">
          <div class="card-body empty-state">
            <i class="bi bi-hand-index-thumb"></i>
            <p class="mb-0">Select a project from the list</p>
          </div>
        </div>

        <template v-else>
          <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i :class="['bi', 'me-2', activeProject.is_global ? 'bi-globe2 text-success' : 'bi-folder2']"></i>
                {{ activeProject.name }}
                <span v-if="activeProject.is_global" class="badge bg-success ms-2">Global</span>
              </h6>
              <div class="d-flex gap-2">
                <template v-if="isOwner && !activeProject.is_global">
                  <button class="btn btn-sm btn-outline-secondary" @click="startRename(activeProject)">
                    <i class="bi bi-pencil me-1"></i>Rename
                  </button>
                  <button
                    class="btn btn-sm"
                    :class="activeProject.is_locked ? 'btn-warning' : 'btn-outline-warning'"
                    @click="toggleLock(activeProject)"
                  >
                    <i :class="['bi', activeProject.is_locked ? 'bi-unlock' : 'bi-lock', 'me-1']"></i>
                    {{ activeProject.is_locked ? 'Unlock' : 'Lock' }}
                  </button>
                  <button
                    class="btn btn-sm btn-outline-success"
                    @click="toggleGlobal(activeProject)"
                    title="Make this project visible to all users"
                  >
                    <i class="bi bi-globe2 me-1"></i>Make Global
                  </button>
                </template>
                <template v-if="isOwner && activeProject.is_global">
                  <button
                    class="btn btn-sm btn-success"
                    @click="toggleGlobal(activeProject)"
                    title="Revert to a private project"
                  >
                    <i class="bi bi-globe2 me-1"></i>Remove Global
                  </button>
                </template>
                <button class="btn btn-sm btn-primary" @click="openProject(activeProject)">
                  <i class="bi bi-box-arrow-in-right me-1"></i>Open
                </button>
              </div>
            </div>
            <div class="card-body">
              <div v-if="activeProject.is_global" class="alert alert-success py-2 mb-2 small">
                <i class="bi bi-globe2 me-2"></i>
                This project is visible to all users. Individual sharing is bypassed.
              </div>
              <div class="row text-muted small">
                <div class="col-6">
                  <i class="bi bi-calendar me-1"></i>
                  Created: {{ new Date(activeProject.created_at).toLocaleDateString() }}
                </div>
                <div class="col-6">
                  <i class="bi bi-clock me-1"></i>
                  Updated: {{ new Date(activeProject.updated_at).toLocaleDateString() }}
                </div>
              </div>
            </div>
          </div>

          <!-- Sharing (hidden for global projects) -->
          <div v-if="!activeProject.is_global" class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i class="bi bi-people me-2"></i>
                Sharing
              </h6>
              <button v-if="isOwner" class="btn btn-sm btn-outline-primary" @click="showShareModal = true">
                <i class="bi bi-person-plus me-1"></i>Share
              </button>
            </div>
            <div class="card-body">
              <div class="mb-2 small">
                <i class="bi bi-person-fill text-primary me-1"></i>
                <strong>{{ activeProject.user_email }}</strong>
                <span class="badge bg-primary ms-1">Owner</span>
              </div>
              <div
                v-for="share in (shares ?? [])"
                :key="share.id"
                class="d-flex justify-content-between align-items-center py-1"
              >
                <div class="small">
                  <i class="bi bi-person me-1"></i>
                  {{ share.shared_with_email }}
                </div>
                <button v-if="isOwner" class="btn btn-sm btn-outline-danger" @click="removeShare(share.id)">
                  <i class="bi bi-x"></i>
                </button>
              </div>
              <div v-if="!shares?.length" class="text-muted small">
                Not shared with anyone yet.
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">New Project</h5>
            <button type="button" class="btn-close" @click="showCreateModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Project Name</label>
              <input
                v-model="newProjectName"
                type="text"
                class="form-control"
                placeholder="e.g., Q1 Sales Reports"
                @keyup.enter="!isCreating && createProject()"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isCreating" @click="createProject">
              <span v-if="isCreating" class="spinner-border spinner-border-sm me-1" role="status"></span>
              Create
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showDeleteModal = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>Delete Project
            </h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            Delete <strong>{{ pendingDeleteName }}</strong>? All structures and templates in this project will also be deleted. This cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDelete">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div v-if="showShareModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showShareModal = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-person-plus me-2"></i>Share Project
            </h5>
            <button type="button" class="btn-close" @click="showShareModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Email address</label>
              <input
                v-model="newShareEmail"
                type="email"
                class="form-control"
                placeholder="colleague@databricks.com"
                @keyup.enter="!isSharing && createShare()"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showShareModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isSharing" @click="createShare">
              <span v-if="isSharing" class="spinner-border spinner-border-sm me-1" role="status"></span>
              Share
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s ease;
}
.project-item:hover { background: #f8f9fa; }
.project-item.active {
  background: #e3f2fd;
  border-left: 3px solid var(--bs-primary);
}
.project-item.global-project {
  background: #f0faf4;
}
.project-item.global-project.active {
  background: #d4edda;
  border-left: 3px solid var(--bs-success);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.empty-state i { font-size: 2.5rem; display: block; margin-bottom: 0.5rem; }
</style>
