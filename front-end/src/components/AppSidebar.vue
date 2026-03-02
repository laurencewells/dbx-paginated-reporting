<script setup lang="ts">
import { computed } from 'vue'
import { useDataStructuresStore } from '@/stores/dataStructures'
import { useTemplatesStore } from '@/stores/templates'
import { useListStructuresApiV1StructuresGet, useListTemplatesApiV1TemplatesGet } from '@/api/generated'
import { useRouter, useRoute } from 'vue-router'

defineProps<{
  collapsed: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle'): void
}>()

const dataStore = useDataStructuresStore()
const templatesStore = useTemplatesStore()
const router = useRouter()
const route = useRoute()

const { data: structures } = useListStructuresApiV1StructuresGet()
const { data: templates } = useListTemplatesApiV1TemplatesGet()
const activeStructureId = computed(() => dataStore.activeStructureId)
const activeTemplateId = computed(() => templatesStore.activeTemplateId)

// Get current page context
const currentPage = computed(() => {
  const path = route.path
  if (path === '/' || path === '/home') return 'home'
  if (path.includes('data-structure')) return 'data-structures'
  if (path.includes('template-editor')) return 'template-editor'
  if (path.includes('preview')) return 'preview'
  return 'home'
})

// Get structure name for a template
function getStructureName(structureId: string): string {
  return structures.value?.find(s => s.id === structureId)?.name || 'Unknown'
}

function selectStructure(id: string) {
  dataStore.setActiveStructure(id)
}


function selectTemplate(id: string) {
  templatesStore.setActiveTemplate(id)
  if (route.path !== '/template-editor') {
    router.push('/template-editor')
  }
}

function goToGuide() {
  router.push('/guide')
}

function goToDataStructures() {
  router.push('/data-structures')
}

function goToTemplateEditor() {
  router.push('/template-editor')
}

function goToPreview() {
  router.push('/preview')
}

const componentSnippets = [
  {
    name: 'Paginated Section',
    icon: 'bi-file-earmark-break',
    description: 'Each row on separate page',
    snippet: `{{#rows}}
<div class="report-page">
  <div class="report-page-header">
    <h2>Item: {{name}}</h2>
  </div>
  
  <div class="report-page-content">
    <!-- Your content for each page here -->
    <p>Field: {{field}}</p>
  </div>
  
  <div class="page-number">Page {{_index}} of {{_total}}</div>
</div>
{{/rows}}`,
  },
  {
    name: 'Page Break',
    icon: 'bi-scissors',
    description: 'Force new page',
    snippet: `<div class="page-break"></div>`,
  },
  {
    name: 'Tile',
    icon: 'bi-card-heading',
    description: 'Metric card',
    snippet: `<div class="report-tile tile-primary">
  <div class="report-tile-title">{{title}}</div>
  <div class="report-tile-value">{{value}}</div>
</div>`,
  },
  {
    name: 'Tile Row',
    icon: 'bi-grid-3x2',
    description: '4 tiles in a row',
    snippet: `<div class="row mb-4">
  <div class="col-md-3">
    <div class="report-tile tile-primary">
      <div class="report-tile-title">Metric 1</div>
      <div class="report-tile-value">{{value1}}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="report-tile tile-success">
      <div class="report-tile-title">Metric 2</div>
      <div class="report-tile-value">{{value2}}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="report-tile tile-warning">
      <div class="report-tile-title">Metric 3</div>
      <div class="report-tile-value">{{value3}}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="report-tile tile-danger">
      <div class="report-tile-title">Metric 4</div>
      <div class="report-tile-value">{{value4}}</div>
    </div>
  </div>
</div>`,
  },
  {
    name: 'Bar Chart',
    icon: 'bi-bar-chart',
    description: 'Vertical bar chart',
    snippet: `<div class="chart-container">
  <div class="chart-title">Chart Title</div>
  <div class="report-bar-chart" data-labels="{{#rows}}{{label}},{{/rows}}" data-values="{{#rows}}{{value}},{{/rows}}">
  </div>
</div>`,
  },
  {
    name: 'Pie Chart',
    icon: 'bi-pie-chart',
    description: 'Pie/donut chart',
    snippet: `<div class="chart-container">
  <div class="chart-title">Chart Title</div>
  <div class="report-pie-chart" data-labels="North,South,East,West" data-values="35,25,20,20">
  </div>
</div>`,
  },
  {
    name: 'Table',
    icon: 'bi-table',
    description: 'Data table',
    snippet: `<table class="report-table">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
      <th>Column 3</th>
    </tr>
  </thead>
  <tbody>
    {{#items}}
    <tr>
      <td>{{field1}}</td>
      <td>{{field2}}</td>
      <td>{{field3}}</td>
    </tr>
    {{/items}}
  </tbody>
</table>`,
  },
  {
    name: 'Status Badge',
    icon: 'bi-palette',
    description: 'Colour badge from field value',
    snippet: `<style>
  /* Add one rule per expected value — class = "status-" + field value */
  .status-approved { background-color: #198754; color: white; }
  .status-pending  { background-color: #fd7e14; color: white; }
  .status-rejected { background-color: #dc3545; color: white; }
</style>

{{#rows}}
<span class="badge fs-6 status-{{approval_status}}">{{approval_status}}</span>
{{/rows}}`,
  },
  {
    name: 'Paginated Table',
    icon: 'bi-table',
    description: 'Table with rows per page',
    snippet: `<!-- Page 1 of transactions -->
<div class="report-page">
  <h3>Transactions (Page 1)</h3>
  <table class="report-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Date</th>
        <th>Customer</th>
        <th>Total</th>
      </tr>
    </thead>
    <tbody>
      {{#transactions_page1}}
      <tr>
        <td>{{id}}</td>
        <td>{{date}}</td>
        <td>{{customer}}</td>
        <td>{{total}}</td>
      </tr>
      {{/transactions_page1}}
    </tbody>
  </table>
</div>`,
  },
]

