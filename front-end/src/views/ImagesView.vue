<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useProjectsStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'
import {
  useListImagesApiV1ImagesGet,
  useUploadImageApiV1ImagesPost,
  useDeleteImageApiV1ImagesImageIdDelete,
  useUpdateImageApiV1ImagesImageIdPut,
  getListImagesApiV1ImagesGetQueryKey,
} from '@/api/generated/images/images'
import { useListProjectsApiV1ProjectsGet } from '@/api/generated/projects/projects'
import type { Image } from '@/api/generated'

const queryClient = useQueryClient()
const projectsStore = useProjectsStore()
const toastStore = useToastStore()

const projectId = computed(() => projectsStore.activeProjectId ?? '')

const { data: projects } = useListProjectsApiV1ProjectsGet()
const isLocked = computed(() => {
  const project = projects.value?.find((p) => p.id === projectsStore.activeProjectId)
  return !!project?.is_locked
})

const invalidateImages = () =>
  queryClient.invalidateQueries({ queryKey: getListImagesApiV1ImagesGetQueryKey({ project_id: projectId.value }) })

// -- Queries ------------------------------------------------------------------
const { data: images, isLoading } = useListImagesApiV1ImagesGet(
  computed(() => ({ project_id: projectId.value })),
  { query: { enabled: computed(() => !!projectId.value) } },
)

// -- Mutations ----------------------------------------------------------------
const { mutateAsync: uploadMutation } = useUploadImageApiV1ImagesPost({
  mutation: { onSuccess: invalidateImages },
})

const { mutateAsync: deleteMutation } = useDeleteImageApiV1ImagesImageIdDelete({
  mutation: { onSuccess: invalidateImages },
})

const { mutateAsync: updateMutation } = useUpdateImageApiV1ImagesImageIdPut({
  mutation: { onSuccess: invalidateImages },
})

