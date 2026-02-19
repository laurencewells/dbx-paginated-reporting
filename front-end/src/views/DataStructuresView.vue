<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useDataStructuresStore } from '@/stores/dataStructures'
import { useProjectsStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'
import {
  useListStructuresApiV1StructuresGet,
  useCreateStructureApiV1StructuresPost,
  useDeleteStructureApiV1StructuresStructureIdDelete,
  useUpdateStructureApiV1StructuresStructureIdPut,
  useBuildStructureApiV1StructuresStructureIdBuildPost,
  getListStructuresApiV1StructuresGetQueryKey,
  listCatalogsApiV1DiscoveryCatalogsGet,
  listSchemasApiV1DiscoveryCatalogsCatalogSchemasGet,
  listTablesApiV1DiscoveryCatalogsCatalogSchemasSchemaTablesGet,
  getTableColumnsApiV1DiscoveryCatalogsCatalogSchemasSchemaTablesTableColumnsGet,
} from '@/api/generated'
import type { CatalogInfo, SchemaInfo, TableInfo, ColumnInfo, StructureTable, StructureFieldOutput } from '@/api/generated'
import { useListProjectsApiV1ProjectsGet } from '@/api/generated/projects/projects'

const queryClient = useQueryClient()
const dataStore = useDataStructuresStore()
const projectsStore = useProjectsStore()
const toastStore = useToastStore()

// -- Structures query ---------------------------------------------------------

const { data: projects } = useListProjectsApiV1ProjectsGet()

const activeProjectId = computed(() => projectsStore.activeProjectId)
const hasProject = computed(() => !!activeProjectId.value)
const structuresParams = computed(() => ({ project_id: activeProjectId.value! }))

const { data: structures, isLoading: loadingStructures } = useListStructuresApiV1StructuresGet(
  structuresParams,
  { query: { enabled: hasProject } },
)

const isLocked = computed(() => {
  const project = projects.value?.find((p) => p.id === activeProjectId.value)
  return !!project?.is_locked
})

const activeStructure = computed(() =>
  structures.value?.find((s) => s.id === dataStore.activeStructureId) ?? null
)

// -- Mutations ----------------------------------------------------------------

const invalidateStructures = () =>
  queryClient.invalidateQueries({ queryKey: getListStructuresApiV1StructuresGetQueryKey(structuresParams) })

const { mutateAsync: createStructureMutation } = useCreateStructureApiV1StructuresPost({
  mutation: { onSuccess: invalidateStructures },
})

const { mutateAsync: deleteStructureMutation } = useDeleteStructureApiV1StructuresStructureIdDelete({
  mutation: { onSuccess: invalidateStructures },
})

const { mutateAsync: updateStructureMutation } = useUpdateStructureApiV1StructuresStructureIdPut({
  mutation: {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: getListStructuresApiV1StructuresGetQueryKey(structuresParams) }),
  },
})

const building = ref(false)
const { mutateAsync: buildStructureMutation } = useBuildStructureApiV1StructuresStructureIdBuildPost({
  mutation: {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: getListStructuresApiV1StructuresGetQueryKey(structuresParams) }),
  },
})

// -- New Structure Modal -------------------------------------------------------
const showNewStructureModal = ref(false)
const newStructureName = ref('')
const isCreatingStructure = ref(false)

// -- Delete confirm modal -------------------------------------------------------
const showDeleteStructureModal = ref(false)
const pendingDeleteId = ref<string | null>(null)
const pendingDeleteName = computed(() =>
  structures.value?.find((s) => s.id === pendingDeleteId.value)?.name ?? ''
)

function promptDeleteStructure(id: string) {
  pendingDeleteId.value = id
  showDeleteStructureModal.value = true
}

async function confirmDeleteStructure() {
  if (!pendingDeleteId.value) return
  const id = pendingDeleteId.value
  showDeleteStructureModal.value = false
  pendingDeleteId.value = null
  await deleteStructureMutation({ structureId: id })
  if (dataStore.activeStructureId === id) dataStore.setActiveStructure(null)
  toastStore.success('Structure deleted')
}

