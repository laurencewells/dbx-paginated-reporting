<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useTemplatesStore } from '@/stores/templates'
import { useProjectsStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'
import ReportPreview from '@/components/ReportPreview.vue'
import AgentChatPanel from '@/components/AgentChatPanel.vue'
import Mustache from 'mustache'
import { html } from '@codemirror/lang-html'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView, keymap, placeholder } from '@codemirror/view'
import { EditorState, Compartment } from '@codemirror/state'
import { indentWithTab, history, historyKeymap } from '@codemirror/commands'
import {
  useListStructuresApiV1StructuresGet,
  useListTemplatesApiV1TemplatesGet,
  useCreateTemplateApiV1TemplatesPost,
  useUpdateTemplateApiV1TemplatesTemplateIdPut,
  useDeleteTemplateApiV1TemplatesTemplateIdDelete,
  getListTemplatesApiV1TemplatesGetQueryKey,
  previewDataApiV1TemplatesTemplateIdPreviewDataPost,
} from '@/api/generated'
import { useListProjectsApiV1ProjectsGet } from '@/api/generated/projects/projects'
import type { PreviewDataResponse } from '@/api/generated'

const queryClient = useQueryClient()
const templatesStore = useTemplatesStore()
const projectsStore = useProjectsStore()
const toastStore = useToastStore()

// -- Queries ------------------------------------------------------------------
const { data: projects } = useListProjectsApiV1ProjectsGet()

const activeProjectId = computed(() => projectsStore.activeProjectId)
const hasProject = computed(() => !!activeProjectId.value)
const structuresParams = computed(() => ({ project_id: activeProjectId.value! }))
const templatesParams = computed(() => ({ project_id: activeProjectId.value! }))

const { data: structures } = useListStructuresApiV1StructuresGet(structuresParams, {
  query: { enabled: hasProject },
})
const { data: templates } = useListTemplatesApiV1TemplatesGet(templatesParams, {
  query: { enabled: hasProject },
})

const activeProject = computed(() =>
  projects.value?.find((p) => p.id === activeProjectId.value) ?? null
)
const isLocked = computed(() => !!activeProject.value?.is_locked)

const activeTemplate = computed(() =>
  (templates.value ?? []).find((t) => t.id === templatesStore.activeTemplateId) ?? null
)

// -- Mutations ----------------------------------------------------------------
const { mutateAsync: createTemplateMutation } = useCreateTemplateApiV1TemplatesPost({
  mutation: {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: getListTemplatesApiV1TemplatesGetQueryKey(templatesParams) }),
  },
})
const { mutateAsync: updateTemplateMutation } = useUpdateTemplateApiV1TemplatesTemplateIdPut({
  mutation: {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: getListTemplatesApiV1TemplatesGetQueryKey(templatesParams) }),
  },
})
const { mutateAsync: deleteTemplateMutation } = useDeleteTemplateApiV1TemplatesTemplateIdDelete({
  mutation: {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: getListTemplatesApiV1TemplatesGetQueryKey(templatesParams) }),
  },
})

// -- Editor state -------------------------------------------------------------
type SaveState = 'idle' | 'unsaved' | 'saving' | 'saved' | 'conflict' | 'error'
const saveState = ref<SaveState>('idle')
const lastKnownUpdatedAt = ref<string | null>(null)

const htmlContent = ref('')
const selectedStructureId = ref('')
const templateName = ref('')

const splitRatio = ref(50)
const isDragging = ref(false)
const splitViewRef = ref<HTMLElement | null>(null)

const showNewTemplateModal = ref(false)
const newTemplateName = ref('')
const isCreatingTemplate = ref(false)
const newTemplateStructureId = ref('')

const showDeleteTemplateModal = ref(false)

const showMustacheHelp = ref(false)
const showStructureHint = ref(false)
const showAgentChat = ref(false)

const editorEl = ref<HTMLElement>()
const cmView = ref<EditorView>()
const editableCompartment = new Compartment()

watch(htmlContent, (newVal) => {
  if (!cmView.value) return
  const current = cmView.value.state.doc.toString()
  if (current !== newVal) {
    cmView.value.dispatch({ changes: { from: 0, to: current.length, insert: newVal } })
  }
})

watch(
  [() => activeTemplate.value, isLocked],
  ([template]) => {
    cmView.value?.dispatch({
      effects: editableCompartment.reconfigure(EditorView.editable.of(!!template && !isLocked.value)),
    })
  },
)


const previewDataResult = ref<Record<string, unknown>>({})
const previewLoading = ref(false)
const previewCache = new Map<string, Record<string, unknown>>()

const activeStructure = computed(() =>
  structures.value?.find((s) => s.id === selectedStructureId.value) ?? null
)

function fieldTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    string: 'bi-fonts', number: 'bi-123', boolean: 'bi-toggle-on',
    date: 'bi-calendar', array: 'bi-list-ul', object: 'bi-braces',
  }
  return icons[type] || 'bi-question'
}

