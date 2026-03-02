<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function navigate(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="home-view">
    <div class="text-center mb-5">
      <h1 class="display-4 fw-bold mb-3">
        <i class="bi bi-file-earmark-richtext text-primary me-3"></i>
        Paginated Reporting
      </h1>
      <p class="lead text-muted">
        Create beautiful, data-driven reports with dynamic templates and PDF export
      </p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="feature-icon bg-primary bg-gradient text-white rounded-circle mb-3 mx-auto">
              <i class="bi bi-diagram-3 fs-3"></i>
            </div>
            <h5 class="card-title">Define Data Structures</h5>
            <p class="card-text text-muted">
              Create flexible data models with support for nested arrays and objects
            </p>
            <button class="btn btn-outline-primary" @click="navigate('/data-structures')">
              <i class="bi bi-arrow-right me-1"></i>
              Get Started
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="feature-icon bg-success bg-gradient text-white rounded-circle mb-3 mx-auto">
              <i class="bi bi-code-square fs-3"></i>
            </div>
            <h5 class="card-title">Build Templates</h5>
            <p class="card-text text-muted">
              Design HTML templates with mustache syntax and live preview
            </p>
            <button class="btn btn-outline-success" @click="navigate('/template-editor')">
              <i class="bi bi-arrow-right me-1"></i>
              Create Template
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="feature-icon bg-danger bg-gradient text-white rounded-circle mb-3 mx-auto">
              <i class="bi bi-file-pdf fs-3"></i>
            </div>
            <h5 class="card-title">Export to PDF</h5>
            <p class="card-text text-muted">
              Generate professional PDF reports with pagination support
            </p>
            <button class="btn btn-outline-danger" @click="navigate('/preview')">
              <i class="bi bi-arrow-right me-1"></i>
              Preview & Export
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">
          <i class="bi bi-lightbulb text-warning me-2"></i>
          Quick Start Guide
        </h5>
      </div>
      <div class="card-body">
        <div class="row g-4">
          <div class="col-md-3">
            <div class="d-flex">
              <div class="step-number me-3">1</div>
              <div>
                <h6>Define Structure</h6>
                <p class="text-muted small mb-0">
                  Create a data model that matches your report data format
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="d-flex">
              <div class="step-number me-3">2</div>
              <div>
                <h6>Build Template</h6>
                <p class="text-muted small mb-0">
                  Design your report layout using HTML and mustache tags
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="d-flex">
              <div class="step-number me-3">3</div>
              <div>
                <h6>Add Components</h6>
                <p class="text-muted small mb-0">
                  Insert tiles, charts, and tables from the component palette
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="d-flex">
              <div class="step-number me-3">4</div>
              <div>
                <h6>Export PDF</h6>
                <p class="text-muted small mb-0">
                  Preview your report and download as a paginated PDF
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 1000px;
  margin: 0 auto;
}

.feature-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-number {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--pr-primary) 0%, var(--pr-secondary) 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12) !important;
}
</style>