// -- Table + Column Picker Modal -----------------------------------------------
const showPickerModal = ref(false)
const catalogs = ref<CatalogInfo[]>([])
const schemas = ref<SchemaInfo[]>([])
const ucTables = ref<TableInfo[]>([])
const pickerColumns = ref<ColumnInfo[]>([])
const pickerCatalog = ref<string | null>(null)
const pickerSchema = ref<string | null>(null)
const pickerTable = ref<string | null>(null)
const pickerSelectedColumns = ref<Set<string>>(new Set())
const loadingCatalogs = ref(false)
const loadingSchemas = ref(false)
const loadingTables = ref(false)
const loadingColumns = ref(false)

const pickerFullName = computed(() => {
  if (!pickerCatalog.value || !pickerSchema.value || !pickerTable.value) return null
  return `${pickerCatalog.value}.${pickerSchema.value}.${pickerTable.value}`
})

const pickerSelectedCount = computed(() => pickerSelectedColumns.value.size)
const canSaveAndBuild = computed(() => !!pickerFullName.value && pickerSelectedCount.value > 0)

// -- Field icon map -----------------------------------------------------------
const fieldIcons: Record<string, string> = {
  string: 'bi-fonts', number: 'bi-123', boolean: 'bi-toggle-on',
  date: 'bi-calendar', array: 'bi-list-ul', object: 'bi-braces',
}
function getFieldIcon(type: string): string {
  return fieldIcons[type] || 'bi-question'
}

// -- Structure management -----------------------------------------------------

async function createStructure() {
  if (!newStructureName.value.trim()) {
    toastStore.warning('Please enter a structure name')
    return
  }
  if (isCreatingStructure.value) return
  isCreatingStructure.value = true
  try {
    const name = newStructureName.value.trim()
    if (!projectsStore.activeProjectId) {
      toastStore.warning('Please select a project first')
      return
    }
    const created = await createStructureMutation({
      data: {
        name,
        project_id: projectsStore.activeProjectId,
      },
    })
    dataStore.setActiveStructure(created.id)
    toastStore.success(`Created structure "${name}"`)
    newStructureName.value = ''
    showNewStructureModal.value = false
  } finally {
    isCreatingStructure.value = false
  }
}

function deleteStructure(id: string) {
  promptDeleteStructure(id)
}

function selectStructure(id: string) {
  dataStore.setActiveStructure(id)
}

// -- Picker modal -------------------------------------------------------------

async function openPickerModal() {
  showPickerModal.value = true
  pickerCatalog.value = null
  pickerSchema.value = null
  pickerTable.value = null
  pickerColumns.value = []
  pickerSelectedColumns.value = new Set()
  schemas.value = []
  ucTables.value = []

  if (activeStructure.value?.tables?.length) {
    const current = activeStructure.value.tables[0]
    const parts = current.full_name.split('.')
    if (parts.length === 3) {
      pickerCatalog.value = parts[0]
      pickerSchema.value = parts[1]
      pickerTable.value = parts[2]
    }
    pickerSelectedColumns.value = new Set(activeStructure.value.selected_columns ?? [])
  }

  if (catalogs.value.length === 0) {
    loadingCatalogs.value = true
    try {
      catalogs.value = (await listCatalogsApiV1DiscoveryCatalogsGet()) as unknown as CatalogInfo[]
    } catch {
      toastStore.error('Failed to load catalogs')
    } finally {
      loadingCatalogs.value = false
    }
  }

  if (pickerCatalog.value) await loadSchemas(pickerCatalog.value)
  if (pickerCatalog.value && pickerSchema.value) await loadTables(pickerCatalog.value, pickerSchema.value)
  if (pickerCatalog.value && pickerSchema.value && pickerTable.value) {
    await loadColumns(pickerCatalog.value, pickerSchema.value, pickerTable.value)
  }
}