async function loadPreviewData(force = false) {
  if (!activeTemplate.value) { previewDataResult.value = {}; return }
  const cacheKey = `${activeTemplate.value.id}:${activeTemplate.value.structure_id}`
  if (!force && previewCache.has(cacheKey)) {
    previewDataResult.value = previewCache.get(cacheKey)!
    return
  }
  previewLoading.value = true
  try {
    const result = (await previewDataApiV1TemplatesTemplateIdPreviewDataPost(activeTemplate.value.id!, { limit: 50 })) as unknown as PreviewDataResponse
    previewCache.set(cacheKey, result.data)
    previewDataResult.value = result.data
  } catch {
    previewDataResult.value = {}
  } finally {
    previewLoading.value = false
  }
}

function getStructureName(structureId: string): string {
  return structures.value?.find((s) => s.id === structureId)?.name || 'Unknown'
}

const renderedHtml = computed(() => {
  if (!htmlContent.value) return '<div class="empty-state"><i class="bi bi-eye-slash"></i><p>Start typing to see preview</p></div>'
  try {
    return Mustache.render(htmlContent.value ?? '', previewDataResult.value)
  } catch (error) {
    return `<div class="alert alert-danger m-3"><i class="bi bi-exclamation-triangle me-2"></i>Template Error: ${error instanceof Error ? error.message : 'Unknown error'}</div>`
  }
})

function startDrag(e: MouseEvent) { isDragging.value = true; e.preventDefault() }
function onDrag(e: MouseEvent) {
  if (!isDragging.value || !splitViewRef.value) return
  const rect = splitViewRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  splitRatio.value = Math.min(80, Math.max(20, (x / rect.width) * 100))
}
function stopDrag() { isDragging.value = false }
function setSplitRatio(ratio: number) { splitRatio.value = ratio }

watch(
  () => projectsStore.activeProjectId,
  (newId, oldId) => {
    if (newId !== oldId) templatesStore.setActiveTemplate(null)
  },
)

watch(
  () => activeTemplate.value?.id,
  async (id, oldId) => {
    const template = activeTemplate.value
    if (template && id) {
      htmlContent.value = template.html_content ?? ''
      selectedStructureId.value = template.structure_id
      templateName.value = template.name
      lastKnownUpdatedAt.value = template.updated_at
      saveState.value = 'idle'
      loadPreviewData()
      await nextTick()
      if (cmView.value) {
        const current = cmView.value.state.doc.toString()
        if (current !== htmlContent.value) {
          cmView.value.dispatch({ changes: { from: 0, to: current.length, insert: htmlContent.value } })
        }
      }
    } else if (oldId) {
      // Only clear when navigating away from a previously loaded template (not on initial render)
      htmlContent.value = ''
      selectedStructureId.value = ''
      templateName.value = ''
      saveState.value = 'idle'
      previewDataResult.value = {}
      await nextTick()
      if (cmView.value) {
        const current = cmView.value.state.doc.toString()
        if (current !== '') cmView.value.dispatch({ changes: { from: 0, to: current.length, insert: '' } })
      }
    }
  },
  { immediate: true },
)

let saveTimeout: ReturnType<typeof setTimeout> | null = null
let savedFadeTimeout: ReturnType<typeof setTimeout> | null = null

watch(htmlContent, () => {
  if (!activeTemplate.value || saveState.value === 'conflict' || isLocked.value) return
  saveState.value = 'unsaved'
  if (saveTimeout) clearTimeout(saveTimeout)
  if (savedFadeTimeout) clearTimeout(savedFadeTimeout)
  saveTimeout = setTimeout(() => autoSave(), 2000)
})

async function autoSave() {
  if (!activeTemplate.value || saveState.value === 'conflict' || isLocked.value) return
  saveState.value = 'saving'
  try {
    const result = await updateTemplateMutation({
      templateId: activeTemplate.value.id,
      data: {
        html_content: htmlContent.value,
        expected_updated_at: lastKnownUpdatedAt.value,
      },
    })
    lastKnownUpdatedAt.value = result.updated_at
    saveState.value = 'saved'
    savedFadeTimeout = setTimeout(() => {
      if (saveState.value === 'saved') saveState.value = 'idle'
    }, 3000)
  } catch (err: unknown) {
    const status = (err as { status?: number })?.status
      ?? (err as { response?: { status?: number } })?.response?.status
    if (status === 409) {
      saveState.value = 'conflict'
      toastStore.warning('This template was modified by another user. Reload to see the latest version.')
    } else if (status === 423) {
      saveState.value = 'error'
      toastStore.warning('This template belongs to a locked project and cannot be modified.')
    } else {
      saveState.value = 'error'
      toastStore.error('Failed to save template')
    }
  }
}