// -- Upload -------------------------------------------------------------------
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFiles(files: FileList | null) {
  if (!files?.length || !projectId.value) return
  isUploading.value = true
  try {
    for (const file of Array.from(files)) {
      await uploadMutation({
        data: { file },
        params: { project_id: projectId.value },
      })
    }
    toastStore.success(`Uploaded ${files.length} image${files.length > 1 ? 's' : ''}`)
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Upload failed')
  } finally {
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function onFileChange(e: Event) {
  handleFiles((e.target as HTMLInputElement).files)
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  handleFiles(e.dataTransfer?.files ?? null)
}

// -- Delete -------------------------------------------------------------------
const showDeleteModal = ref(false)
const pendingDeleteImage = ref<Image | null>(null)

function promptDelete(image: Image) {
  pendingDeleteImage.value = image
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!pendingDeleteImage.value) return
  const name = pendingDeleteImage.value.filename
  try {
    await deleteMutation({ imageId: pendingDeleteImage.value.id })
    showDeleteModal.value = false
    pendingDeleteImage.value = null
    toastStore.success(`Deleted "${name}"`)
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to delete image')
  }
}

// -- Rename -------------------------------------------------------------------
const editingId = ref<string | null>(null)
const editingName = ref('')

function startRename(image: Image) {
  editingId.value = image.id
  editingName.value = image.filename
}

async function saveRename() {
  if (!editingId.value || !editingName.value.trim()) return
  try {
    await updateMutation({
      imageId: editingId.value,
      data: { filename: editingName.value.trim() },
    })
    toastStore.success('Image renamed')
    editingId.value = null
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toastStore.error(detail ?? 'Failed to rename image')
  }
}

// -- Helpers ------------------------------------------------------------------
function imageUrl(id: string): string {
  return `/api/v1/images/${id}/data`
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// -- Lightbox -----------------------------------------------------------------
const lightboxImage = ref<Image | null>(null)

// -- Copy URL -----------------------------------------------------------------
function copyUrl(image: Image) {
  const url = `/api/v1/images/${image.id}/data`
  navigator.clipboard.writeText(url)
  toastStore.success('URL copied to clipboard')
}
</script>

<template>
  <div class="images-view">
    <!-- No project selected -->
    <div v-if="!projectId" class="text-center py-5">
      <div class="empty-state">
        <i class="bi bi-folder-x"></i>
        <h5>No project selected</h5>
        <p class="text-muted">Select a project first to manage its images.</p>
        <router-link to="/projects" class="btn btn-primary">
          <i class="bi bi-folder2-open me-1"></i>Go to Projects
        </router-link>
      </div>
    </div>

    <template v-else>
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="mb-0">
          <i class="bi bi-images me-2 text-primary"></i>
          Image Gallery
          <span v-if="isLocked" class="badge bg-warning text-dark ms-2 fs-6">
            <i class="bi bi-lock-fill me-1"></i>Locked
          </span>
        </h2>
        <button v-if="!isLocked" class="btn btn-primary" :disabled="isUploading" @click="triggerUpload">
          <span v-if="isUploading" class="spinner-border spinner-border-sm me-1" role="status"></span>
          <i v-else class="bi bi-upload me-1"></i>
          Upload
        </button>
        <input
          ref="fileInput"
          type="file"
          multiple
          accept="image/jpeg,image/png,image/gif,image/webp,image/svg+xml"
          class="d-none"
          @change="onFileChange"
        />
      </div>

      <!-- Drop zone (hidden when locked) -->
      <div
        v-if="!isLocked"
        class="drop-zone mb-4"
        :class="{ dragging: isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
        @click="triggerUpload"
      >
        <i class="bi bi-cloud-arrow-up"></i>
        <p class="mb-0">Drag & drop images here or click to browse</p>
        <small class="text-muted">JPEG, PNG, GIF, WebP, SVG — max 2 MB each</small>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading images...</p>
      </div>

      <!-- Empty -->
      <div v-else-if="!images?.length" class="text-center py-5">
        <div class="empty-state">
          <i class="bi bi-image"></i>
          <h5>No images yet</h5>
          <p class="text-muted">Upload images to use in your report templates.</p>
        </div>
      </div>

      <!-- Gallery grid -->
      <div v-else class="row g-3">
        <div v-for="image in images" :key="image.id" class="col-6 col-md-4 col-lg-3">
          <div class="card image-card h-100">
            <div class="image-thumb" @click="lightboxImage = image">
              <img :src="imageUrl(image.id)" :alt="image.filename" loading="lazy" />
            </div>
            <div class="card-body p-2">
              <template v-if="editingId === image.id">
                <div class="input-group input-group-sm">
                  <input
                    v-model="editingName"
                    class="form-control"
                    @keyup.enter="saveRename"
                    @keyup.esc="editingId = null"
                  />
                  <button class="btn btn-success" @click="saveRename">
                    <i class="bi bi-check"></i>
                  </button>
                </div>
              </template>
              <template v-else>
                <div class="image-filename text-truncate" :title="image.filename">
                  {{ image.filename }}
                </div>
                <div class="d-flex justify-content-between align-items-center mt-1">
                  <small class="text-muted">{{ formatSize(image.size_bytes) }}</small>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary" title="Copy URL" @click="copyUrl(image)">
                      <i class="bi bi-link-45deg"></i>
                    </button>
                    <button class="btn btn-outline-secondary" title="Rename" :disabled="isLocked" @click="!isLocked && startRename(image)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" title="Delete" :disabled="isLocked" @click="!isLocked && promptDelete(image)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showDeleteModal = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>Delete Image
            </h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            Delete <strong>{{ pendingDeleteImage?.filename }}</strong>? This cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDelete">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="lightboxImage" class="lightbox" @click="lightboxImage = null">
      <button class="btn-close btn-close-white lightbox-close" @click="lightboxImage = null"></button>
      <img :src="imageUrl(lightboxImage.id)" :alt="lightboxImage.filename" @click.stop />
      <div class="lightbox-caption">{{ lightboxImage.filename }}</div>
    </div>
  </div>
</template>

<style scoped>
.drop-zone {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6c757d;
}
.drop-zone:hover,
.drop-zone.dragging {
  border-color: var(--bs-primary);
  background: #f0f7ff;
  color: var(--bs-primary);
}
.drop-zone i {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.image-card {
  transition: box-shadow 0.2s ease;
}
.image-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-thumb {
  height: 160px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  cursor: pointer;
  border-radius: 0.375rem 0.375rem 0 0;
}
.image-thumb img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-filename {
  font-size: 0.85rem;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.empty-state i {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}

.lightbox {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  z-index: 9999;
  cursor: pointer;
}
.lightbox img {
  max-width: 90vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 4px;
  cursor: default;
}
.lightbox-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
.lightbox-caption {
  color: white;
  margin-top: 1rem;
  font-size: 0.9rem;
}
</style>