async function loadSchemas(catalogName: string) {
  loadingSchemas.value = true
  schemas.value = []
  try {
    schemas.value = (await listSchemasApiV1DiscoveryCatalogsCatalogSchemasGet(catalogName)) as unknown as SchemaInfo[]
  } catch {
    toastStore.error('Failed to load schemas')
  } finally {
    loadingSchemas.value = false
  }
}

async function loadTables(catalogName: string, schemaName: string) {
  loadingTables.value = true
  ucTables.value = []
  try {
    ucTables.value = (await listTablesApiV1DiscoveryCatalogsCatalogSchemasSchemaTablesGet(catalogName, schemaName)) as unknown as TableInfo[]
  } catch {
    toastStore.error('Failed to load tables')
  } finally {
    loadingTables.value = false
  }
}

async function loadColumns(catalogName: string, schemaName: string, tableName: string) {
  loadingColumns.value = true
  pickerColumns.value = []
  try {
    pickerColumns.value = (await getTableColumnsApiV1DiscoveryCatalogsCatalogSchemasSchemaTablesTableColumnsGet(catalogName, schemaName, tableName)) as unknown as ColumnInfo[]
  } catch {
    toastStore.error('Failed to load columns')
  } finally {
    loadingColumns.value = false
  }
}

async function selectPickerCatalog(name: string) {
  pickerCatalog.value = name
  pickerSchema.value = null
  pickerTable.value = null
  pickerColumns.value = []
  pickerSelectedColumns.value = new Set()
  await loadSchemas(name)
}

async function selectPickerSchema(name: string) {
  pickerSchema.value = name
  pickerTable.value = null
  pickerColumns.value = []
  pickerSelectedColumns.value = new Set()
  await loadTables(pickerCatalog.value!, name)
}

async function selectPickerTable(name: string) {
  pickerTable.value = name
  pickerSelectedColumns.value = new Set()
  await loadColumns(pickerCatalog.value!, pickerSchema.value!, name)
}

function toggleColumn(colName: string) {
  if (pickerSelectedColumns.value.has(colName)) {
    pickerSelectedColumns.value.delete(colName)
  } else {
    pickerSelectedColumns.value.add(colName)
  }
  pickerSelectedColumns.value = new Set(pickerSelectedColumns.value)
}

function selectAllColumns() {
  pickerSelectedColumns.value = new Set(pickerColumns.value.map((c) => c.name))
}

function deselectAllColumns() {
  pickerSelectedColumns.value = new Set()
}

async function confirmSaveAndBuild() {
  if (!activeStructure.value || !pickerFullName.value || !pickerTable.value) return
  if (pickerSelectedCount.value === 0) {
    toastStore.warning('Select at least one column')
    return
  }

  const table: StructureTable = {
    full_name: pickerFullName.value,
    alias: pickerTable.value,
  }
  const columns = [...pickerSelectedColumns.value]
  const structureId = activeStructure.value.id

  showPickerModal.value = false
  building.value = true
  try {
    await updateStructureMutation({ structureId, data: { tables: [table], selected_columns: columns } })
    await buildStructureMutation({ structureId })
    toastStore.success('Structure saved and built — fields inferred from Unity Catalog')
  } catch (err: unknown) {
    const axiosDetail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    const detail = axiosDetail ?? (err instanceof Error ? err.message : 'Build failed')
    toastStore.error(detail)
  } finally {
    building.value = false
  }
}

// -- Column children expand/collapse ------------------------------------------
const expandedColumns = ref<Set<string>>(new Set())

function toggleExpanded(colName: string, e: Event) {
  e.preventDefault()
  e.stopPropagation()
  const next = new Set(expandedColumns.value)
  if (next.has(colName)) { next.delete(colName) } else { next.add(colName) }
  expandedColumns.value = next
}

// -- Column type helpers -------------------------------------------------------