function insertComponent(snippet: string) {
  const event = new CustomEvent('insert-snippet', { detail: snippet })
  window.dispatchEvent(event)
}

</script>

<template>
  <aside class="app-sidebar" :class="{ collapsed: collapsed }">
    <!-- Collapse Toggle Button -->
    <button
      class="sidebar-toggle"
      @click="emit('toggle')"
      :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      :aria-expanded="!collapsed"
      aria-controls="sidebar-content"
    >
      <i :class="['bi', collapsed ? 'bi-chevron-right' : 'bi-chevron-left']"></i>
    </button>

    <div id="sidebar-content" class="sidebar-content" v-show="!collapsed">
      <!-- HOME PAGE: Quick Links -->
      <template v-if="currentPage === 'home'">
        <div class="sidebar-section">
          <span class="sidebar-section-title">Quick Start</span>
          <button class="nav-btn" @click="goToGuide">
            <i class="bi bi-book me-2"></i>
            <span>Guide</span>
          </button>
          <button class="nav-btn" @click="goToDataStructures">
            <i class="bi bi-diagram-3 me-2"></i>
            <span>Data Structures</span>
            <span class="badge bg-secondary ms-auto">{{ structures?.length ?? 0 }}</span>
          </button>
          <button class="nav-btn" @click="goToTemplateEditor">
            <i class="bi bi-code-square me-2"></i>
            <span>Template Editor</span>
            <span class="badge bg-secondary ms-auto">{{ templates?.length ?? 0 }}</span>
          </button>
          <button class="nav-btn" @click="goToPreview">
            <i class="bi bi-file-earmark-pdf me-2"></i>
            <span>Preview & Export</span>
          </button>
        </div>
      </template>

      <!-- DATA STRUCTURES PAGE -->
      <template v-if="currentPage === 'data-structures'">
        <div class="sidebar-section">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="sidebar-section-title mb-0">Data Structures</span>
          </div>
          <div v-if="!structures?.length" class="text-muted small px-2">
            No structures defined yet
          </div>
          <div
            v-for="structure in (structures ?? [])"
            :key="structure.id"
            class="structure-list-item"
            :class="{ active: structure.id === activeStructureId }"
            @click="selectStructure(structure.id)"
          >
            <i class="bi bi-diagram-3 me-2"></i>
            <span class="item-name">{{ structure.name }}</span>
            <span class="badge bg-light text-dark ms-auto">{{ structure.fields?.length ?? 0 }} fields</span>
          </div>
        </div>

        <div class="sidebar-section">
          <span class="sidebar-section-title">Linked Templates</span>
          <div v-if="!activeStructureId" class="text-muted small px-2">
            Select a structure to see linked templates
          </div>
          <template v-else>
            <div
              v-for="template in (templates ?? []).filter(t => t.structure_id === activeStructureId)"
              :key="template.id"
              class="structure-list-item small"
              @click="selectTemplate(template.id)"
            >
              <i class="bi bi-file-code me-2"></i>
              {{ template.name }}
            </div>
            <div v-if="!(templates ?? []).filter(t => t.structure_id === activeStructureId).length" class="text-muted small px-2">
              No templates use this structure
            </div>
          </template>
        </div>
      </template>

      <!-- TEMPLATE EDITOR PAGE -->
      <template v-if="currentPage === 'template-editor'">
        <div class="sidebar-section">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="sidebar-section-title mb-0">Templates</span>
          </div>
          <div v-if="!templates?.length" class="text-muted small px-2">
            No templates created
          </div>
          <div
            v-for="template in (templates ?? [])"
            :key="template.id"
            class="template-list-item"
            :class="{ active: template.id === activeTemplateId }"
            @click="selectTemplate(template.id)"
          >
            <div class="template-info">
              <i class="bi bi-file-code me-2"></i>
              <span class="item-name">{{ template.name }}</span>
            </div>
            <div class="template-structure">
              <i class="bi bi-link-45deg"></i>
              {{ getStructureName(template.structure_id) }}
            </div>
          </div>
        </div>

        <div class="sidebar-section">
          <span class="sidebar-section-title">Insert Component</span>
          <button
            v-for="comp in componentSnippets"
            :key="comp.name"
            class="component-btn"
            :title="comp.description"
            @click="insertComponent(comp.snippet)"
          >
            <i :class="['bi', comp.icon, 'me-2']"></i>
            <div class="component-info">
              <div class="component-name">{{ comp.name }}</div>
              <div class="component-desc">{{ comp.description }}</div>
            </div>
          </button>
        </div>
      </template>

      <!-- PREVIEW PAGE -->
      <template v-if="currentPage === 'preview'">
        <div class="sidebar-section">
          <span class="sidebar-section-title">Select Template</span>
          <div v-if="!templates?.length" class="text-muted small px-2">
            No templates available
          </div>
          <div
            v-for="template in (templates ?? [])"
            :key="template.id"
            class="template-list-item"
            :class="{ active: template.id === activeTemplateId }"
            @click="templatesStore.setActiveTemplate(template.id)"
          >
            <div class="template-info">
              <i class="bi bi-file-code me-2"></i>
              <span class="item-name">{{ template.name }}</span>
            </div>
            <div class="template-structure">
              <i class="bi bi-link-45deg"></i>
              {{ getStructureName(template.structure_id) }}
            </div>
          </div>
        </div>

        <div class="sidebar-section">
          <span class="sidebar-section-title">Export Options</span>
          <div class="export-info small text-muted px-2 mb-2">
            Select a template above, then use the Export button in the main panel.
          </div>
        </div>
      </template>
    </div>

    <!-- Collapsed state icons -->
    <div class="sidebar-collapsed-icons" v-show="collapsed">
      <button class="collapsed-icon-btn" @click="goToGuide" title="Guide">
        <i class="bi bi-book"></i>
      </button>
      <button class="collapsed-icon-btn" @click="goToDataStructures" title="Data Structures">
        <i class="bi bi-diagram-3"></i>
      </button>
      <button class="collapsed-icon-btn" @click="goToTemplateEditor" title="Templates">
        <i class="bi bi-code-square"></i>
      </button>
      <button class="collapsed-icon-btn" @click="goToPreview" title="Preview & Export">
        <i class="bi bi-file-earmark-pdf"></i>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  transition: width 0.3s ease;
}