function reloadTemplate() {
  if (!activeTemplate.value) return
  queryClient.invalidateQueries({ queryKey: getListTemplatesApiV1TemplatesGetQueryKey(templatesParams) })
  saveState.value = 'idle'
}

async function createTemplate() {
  if (!newTemplateName.value.trim()) { toastStore.warning('Please enter a template name'); return }
  if (!newTemplateStructureId.value) { toastStore.warning('Please select a data structure'); return }
  if (isCreatingTemplate.value) return
  isCreatingTemplate.value = true
  try {
    const created = await createTemplateMutation({ data: { name: newTemplateName.value.trim(), structure_id: newTemplateStructureId.value } })
    templatesStore.setActiveTemplate(created.id)
    toastStore.success(`Created template "${newTemplateName.value}"`)
    newTemplateName.value = ''
    newTemplateStructureId.value = ''
    showNewTemplateModal.value = false
  } finally {
    isCreatingTemplate.value = false
  }
}

async function saveTemplate() {
  if (!activeTemplate.value || isLocked.value) return
  if (saveTimeout) clearTimeout(saveTimeout)
  saveState.value = 'saving'
  try {
    const result = await updateTemplateMutation({
      templateId: activeTemplate.value.id,
      data: {
        name: templateName.value,
        structure_id: selectedStructureId.value,
        html_content: htmlContent.value,
        expected_updated_at: lastKnownUpdatedAt.value,
      },
    })
    lastKnownUpdatedAt.value = result.updated_at
    saveState.value = 'saved'
    toastStore.success('Template saved!')
    if (savedFadeTimeout) clearTimeout(savedFadeTimeout)
    savedFadeTimeout = setTimeout(() => {
      if (saveState.value === 'saved') saveState.value = 'idle'
    }, 3000)
  } catch (err: unknown) {
    const status = (err as { status?: number })?.status
      ?? (err as { response?: { status?: number } })?.response?.status
    if (status === 409) {
      saveState.value = 'conflict'
      toastStore.warning('This template was modified by another user. Reload to see the latest version.')
    } else if (status === 423) {
      saveState.value = 'error'
      toastStore.warning('This template belongs to a locked project and cannot be modified.')
    } else {
      saveState.value = 'error'
      toastStore.error('Failed to save template')
    }
  }
}

function deleteTemplate() {
  if (!activeTemplate.value) return
  showDeleteTemplateModal.value = true
}

async function confirmDeleteTemplate() {
  if (!activeTemplate.value) return
  const id = activeTemplate.value.id
  showDeleteTemplateModal.value = false
  await deleteTemplateMutation({ templateId: id })
  templatesStore.setActiveTemplate(null)
  toastStore.success('Template deleted')
  htmlContent.value = ''
  selectedStructureId.value = ''
  templateName.value = ''
}


const VOID_TAGS = new Set([
  'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
  'link', 'meta', 'param', 'source', 'track', 'wbr',
])