function parseChildNames(typeText: string | null | undefined): string[] {
  if (!typeText) return []
  const t = typeText.trim().toLowerCase()
  let inner: string
  if (t.startsWith('struct<') && t.endsWith('>')) {
    inner = t.slice(7, -1)
  } else if (t.startsWith('array<struct<') && t.endsWith('>>')) {
    inner = t.slice(13, -2)
  } else {
    return []
  }
  // split on top-level commas only
  const parts: string[] = []
  let depth = 0, buf = ''
  for (const ch of inner) {
    if (ch === '<') { depth++; buf += ch }
    else if (ch === '>') { depth--; buf += ch }
    else if (ch === ',' && depth === 0) { parts.push(buf.trim()); buf = '' }
    else { buf += ch }
  }
  if (buf.trim()) parts.push(buf.trim())
  return parts.map(p => p.split(':')[0].trim()).filter(Boolean)
}

function columnTypeLabel(typeText: string | null | undefined, typeName: string): string {
  const t = (typeText ?? typeName).trim().toLowerCase()
  if (t.startsWith('array<struct<')) return 'ARRAY<STRUCT>'
  if (t.startsWith('array<')) return 'ARRAY'
  if (t.startsWith('struct<')) return 'STRUCT'
  if (t.startsWith('map<')) return 'MAP'
  return String(typeName).split('.').pop() ?? typeName
}

// -- Field tree rendering -----------------------------------------------------

function renderFieldTree(fields: StructureFieldOutput[], depth = 0): (StructureFieldOutput & { depth: number })[] {
  const result: (StructureFieldOutput & { depth: number })[] = []
  for (const field of fields) {
    result.push({ ...field, depth })
    const children = field.children as StructureFieldOutput[] | null | undefined
    if (children?.length) {
      result.push(...renderFieldTree(children, depth + 1))
    }
  }
  return result
}

const flattenedFields = computed(() => {
  if (!activeStructure.value) return []
  return renderFieldTree((activeStructure.value.fields ?? []) as StructureFieldOutput[])
})
</script>