.app-sidebar.collapsed {
  width: 56px !important;
}

.sidebar-toggle {
  position: absolute;
  top: 12px;
  right: -12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
}

.sidebar-toggle:hover {
  background: var(--pr-info);
  color: white;
  border-color: var(--pr-info);
}

.sidebar-content {
  padding-top: 8px;
}

.sidebar-collapsed-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 1rem;
  gap: 0.5rem;
}

.collapsed-icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #495057;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.collapsed-icon-btn:hover {
  background: var(--pr-info);
  color: white;
}

.collapsed-icon-btn i {
  font-size: 1.25rem;
}

.nav-btn {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 6px;
  margin-bottom: 0.25rem;
}

.nav-btn:hover {
  background: #f0f4f8;
}

.structure-list-item {
  display: flex;
  align-items: center;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 6px;
  margin: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.structure-list-item:hover {
  background: #f0f4f8;
}

.structure-list-item.active {
  background: var(--pr-info);
  color: white;
}

.structure-list-item.active .badge {
  background: rgba(255,255,255,0.2) !important;
  color: white !important;
}

.item-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.template-list-item {
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 6px;
  margin: 0.25rem 0.5rem;
  border: 1px solid transparent;
}

.template-list-item:hover {
  background: #f0f4f8;
  border-color: #e0e0e0;
}

.template-list-item.active {
  background: #e3f2fd;
  border-color: var(--pr-info);
}

.template-info {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 500;
}

.template-structure {
  font-size: 0.7rem;
  color: #6c757d;
  margin-top: 0.25rem;
  margin-left: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.template-list-item.active .template-structure {
  color: var(--pr-info);
}

.component-btn {
  width: 100%;
  display: flex;
  align-items: flex-start;
  padding: 0.6rem 0.75rem;
  border: 1px solid #e9ecef;
  background: white;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 6px;
  margin-bottom: 0.4rem;
}

.component-btn:hover {
  background: var(--pr-info);
  color: white;
  border-color: var(--pr-info);
}

.component-info {
  flex: 1;
}

.component-name {
  font-weight: 500;
  font-size: 0.8rem;
}

.component-desc {
  font-size: 0.65rem;
  color: #6c757d;
  margin-top: 1px;
}

.component-btn:hover .component-desc {
  color: rgba(255, 255, 255, 0.8);
}

.export-info {
  line-height: 1.4;
}
</style>