function formatHtml() {
  if (!htmlContent.value.trim() || !cmView.value) return
  const INDENT = '  '

  const normalized = htmlContent.value.replace(/<([a-zA-Z][^>]*)>/gs, (match) =>
    match.replace(/\s*\n\s*/g, ' '),
  )

  const tokens = normalized
    .replace(/>\s*</g, '>\n<')
    .replace(/>\s*(\{\{)/g, '>\n$1')
    .replace(/(\}\})\s*</g, '$1\n<')
    .split('\n')
    .map((t) => t.trim())
    .filter(Boolean)

  let depth = 0
  const lines: string[] = []

  for (const token of tokens) {
    // Collect all opening tags (non-void, non-self-closing)
    const openNames: string[] = []
    const openRe = /<([a-zA-Z][a-zA-Z0-9]*)[^>]*>/g
    let m: RegExpExecArray | null
    while ((m = openRe.exec(token)) !== null) {
      const name = m[1].toLowerCase()
      if (!VOID_TAGS.has(name) && !m[0].endsWith('/>')) openNames.push(name)
    }

    // Collect all closing tags
    const closeNames: string[] = []
    const closeRe = /<\/([a-zA-Z][a-zA-Z0-9]*)\s*>/g
    while ((m = closeRe.exec(token)) !== null) closeNames.push(m[1].toLowerCase())

    // Cancel matched open/close pairs within the same token
    const unpairedOpens = [...openNames]
    const unpairedCloses = [...closeNames]
    for (const name of openNames) {
      const i = unpairedCloses.indexOf(name)
      if (i !== -1) { unpairedCloses.splice(i, 1); unpairedOpens.splice(unpairedOpens.indexOf(name), 1) }
    }

    // Mustache block open {{# and close {{/
    const mustacheOpen = /^\{\{#/.test(token) ? 1 : 0
    const mustacheClose = /^\{\{\//.test(token) ? 1 : 0

    depth = Math.max(0, depth - unpairedCloses.length - mustacheClose)
    lines.push(INDENT.repeat(depth) + token)
    depth += unpairedOpens.length + mustacheOpen
  }

  const formatted = lines.join('\n')
  const docLength = cmView.value.state.doc.length
  cmView.value.dispatch({
    changes: { from: 0, to: docLength, insert: formatted },
  })
  toastStore.info('Template formatted')
}

function handleReplaceContent(event: CustomEvent) {
  if (!activeTemplate.value) { toastStore.warning('Please select or create a template first'); return }
  htmlContent.value = event.detail as string
  toastStore.success('Template replaced')
}

function handleSnippetInsert(event: CustomEvent) {
  const snippet = event.detail as string
  if (!activeTemplate.value) { toastStore.warning('Please select or create a template first'); return }
  if (cmView.value) {
    const { from, to } = cmView.value.state.selection.main
    cmView.value.dispatch({
      changes: { from, to, insert: snippet },
      selection: { anchor: from + snippet.length },
    })
    cmView.value.focus()
  } else {
    htmlContent.value += '\n' + snippet
  }
  toastStore.info('Component inserted')
}

function createEditor() {
  if (!editorEl.value) return
  cmView.value?.destroy()
  cmView.value = new EditorView({
    parent: editorEl.value,
    state: EditorState.create({
      doc: htmlContent.value,
      extensions: [
        html(),
        oneDark,
        EditorView.lineWrapping,
        EditorState.tabSize.of(2),
        history(),
        keymap.of([...historyKeymap, indentWithTab]),
        placeholder('Enter your HTML template here...'),
        editableCompartment.of(EditorView.editable.of(!!activeTemplate.value && !isLocked.value)),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) htmlContent.value = update.state.doc.toString()
        }),
      ],
    }),
  })
}

watch(editorEl, (el) => {
  if (el) createEditor()
})

onMounted(() => {
  window.addEventListener('insert-snippet', handleSnippetInsert as (event: Event) => void)
  window.addEventListener('replace-template-content', handleReplaceContent as (event: Event) => void)
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
  createEditor()
})

onUnmounted(() => {
  window.removeEventListener('insert-snippet', handleSnippetInsert as (event: Event) => void)
  window.removeEventListener('replace-template-content', handleReplaceContent as (event: Event) => void)
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
  if (saveTimeout) clearTimeout(saveTimeout)
  if (savedFadeTimeout) clearTimeout(savedFadeTimeout)
  cmView.value?.destroy()
})
</script>

<template>
  <div class="template-editor-view">
    <!-- Toolbar -->
    <div class="toolbar mb-3 d-flex justify-content-between align-items-center flex-wrap gap-2">
      <div class="d-flex align-items-center gap-2">
        <template v-if="activeTemplate">
          <i :class="['bi', isLocked ? 'bi-lock-fill text-warning' : 'bi-file-code text-primary']"></i>
          <template v-if="isLocked">
            <span class="fw-semibold small">{{ templateName }}</span>
          </template>
          <input v-else v-model="templateName" type="text" class="form-control form-control-sm fw-semibold" style="width: 220px" placeholder="Report name" />
          <div class="d-flex align-items-center gap-1 position-relative">
            <template v-if="isLocked">
              <span class="input-group-text input-group-sm"><i class="bi bi-link-45deg"></i> Data</span>
              <span class="small text-muted">{{ getStructureName(selectedStructureId) }}</span>
            </template>
            <div v-else class="input-group input-group-sm" style="width: auto;">
              <span class="input-group-text"><i class="bi bi-link-45deg"></i> Data</span>
              <select v-model="selectedStructureId" class="form-select form-select-sm" style="width: 150px" title="Data Structure">
                <option v-for="s in (structures ?? [])" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <button v-if="activeStructure" class="btn btn-sm btn-outline-secondary" :class="{ active: showStructureHint }" title="View data schema" @click="showStructureHint = !showStructureHint">
              <i class="bi bi-diagram-3"></i>
            </button>
            <div v-if="showStructureHint && activeStructure" class="structure-hint-popup card">
              <div class="card-header d-flex justify-content-between align-items-center py-2">
                <span class="small fw-semibold mb-0"><i class="bi bi-diagram-3 me-1 text-primary"></i> {{ activeStructure.name }} Fields</span>
                <button type="button" class="btn-close btn-sm" @click="showStructureHint = false"></button>
              </div>
              <div class="card-body p-2">
                <p class="text-muted small mb-2 px-1">Use <code>{<!-- -->{field}}</code> in your template</p>
                <template v-for="field in activeStructure.fields" :key="field.name">
                  <div class="hint-field-item">
                    <div class="d-flex align-items-center">
                      <i :class="['bi', fieldTypeIcon(field.type), 'me-2 text-primary']"></i>
                      <span class="fw-medium">{{ field.name }}</span>
                      <span class="badge bg-light text-dark ms-2">{{ field.type }}</span>
                    </div>
                    <div v-if="field.type === 'array' || field.type === 'object'" class="text-muted small mt-1">
                      <code class="hint-mustache">{<!-- -->{#{{ field.name }}}} ... {<!-- -->{/{{ field.name }}}}</code>
                    </div>
                  </div>
                  <template v-if="field.children && field.children.length">
                    <div v-for="child in field.children" :key="child.name" class="hint-field-item nested" style="margin-left: 24px">
                      <div class="d-flex align-items-center">
                        <i :class="['bi', fieldTypeIcon(child.type), 'me-2 text-primary']"></i>
                        <span class="fw-medium">{{ child.name }}</span>
                        <span class="badge bg-light text-dark ms-2">{{ child.type }}</span>
                      </div>
                    </div>
                  </template>
                </template>
              </div>
            </div>
          </div>
          <button class="btn btn-sm btn-primary" @click="saveTemplate" title="Save template" :disabled="saveState === 'saving' || isLocked"><i class="bi bi-save"></i></button>
          <span class="save-indicator" :class="`save-${saveState}`">
            <template v-if="saveState === 'unsaved'"><i class="bi bi-circle-fill"></i> Unsaved</template>
            <template v-else-if="saveState === 'saving'"><span class="spinner-border spinner-border-sm"></span> Saving</template>
            <template v-else-if="saveState === 'saved'"><i class="bi bi-check-circle-fill"></i> Saved</template>
            <template v-else-if="saveState === 'conflict'"><i class="bi bi-exclamation-triangle-fill"></i> Conflict</template>
            <template v-else-if="saveState === 'error'"><i class="bi bi-x-circle-fill"></i> Error</template>
          </span>
          <button class="btn btn-sm btn-outline-danger" @click="deleteTemplate" title="Delete template" :disabled="isLocked"><i class="bi bi-trash"></i></button>
        </template>
        <template v-else>
          <span class="text-muted small">{{ isLocked ? 'Select a template from the sidebar to view' : 'Select a template from the sidebar or create one' }}</span>
        </template>
        <button v-if="!isLocked" class="btn btn-sm btn-outline-primary" @click="showNewTemplateModal = true"><i class="bi bi-plus-lg me-1"></i> New</button>
      </div>
      <div v-if="activeTemplate" class="d-flex align-items-center gap-2">
        <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-outline-secondary" :class="{ active: splitRatio < 35 }" @click="setSplitRatio(30)" title="More preview"><i class="bi bi-layout-sidebar-reverse"></i></button>
          <button type="button" class="btn btn-outline-secondary" :class="{ active: splitRatio >= 35 && splitRatio <= 65 }" @click="setSplitRatio(50)" title="Equal split"><i class="bi bi-layout-split"></i></button>
          <button type="button" class="btn btn-outline-secondary" :class="{ active: splitRatio > 65 }" @click="setSplitRatio(70)" title="More editor"><i class="bi bi-layout-sidebar"></i></button>
        </div>
        <button class="btn btn-sm" :class="showAgentChat ? 'btn-primary' : 'btn-outline-primary'" @click="showAgentChat = !showAgentChat" title="AI Assistant">
          <i class="bi bi-robot me-1"></i> AI
        </button>
      </div>
    </div>

    <div v-if="activeTemplate" class="template-info-bar mb-2">
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-primary"><i class="bi bi-file-code me-1"></i> {{ activeTemplate.name }}</span>
        <span class="text-muted">→</span>
        <span class="badge bg-secondary"><i class="bi bi-diagram-3 me-1"></i> {{ getStructureName(selectedStructureId) }}</span>
      </div>
    </div>

    <div v-if="isLocked" class="alert alert-warning d-flex align-items-center gap-2 mb-2 py-2 px-3">
      <i class="bi bi-lock-fill"></i>
      <span class="small flex-grow-1">This project is locked. The editor is read-only and changes cannot be saved.</span>
    </div>

    <div v-if="saveState === 'conflict'" class="alert alert-warning d-flex align-items-center gap-2 mb-2 py-2 px-3">
      <i class="bi bi-exclamation-triangle-fill"></i>
      <span class="small flex-grow-1">This template was modified by another user. Your unsaved changes may conflict.</span>
      <button class="btn btn-sm btn-warning" @click="reloadTemplate">
        <i class="bi bi-arrow-clockwise me-1"></i> Reload latest
      </button>
    </div>

    <div v-if="activeTemplate" class="editor-layout" :class="{ 'with-agent': showAgentChat }">
    <div class="split-view" ref="splitViewRef" :class="{ dragging: isDragging }">
      <div class="split-panel editor-panel" :class="{ 'editor-locked': isLocked }" :style="{ width: `calc(${splitRatio}% - 6px)` }">
        <div class="panel-header" style="background-color: #1a1f36;">
          <h6 class="panel-title" style="color: #FFF;"><i class="bi bi-code-square me-2"></i> HTML Template</h6>
          <div class="d-flex align-items-center gap-1">
            <span class="badge bg-secondary">Mustache</span>
            <span v-if="isLocked" class="badge bg-warning text-dark"><i class="bi bi-lock-fill me-1"></i>Read Only</span>
            <template v-if="!isLocked">
              <button class="btn-syntax-help" title="Format HTML" @click="formatHtml"><i class="bi bi-braces-asterisk"></i></button>
              <button class="btn-syntax-help" @click="showMustacheHelp = !showMustacheHelp" title="Mustache syntax help"><i class="bi bi-info-circle"></i></button>
            </template>
          </div>
        </div>
        <div v-if="showMustacheHelp" class="syntax-help-popup">
          <div class="syntax-help-header">
            <h6 class="mb-0"><i class="bi bi-mortarboard me-2"></i> Template Guide</h6>
            <button class="btn-close btn-close-white btn-sm" @click="showMustacheHelp = false"></button>
          </div>
          <div class="syntax-help-content">
            <div class="syntax-section-label">Mustache Syntax</div>
            <div class="syntax-item"><code>{{"\{\{fieldName\}\}"}}</code><span>Output a value</span></div>
            <div class="syntax-item"><code>{{"\{\{#rows\}\}...\{\{/rows\}\}"}}</code><span>Loop over data rows</span></div>
            <div class="syntax-item"><code>{{"\{\{#condition\}\}...\{\{/condition\}\}"}}</code><span>Conditional (truthy)</span></div>
            <div class="syntax-item"><code>{{"\{\{^condition\}\}...\{\{/condition\}\}"}}</code><span>Conditional (falsy)</span></div>
            <div class="syntax-item"><code>{{"\{\{_index\}\}"}}</code><span>Row number (1-based)</span></div>
            <div class="syntax-item"><code>{{"\{\{_total\}\}"}}</code><span>Total row count</span></div>
            <hr class="my-2">
            <div class="syntax-section-label">Report Components</div>
            <div class="syntax-item"><code>.report-page</code><span>Page wrapper (A4 size)</span></div>
            <div class="syntax-item"><code>.report-tile.tile-primary</code><span>Stat tile — blue</span></div>
            <div class="syntax-item"><code>.report-tile.tile-success</code><span>Stat tile — green</span></div>
            <div class="syntax-item"><code>.report-tile.tile-warning</code><span>Stat tile — amber</span></div>
            <div class="syntax-item"><code>.report-tile.tile-danger</code><span>Stat tile — red</span></div>
            <div class="syntax-item"><code>.report-table</code><span>Styled data table</span></div>
            <div class="syntax-item"><code>.report-bar-chart</code><span>Bar chart (data-labels / data-values)</span></div>
            <div class="syntax-item"><code>.report-pie-chart</code><span>Pie chart (data-labels / data-values)</span></div>
            <div class="syntax-item"><code>.page-number</code><span>Footer page counter</span></div>
            <hr class="my-2">
            <div class="syntax-section-label">Bootstrap 5</div>
            <p class="syntax-note">Bootstrap 5 is fully available — use any utility or grid class directly in your template.</p>
            <div class="syntax-item"><code>.row / .col-md-*</code><span>Responsive grid layout</span></div>
            <div class="syntax-item"><code>.d-flex / .gap-*</code><span>Flexbox utilities</span></div>
            <div class="syntax-item"><code>.badge / .text-muted</code><span>Typography helpers</span></div>
            <hr class="my-2">
            <div class="syntax-section-label">Conditional Styles</div>
            <div class="syntax-item"><code>{{"\{\{field\}\}"}}</code><span>Use as CSS class suffix</span></div>
            <p class="syntax-note">Interpolate a field into the class name, then define one CSS rule per value in a <code>&lt;style&gt;</code> block.</p>
            <div class="syntax-example">
              <pre>&lt;style&gt;
  .status-approved { background: #198754; color: white; }
  .status-pending  { background: #fd7e14; color: white; }
  .status-rejected { background: #dc3545; color: white; }
&lt;/style&gt;

&lt;span class="badge status-{{"\{\{approval_status\}\}"}}"&gt;
  {{"\{\{approval_status\}\}"}}
&lt;/span&gt;</pre>
            </div>
            <p class="syntax-note mt-2">For conditional blocks (not just colour), add boolean columns in your SQL: <code>status = 'approved' AS is_approved</code> then use <code>{{"\{\{#is_approved\}\}"}}</code>.</p>
            <hr class="my-2">
            <div class="syntax-section-label">Custom Styles</div>
            <p class="syntax-note">Add a <code>&lt;style&gt;</code> block at the top of your template for fully custom CSS.</p>
            <div class="syntax-example">
              <pre>&lt;style&gt;
  .my-header { background: #1a1f36; color: white; }
&lt;/style&gt;

{{"\{\{#rows\}\}"}}
&lt;div class="report-page"&gt;
  &lt;div class="my-header"&gt;{{"\{\{name\}\}"}}&lt;/div&gt;
  &lt;div class="page-number"&gt;{{"\{\{_index\}\}"}} / {{"\{\{_total\}\}"}}&lt;/div&gt;
&lt;/div&gt;
{{"\{\{/rows\}\}"}}</pre>
            </div>
          </div>
        </div>
        <pre v-if="isLocked" class="code-readonly">{{ htmlContent }}</pre>
        <div v-show="!isLocked" ref="editorEl" class="code-editor" />
      </div>
      <div class="resize-handle" @mousedown="startDrag" title="Drag to resize panels"><div class="resize-handle-bar"></div></div>
      <div class="split-panel preview-panel" :style="{ width: `calc(${100 - splitRatio}% - 6px)` }">
        <div class="panel-header">
          <h6 class="panel-title"><i class="bi bi-eye me-2"></i> Live Preview</h6>
          <transition name="fade">
            <span v-if="previewLoading" class="preview-loading-badge">
              <span class="spinner-border spinner-border-sm me-1"></span> Loading data…
            </span>
          </transition>
        </div>
        <div class="preview-content"><ReportPreview :html="renderedHtml" /></div>
      </div>
    </div>

    <!-- Agent Chat Panel -->
    <div v-if="showAgentChat" class="agent-panel">
      <AgentChatPanel
        :template-id="activeTemplate?.id || null"
        :template-name="activeTemplate?.name || null"
        :structure-name="activeStructure?.name || null"
      />
    </div>
    </div>

    <div v-else class="empty-state-container d-flex flex-column align-items-center justify-content-center text-center">
      <i :class="['bi', 'empty-state-icon', 'text-muted', isLocked ? 'bi-lock-fill' : 'bi-file-earmark-code']"></i>
      <h5 class="mt-3 mb-2">{{ isLocked ? 'Project is locked' : 'No template selected' }}</h5>
      <p class="text-muted mb-3">{{ isLocked ? 'Select a template from the sidebar to view it in read-only mode.' : 'Select a template from the sidebar or create a new one to get started.' }}</p>
      <button v-if="!isLocked" class="btn btn-primary" @click="showNewTemplateModal = true">
        <i class="bi bi-plus-lg me-1"></i> Create Template
      </button>
    </div>

    <!-- Delete Template Modal -->
    <div v-if="showDeleteTemplateModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @keydown.esc="showDeleteTemplateModal = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill text-danger me-2"></i> Delete Template</h5>
            <button type="button" class="btn-close" @click="showDeleteTemplateModal = false"></button>
          </div>
          <div class="modal-body">
            Delete <strong>{{ activeTemplate?.name }}</strong>? This cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteTemplateModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDeleteTemplate">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- New Template Modal -->
    <div v-if="showNewTemplateModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-file-earmark-plus me-2"></i> New Template</h5>
            <button type="button" class="btn-close" @click="showNewTemplateModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Template Name</label>
              <input v-model="newTemplateName" type="text" class="form-control" placeholder="e.g., Monthly Sales Report" />
            </div>
            <div class="mb-3">
              <label class="form-label"><i class="bi bi-link-45deg me-1"></i> Link to Data Structure</label>
              <select v-model="newTemplateStructureId" class="form-select">
                <option value="" disabled>Select a structure...</option>
                <option v-for="s in (structures ?? [])" :key="s.id" :value="s.id">{{ s.name }} ({{ s.fields?.length ?? 0 }} fields)</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showNewTemplateModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" :disabled="isCreatingTemplate" @click="createTemplate">
              <span v-if="isCreatingTemplate" class="spinner-border spinner-border-sm me-1" role="status"></span>
              <i v-else class="bi bi-plus-lg me-1"></i>
              Create Template
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.template-editor-view { height: calc(100vh - var(--pr-navbar-height) - 3rem); display: flex; flex-direction: column; }
.toolbar { flex-shrink: 0; }
.template-info-bar { flex-shrink: 0; font-size: 0.8rem; }
.editor-layout { flex: 1; min-height: 0; display: flex; gap: 0; }
.editor-layout .split-view { flex: 1; min-width: 0; }
.agent-panel { width: 340px; flex-shrink: 0; min-height: 0; display: flex; flex-direction: column; border-radius: 0 8px 8px 0; overflow: hidden; border: 1px solid #dee2e6; border-left: none; }
.split-view { flex: 1; min-height: 0; display: flex; gap: 0; position: relative; }
.split-view.dragging { cursor: col-resize; user-select: none; }
.split-panel { flex: none !important; min-width: 200px; overflow: hidden; display: flex; flex-direction: column; transition: width 0.15s ease; }
.split-view.dragging .split-panel { transition: none; }
.resize-handle { width: 12px; cursor: col-resize; display: flex; align-items: center; justify-content: center; flex-shrink: 0; background: transparent; transition: background 0.2s ease; z-index: 10; }
.resize-handle:hover { background: rgba(52, 152, 219, 0.1); }
.resize-handle-bar { width: 4px; height: 40px; background: #dee2e6; border-radius: 2px; transition: all 0.2s ease; }
.resize-handle:hover .resize-handle-bar { background: var(--pr-info); height: 60px; }
.split-view.dragging .resize-handle-bar { background: var(--pr-info); height: 80px; }
.editor-panel { background: var(--pr-editor-bg); border-radius: 8px 0 0 8px; }
.code-readonly {
  flex: 1;
  min-height: 0;
  overflow: auto;
  margin: 0;
  padding: 1rem;
  background: var(--pr-editor-bg);
  color: #abb2bf;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 0.82rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  border: none;
  border-radius: 0;
}
.preview-panel { background: #fff; border-radius: 0 8px 8px 0; border: 1px solid #dee2e6; border-left: none; }
.code-editor { flex: 1; min-height: 0; overflow: hidden; }
.code-editor :deep(.cm-editor) { height: 100%; font-size: 0.82rem; }
.code-editor :deep(.cm-scroller) { overflow: auto; font-family: 'Fira Code', 'Consolas', 'Monaco', monospace; }
.code-editor :deep(.cm-editor.cm-focused) { outline: none; }
.preview-content { flex: 1; overflow: auto; padding: 0; }
.btn-group .btn.active { background-color: var(--pr-info); border-color: var(--pr-info); color: white; }
.btn-syntax-help { background: transparent; border: none; color: rgba(255,255,255,0.7); cursor: pointer; padding: 0.2rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; }
.btn-syntax-help:hover { color: white; background: rgba(255,255,255,0.2); }
.syntax-help-popup { position: absolute; top: 45px; right: 10px; width: 340px; background: #1a1a2e; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.4); z-index: 100; overflow: hidden; border: 1px solid #2d2d44; }
.syntax-help-header { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 0.75rem 1rem; display: flex; justify-content: space-between; align-items: center; }
.syntax-help-content { padding: 1rem; max-height: 400px; overflow-y: auto; }
.syntax-item { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px solid #2d2d44; }
.syntax-item:last-of-type { border-bottom: none; }
.syntax-item code { background: #2d2d44; color: #e74c3c; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-family: 'Fira Code', 'Consolas', monospace; }
.syntax-item span { color: #a0a0a0; font-size: 0.75rem; }
.syntax-example { margin-top: 0.5rem; }
.syntax-example strong { color: #e0e0e0; font-size: 0.8rem; }
.syntax-example pre { background: #2d2d44; color: #a0e0a0; padding: 0.75rem; border-radius: 6px; font-size: 0.7rem; margin-top: 0.5rem; overflow-x: auto; white-space: pre-wrap; font-family: 'Fira Code', 'Consolas', monospace; }
.syntax-help-content hr { border-color: #2d2d44; }
.structure-hint-popup { position: absolute; top: 100%; left: 0; margin-top: 6px; width: 340px; z-index: 200; box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
.structure-hint-popup .card-body { max-height: 360px; overflow-y: auto; }
.hint-field-item { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 0.4rem 0.6rem; margin-bottom: 0.35rem; font-size: 0.8rem; }
.hint-field-item.nested { border-left: 3px solid var(--pr-info); background: #fff; }
.hint-mustache { font-size: 0.72rem; color: #6c757d; }
.preview-loading-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 500;
  color: #0c63e4;
  background: #cfe2ff;
  border: 1px solid #b6d4fe;
  border-radius: 6px;
  padding: 0.2rem 0.55rem;
}
.save-indicator { font-size: 0.72rem; font-weight: 500; display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.15rem 0.5rem; border-radius: 4px; transition: all 0.2s ease; }
.save-idle { opacity: 0; }
.save-unsaved { color: #6c757d; }
.save-saving { color: #0c63e4; }
.save-saved { color: #198754; }
.save-conflict { color: #fd7e14; font-weight: 600; }
.save-error { color: #dc3545; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.syntax-section-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #7c83a0; margin: 0.6rem 0 0.4rem; }
.syntax-note { font-size: 0.75rem; color: #a0a0a0; margin: 0.15rem 0 0.5rem; line-height: 1.4; }
.syntax-note code { background: #2d2d44; color: #e74c3c; padding: 0.1rem 0.35rem; border-radius: 3px; font-size: 0.72rem; }
.empty-state-container { flex: 1; min-height: 0; }
.empty-state-icon { font-size: 4rem; opacity: 0.3; }
</style>