<template>
  <div class="data-structures-view">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="bi bi-diagram-3 me-2 text-primary"></i>
        Data Structures
      </h2>
      <button v-if="!isLocked && hasProject" class="btn btn-primary" @click="showNewStructureModal = true">
        <i class="bi bi-plus-lg me-1"></i>
        New Structure
      </button>
    </div>

    <div v-if="!hasProject" class="text-center py-5">
      <div class="empty-state">
        <i class="bi bi-folder-x"></i>
        <h5>No project selected</h5>
        <p class="text-muted">Select a project first to view and manage its data structures.</p>
        <router-link to="/projects" class="btn btn-primary">
          <i class="bi bi-folder2-open me-1"></i>Go to Projects
        </router-link>
      </div>
    </div>

    <template v-else>

    <div v-if="isLocked" class="alert alert-warning d-flex align-items-center gap-2 mb-3 py-2 px-3">
      <i class="bi bi-lock-fill"></i>
      <span class="small">This project is locked. Structures are read-only and cannot be modified.</span>
    </div>

    <div v-if="loadingStructures" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2">Loading structures...</p>
    </div>

    <div v-else class="row">
      <!-- Structure list -->
      <div class="col-md-3">
        <div class="card">
          <div class="card-header"><h6 class="mb-0">Structures</h6></div>
          <div class="card-body p-0">
            <div v-if="!structures?.length" class="empty-state py-4">
              <i class="bi bi-folder-x"></i>
              <p class="mb-0">No structures yet</p>
            </div>
            <div
              v-for="structure in (structures ?? [])"
              :key="structure.id"
              class="structure-item"
              :class="{ active: activeStructure?.id === structure.id }"
              @click="selectStructure(structure.id)"
            >
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <i class="bi bi-diagram-3 me-2"></i>
                  <strong>{{ structure.name }}</strong>
                </div>
                <div class="d-flex align-items-center gap-1">
                  <span class="badge bg-secondary">
                    {{ structure.selected_columns?.length ?? 0 }} col(s)
                  </span>
                  <button v-if="!isLocked" class="btn btn-sm btn-outline-danger" @click.stop="deleteStructure(structure.id)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Structure detail -->
      <div class="col-md-9">
        <div v-if="!activeStructure" class="card">
          <div class="card-body empty-state">
            <i class="bi bi-hand-index-thumb"></i>
            <p class="mb-0">Select a structure from the list</p>
          </div>
        </div>

        <template v-else>
          <!-- Table + Columns section -->
          <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i class="bi bi-table me-2"></i>
                Source Table &amp; Columns
              </h6>
              <button v-if="!isLocked" class="btn btn-sm btn-primary" @click="openPickerModal" :disabled="building">
                <i class="bi bi-pencil me-1"></i>
                {{ activeStructure.tables?.length ? 'Edit' : 'Set Table' }}
              </button>
            </div>
            <div class="card-body">
              <!-- No table set yet -->
              <div v-if="!activeStructure.tables?.length" class="text-muted small text-center py-3">
                <i class="bi bi-table me-1"></i>
                No table selected. Click "Set Table" to browse Unity Catalog.
              </div>

              <!-- Table is set -->
              <template v-else>
                <div class="table-item mb-3">
                  <div class="d-flex align-items-center gap-2">
                    <i class="bi bi-table text-primary"></i>
                    <strong>{{ activeStructure.tables[0].alias }}</strong>
                    <code class="small text-muted">{{ activeStructure.tables[0].full_name }}</code>
                  </div>
                </div>

                <div v-if="activeStructure.selected_columns?.length">
                  <p class="small fw-semibold text-muted mb-2">
                    Selected columns ({{ activeStructure.selected_columns.length }}):
                  </p>
                  <div class="column-grid">
                    <span
                      v-for="col in activeStructure.selected_columns"
                      :key="col"
                      class="column-chip"
                    >
                      <i class="bi bi-check2 text-success me-1" style="font-size:0.65rem"></i>
                      {{ col }}
                    </span>
                  </div>
                </div>
                <div v-else class="text-muted small">
                  <i class="bi bi-info-circle me-1"></i>
                  No columns selected — click "Edit" to choose columns.
                </div>
              </template>

              <!-- Building indicator -->
              <div v-if="building" class="mt-3 d-flex align-items-center gap-2 text-primary small">
                <span class="spinner-border spinner-border-sm"></span>
                Building — inferring fields from Unity Catalog…
              </div>
            </div>
          </div>

          <!-- Inferred fields -->
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-list-columns me-2"></i>
                Inferred Fields ({{ flattenedFields.length }})
              </h6>
            </div>
            <div class="card-body">
              <div v-if="flattenedFields.length === 0" class="text-muted small text-center py-3">
                <i class="bi bi-info-circle me-1"></i>
                Fields will appear after setting a table and columns.
              </div>
              <div
                v-for="field in flattenedFields"
                :key="field.name + '-' + field.depth"
                class="field-item"
                :class="{ nested: field.depth > 0 }"
                :style="{ marginLeft: field.depth * 24 + 'px' }"
              >
                <div class="d-flex align-items-center">
                  <i :class="['bi', getFieldIcon(field.type), 'me-2 text-primary']"></i>
                  <span class="fw-medium">{{ field.name }}</span>
                  <span class="badge bg-light text-dark ms-2">{{ field.type }}</span>
                  <span v-if="field.children && field.children.length > 0" class="text-muted small ms-2">
                    ({{ field.children.length }} children)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    </template>

    <!-- New Structure Modal -->
    <div v-if="showNewStructureModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">New Data Structure</h5>
            <button type="button" class="btn-close" @click="showNewStructureModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Structure Name</label>
              <input
                v-model="newStructureName"
                type="text"
                class="form-control"
                placeholder="e.g., Sales Report"
                @keyup.enter="!isCreatingStructure && createStructure()"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showNewStructureModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isCreatingStructure" @click="createStructure">
              <span v-if="isCreatingStructure" class="spinner-border spinner-border-sm me-1" role="status"></span>
              Create
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <div v-if="showDeleteStructureModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showDeleteStructureModal = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill text-danger me-2"></i> Delete Structure</h5>
            <button type="button" class="btn-close" @click="showDeleteStructureModal = false"></button>
          </div>
          <div class="modal-body">
            Delete <strong>{{ pendingDeleteName }}</strong>? This cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteStructureModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDeleteStructure">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Table + Column Picker Modal -->
    <div v-if="showPickerModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-search me-2"></i> Browse Unity Catalog</h5>
            <button type="button" class="btn-close" @click="showPickerModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-2" style="min-height: 340px;">
              <!-- Catalogs -->
              <div class="col-md-3">
                <div class="picker-panel">
                  <div class="picker-header"><i class="bi bi-database me-1"></i> Catalogs</div>
                  <div class="picker-body">
                    <div v-if="loadingCatalogs" class="text-center py-3">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </div>
                    <div
                      v-for="cat in catalogs" :key="cat.name"
                      class="picker-item" :class="{ active: pickerCatalog === cat.name }"
                      @click="selectPickerCatalog(cat.name)"
                    >{{ cat.name }}</div>
                  </div>
                </div>
              </div>

              <!-- Schemas -->
              <div class="col-md-2">
                <div class="picker-panel">
                  <div class="picker-header"><i class="bi bi-folder me-1"></i> Schemas</div>
                  <div class="picker-body">
                    <div v-if="!pickerCatalog" class="text-muted small p-2">Select a catalog</div>
                    <div v-else-if="loadingSchemas" class="text-center py-3">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </div>
                    <div
                      v-for="s in schemas" :key="s.name"
                      class="picker-item" :class="{ active: pickerSchema === s.name }"
                      @click="selectPickerSchema(s.name)"
                    >{{ s.name }}</div>
                  </div>
                </div>
              </div>

              <!-- Tables -->
              <div class="col-md-3">
                <div class="picker-panel">
                  <div class="picker-header"><i class="bi bi-table me-1"></i> Tables / Views</div>
                  <div class="picker-body">
                    <div v-if="!pickerSchema" class="text-muted small p-2">Select a schema</div>
                    <div v-else-if="loadingTables" class="text-center py-3">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </div>
                    <div
                      v-for="t in ucTables" :key="t.name"
                      class="picker-item" :class="{ active: pickerTable === t.name }"
                      @click="selectPickerTable(t.name)"
                    >
                      {{ t.name }}
                      <span class="badge bg-light text-dark ms-1" style="font-size:0.55rem">{{ t.table_type }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Columns — checkboxes -->
              <div class="col-md-4">
                <div class="picker-panel">
                  <div class="picker-header d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-list-check me-1"></i> Columns</span>
                    <div v-if="pickerColumns.length > 0" class="d-flex gap-1">
                      <button class="btn btn-link btn-sm p-0 text-decoration-none" style="font-size:0.7rem" @click="selectAllColumns">All</button>
                      <span class="text-muted" style="font-size:0.7rem">/</span>
                      <button class="btn btn-link btn-sm p-0 text-decoration-none" style="font-size:0.7rem" @click="deselectAllColumns">None</button>
                    </div>
                  </div>
                  <div class="picker-body">
                    <div v-if="!pickerTable" class="text-muted small p-2">Select a table</div>
                    <div v-else-if="loadingColumns" class="text-center py-3">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </div>
                    <label
                      v-for="col in pickerColumns"
                      :key="col.name"
                      class="picker-item picker-checkbox-item"
                      :class="{ selected: pickerSelectedColumns.has(col.name) }"
                    >
                      <input
                        type="checkbox"
                        class="form-check-input me-2 flex-shrink-0"
                        :checked="pickerSelectedColumns.has(col.name)"
                        @change="toggleColumn(col.name)"
                      />
                      <div class="overflow-hidden w-100">
                        <div class="column-name-row">
                          <span class="column-name text-truncate">{{ col.name }}</span>
                          <span class="column-type-badge">{{ columnTypeLabel(col.type_text, col.type_name) }}</span>
                          <button
                            v-if="parseChildNames(col.type_text).length"
                            class="expand-btn ms-auto"
                            :title="expandedColumns.has(col.name) ? 'Hide fields' : 'Show fields'"
                            @click="toggleExpanded(col.name, $event)"
                          >
                            <i :class="['bi', expandedColumns.has(col.name) ? 'bi-chevron-up' : 'bi-chevron-down']"></i>
                            {{ parseChildNames(col.type_text).length }}
                          </button>
                        </div>
                        <ul v-if="expandedColumns.has(col.name) && parseChildNames(col.type_text).length" class="column-children-list">
                          <li v-for="child in parseChildNames(col.type_text)" :key="child">
                            <i class="bi bi-dot me-1"></i>{{ child }}
                          </li>
                        </ul>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Summary bar -->
            <div class="mt-3 p-2 rounded border d-flex align-items-center gap-3" style="background:#f8f9fa; font-size:0.85rem;">
              <span v-if="pickerFullName">
                <i class="bi bi-table text-primary me-1"></i>
                <code>{{ pickerFullName }}</code>
              </span>
              <span v-else class="text-muted">No table selected</span>
              <span v-if="pickerSelectedCount > 0" class="badge bg-primary">
                {{ pickerSelectedCount }} column{{ pickerSelectedCount !== 1 ? 's' : '' }} selected
              </span>
              <span v-else-if="pickerTable" class="text-warning small">
                <i class="bi bi-exclamation-triangle me-1"></i>No columns selected
              </span>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showPickerModal = false">Cancel</button>
            <button
              type="button"
              class="btn btn-success"
              :disabled="!canSaveAndBuild || building"
              @click="confirmSaveAndBuild"
            >
              <i class="bi bi-hammer me-1"></i>
              Save &amp; Build
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.structure-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s ease;
}
.structure-item:hover { background: #f8f9fa; }
.structure-item.active {
  background: #e3f2fd;
  border-left: 3px solid var(--bs-primary);
}

.table-item {
  background: #f0f7ff;
  border: 1px solid #b8daff;
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
}

.column-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.column-chip {
  display: inline-flex;
  align-items: center;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.field-item {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.35rem;
}
.field-item.nested {
  border-left: 3px solid var(--bs-primary);
  background: #fff;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.empty-state i { font-size: 2rem; display: block; margin-bottom: 0.5rem; }

/* Picker panel */
.picker-panel {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  height: 340px;
  display: flex;
  flex-direction: column;
}
.picker-header {
  background: #f8f9fa;
  padding: 0.4rem 0.75rem;
  font-weight: 600;
  font-size: 0.8rem;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0;
}
.picker-body {
  overflow-y: auto;
  flex: 1;
}
.picker-item {
  padding: 0.4rem 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.82rem;
  transition: background 0.15s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.picker-item:hover { background: #f8f9fa; }
.picker-item.active { background: #e3f2fd; border-left: 3px solid var(--bs-primary); }

/* Column checkbox items */
.picker-checkbox-item {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0.4rem;
  cursor: pointer;
  padding: 0.45rem 0.75rem;
  user-select: none;
}
.picker-checkbox-item.selected { background: #f0f7ff; }
.picker-checkbox-item:hover { background: #f8f9fa; }
.picker-checkbox-item.selected:hover { background: #e3f2fd; }

.column-name-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.column-name { font-weight: 500; font-size: 0.8rem; }
.column-type-badge {
  font-size: 0.6rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  background: #e9ecef;
  color: #495057;
  border-radius: 3px;
  padding: 0.05rem 0.35rem;
  white-space: nowrap;
  flex-shrink: 0;
}
.expand-btn {
  background: none;
  border: none;
  padding: 0 0.2rem;
  font-size: 0.6rem;
  color: #6c757d;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
  flex-shrink: 0;
  line-height: 1;
}
.expand-btn:hover { color: var(--bs-primary); }

.column-children-list {
  list-style: none;
  margin: 0.25rem 0 0.1rem 0.5rem;
  padding: 0;
  border-left: 2px solid #dee2e6;
}
.column-children-list li {
  font-size: 0.68rem;
  color: #6c757d;
  padding: 0.1rem 0.4rem;
  font-family: 'Fira Code', 'Consolas', monospace;
}
</style>
