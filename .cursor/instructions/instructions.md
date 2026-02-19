# Paginated Reporting Frontend - Project Specification

## Project Overview
Build a static-rendered Vue3 TypeScript web application using Vite that enables users to create paginated reports. Users can define data structures, build dynamic HTML templates using mustache syntax, preview their reports in real-time, and export to PDF.

## Tech Stack
- **Framework:** Vue 3 with Composition API and `<script setup>` syntax
- **Language:** TypeScript (strict mode)
- **Build Tool:** Vite (configured for static site generation)
- **Styling:** Bootstrap 5 (via npm, not CDN)
- **PDF Export:** html2pdf.js or jsPDF with html2canvas
- **Charts:** Chart.js with vue-chartjs wrapper
- **Template Rendering:** Mustache.js for dynamic template interpolation
- **Icons:** Bootstrap Icons

## Core Features

### 1. Data Structure Builder
- Allow users to define a data model with fields
- Support field types: `string`, `number`, `boolean`, `date`, `array`, `object`
- Support ONE level of nested structure (e.g., `report.items[]` where items can have their own flat fields)
- Provide a visual UI to add/remove/edit fields
- Store structure in Pinia store

**Example Data Structure:**
interface DataField {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'array' | 'object';
  children?: DataField[]; // Only for array/object types, max 1 level deep
}

interface DataStructure {
  name: string;
  fields: DataField[];
}

### 2. Template Editor (Split View)
- Left panel: HTML editor with syntax highlighting (use a simple textarea with monospace font, or use Monaco
- Right panel: Live preview rendering the template with mock data
- Support mustache syntax: {{fieldName}}, {{#items}}...{{/items}} for loops
- Toolbar with buttons to insert predefined components
Predefined Component Snippets:
- Tile: A styled card showing a metric (title + value)
- Bar Chart: Renders a bar chart from array data
- Pie Chart: Renders a pie chart from array data
- Table: Renders a data table from array data

### 3. Predefined Report Components
```html
<!-- Tile Component -->
<div class="report-tile" data-title="{{title}}" data-value="{{value}}" data-color="primary"></div>
<!-- Bar Chart Component -->
 <div class="report-bar-chart" data-labels="{{#items}}{{label}},{{/items}}" data-values="{{#items}}{{value}},{{/items}}"></div>
<!-- Pie Chart Component -->
 <div class="report-pie-chart" data-labels="{{#items}}{{label}},{{/items}}" data-values="{{#items}}{{value}},{{/items}}"></div>
<!-- Table Component -->
 <div class="report-table" data-columns="Name,Amount,Date">  {{#items}}  <tr><td>{{name}}</td><td>{{amount}}</td><td>{{date}}</td></tr>  {{/items}}</div>
```

### 4. PDF Export
Button to download the rendered preview as a PDF
Maintain page breaks and styling
Use html2pdf.js for conversion

### 5. Navigation & Layout
Navbar: App title, main navigation links
Sidebar:
Data structure list/selector
Component palette (click-to-insert)
Export options
Main Content: Router view for different pages



## UI/UX Requirements
- Clean, professional Bootstrap styling
- Responsive layout (but primarily desktop-focused)
- Split view should be resizable or have sensible fixed proportions (50/50 or 40/60)
- Toast notifications for actions (save, export, etc.)
- Form validation for data structure builder

## Getting Started Commands
npm create vite@latest . -- --template vue-ts
npm install bootstrap bootstrap-icons
npm install pinia vue-router
npm install chart.js vue-chartjs
npm install mustache
npm install html2pdf.js
npm install @types/mustache --save-dev



## Additional Notes
Use Pinia for state management
Use Vue Router for navigation
Keep the design simple but polished
The preview should update in real-time as the user types in the editor using a sample if one is there alternativly just add the placeholder 


## Mock Datastructures 

```javascript
// ============================================
// MOCK DATA STRUCTURES
// ============================================

// Mock 1: Sales Report - Multi-page transaction data
const salesReportData = {
  // Report metadata
  reportTitle: "Q4 2025 Sales Report",
  companyName: "Acme Corporation",
  generatedDate: "2025-12-31",
  reportPeriod: "October 1, 2025 - December 31, 2025",
  
  // Summary metrics (for tiles)
  totalRevenue: 2847500,
  totalOrders: 1247,
  avgOrderValue: 2283.45,
  returnRate: 3.2,
  
  // Regional breakdown (for pie/bar charts)
  regions: [
    { name: "North America", value: 1250000, percentage: 44 },
    { name: "Europe", value: 854250, percentage: 30 },
    { name: "Asia Pacific", value: 456750, percentage: 16 },
    { name: "Latin America", value: 186500, percentage: 7 },
    { name: "Other", value: 100000, percentage: 3 },
  ],
  
  // Transaction line items - enough for 3-4 pages at ~15 rows per page
  transactions: [
    { id: "TXN-001", date: "2025-10-02", customer: "Globex Industries", product: "Enterprise Suite", quantity: 5, unitPrice: 2500, total: 12500, status: "Completed" },
    { id: "TXN-002", date: "2025-10-03", customer: "Initech LLC", product: "Pro License", quantity: 12, unitPrice: 450, total: 5400, status: "Completed" },
    { id: "TXN-003", date: "2025-10-05", customer: "Umbrella Corp", product: "Enterprise Suite", quantity: 3, unitPrice: 2500, total: 7500, status: "Completed" },
    { id: "TXN-004", date: "2025-10-07", customer: "Stark Industries", product: "Premium Add-on", quantity: 8, unitPrice: 750, total: 6000, status: "Completed" },
    { id: "TXN-005", date: "2025-10-08", customer: "Wayne Enterprises", product: "Enterprise Suite", quantity: 10, unitPrice: 2500, total: 25000, status: "Completed" },
    { id: "TXN-006", date: "2025-10-10", customer: "Cyberdyne Systems", product: "Pro License", quantity: 25, unitPrice: 450, total: 11250, status: "Completed" },
    { id: "TXN-007", date: "2025-10-12", customer: "Oscorp Industries", product: "Basic Package", quantity: 50, unitPrice: 99, total: 4950, status: "Completed" },
    { id: "TXN-008", date: "2025-10-14", customer: "Massive Dynamic", product: "Enterprise Suite", quantity: 7, unitPrice: 2500, total: 17500, status: "Completed" },
    { id: "TXN-009", date: "2025-10-15", customer: "Weyland Corp", product: "Premium Add-on", quantity: 15, unitPrice: 750, total: 11250, status: "Pending" },
    { id: "TXN-010", date: "2025-10-17", customer: "Soylent Corp", product: "Pro License", quantity: 30, unitPrice: 450, total: 13500, status: "Completed" },
    { id: "TXN-011", date: "2025-10-19", customer: "Tyrell Corporation", product: "Enterprise Suite", quantity: 4, unitPrice: 2500, total: 10000, status: "Completed" },
    { id: "TXN-012", date: "2025-10-21", customer: "Aperture Science", product: "Basic Package", quantity: 100, unitPrice: 99, total: 9900, status: "Completed" },
    { id: "TXN-013", date: "2025-10-23", customer: "Black Mesa Research", product: "Pro License", quantity: 18, unitPrice: 450, total: 8100, status: "Completed" },
    { id: "TXN-014", date: "2025-10-25", customer: "Vault-Tec", product: "Enterprise Suite", quantity: 2, unitPrice: 2500, total: 5000, status: "Refunded" },
    { id: "TXN-015", date: "2025-10-27", customer: "InGen Technologies", product: "Premium Add-on", quantity: 20, unitPrice: 750, total: 15000, status: "Completed" },
    { id: "TXN-016", date: "2025-10-29", customer: "Virtucon Industries", product: "Pro License", quantity: 40, unitPrice: 450, total: 18000, status: "Completed" },
    { id: "TXN-017", date: "2025-11-01", customer: "Acme Corp", product: "Basic Package", quantity: 75, unitPrice: 99, total: 7425, status: "Completed" },
    { id: "TXN-018", date: "2025-11-03", customer: "LexCorp", product: "Enterprise Suite", quantity: 6, unitPrice: 2500, total: 15000, status: "Completed" },
    { id: "TXN-019", date: "2025-11-05", customer: "Oceanic Airlines", product: "Pro License", quantity: 22, unitPrice: 450, total: 9900, status: "Completed" },
    { id: "TXN-020", date: "2025-11-07", customer: "Dharma Initiative", product: "Premium Add-on", quantity: 10, unitPrice: 750, total: 7500, status: "Pending" },
    { id: "TXN-021", date: "2025-11-09", customer: "Hanso Foundation", product: "Enterprise Suite", quantity: 8, unitPrice: 2500, total: 20000, status: "Completed" },
    { id: "TXN-022", date: "2025-11-11", customer: "Gekko & Co", product: "Basic Package", quantity: 200, unitPrice: 99, total: 19800, status: "Completed" },
    { id: "TXN-023", date: "2025-11-13", customer: "Nakatomi Trading", product: "Pro License", quantity: 35, unitPrice: 450, total: 15750, status: "Completed" },
    { id: "TXN-024", date: "2025-11-15", customer: "Rekall Inc", product: "Enterprise Suite", quantity: 5, unitPrice: 2500, total: 12500, status: "Completed" },
    { id: "TXN-025", date: "2025-11-17", customer: "OCP Industries", product: "Premium Add-on", quantity: 25, unitPrice: 750, total: 18750, status: "Completed" },
    { id: "TXN-026", date: "2025-11-19", customer: "Yoyodyne Propulsion", product: "Pro License", quantity: 15, unitPrice: 450, total: 6750, status: "Refunded" },
    { id: "TXN-027", date: "2025-11-21", customer: "Spacely Sprockets", product: "Basic Package", quantity: 150, unitPrice: 99, total: 14850, status: "Completed" },
    { id: "TXN-028", date: "2025-11-23", customer: "Cogswell Cogs", product: "Enterprise Suite", quantity: 9, unitPrice: 2500, total: 22500, status: "Completed" },
    { id: "TXN-029", date: "2025-11-25", customer: "Duff Brewing", product: "Pro License", quantity: 28, unitPrice: 450, total: 12600, status: "Completed" },
    { id: "TXN-030", date: "2025-11-27", customer: "Krusty Industries", product: "Premium Add-on", quantity: 12, unitPrice: 750, total: 9000, status: "Completed" },
    { id: "TXN-031", date: "2025-11-29", customer: "Burns Enterprises", product: "Enterprise Suite", quantity: 15, unitPrice: 2500, total: 37500, status: "Completed" },
    { id: "TXN-032", date: "2025-12-01", customer: "Bluth Company", product: "Basic Package", quantity: 80, unitPrice: 99, total: 7920, status: "Pending" },
    { id: "TXN-033", date: "2025-12-03", customer: "Prestige Worldwide", product: "Pro License", quantity: 45, unitPrice: 450, total: 20250, status: "Completed" },
    { id: "TXN-034", date: "2025-12-05", customer: "Dunder Mifflin", product: "Enterprise Suite", quantity: 3, unitPrice: 2500, total: 7500, status: "Completed" },
    { id: "TXN-035", date: "2025-12-07", customer: "Wernham Hogg", product: "Premium Add-on", quantity: 18, unitPrice: 750, total: 13500, status: "Completed" },
    { id: "TXN-036", date: "2025-12-09", customer: "Sabre Corporation", product: "Pro License", quantity: 60, unitPrice: 450, total: 27000, status: "Completed" },
    { id: "TXN-037", date: "2025-12-11", customer: "Hooli Inc", product: "Enterprise Suite", quantity: 12, unitPrice: 2500, total: 30000, status: "Completed" },
    { id: "TXN-038", date: "2025-12-13", customer: "Pied Piper", product: "Basic Package", quantity: 25, unitPrice: 99, total: 2475, status: "Completed" },
    { id: "TXN-039", date: "2025-12-15", customer: "Raviga Capital", product: "Premium Add-on", quantity: 30, unitPrice: 750, total: 22500, status: "Completed" },
    { id: "TXN-040", date: "2025-12-17", customer: "Bachmanity", product: "Pro License", quantity: 8, unitPrice: 450, total: 3600, status: "Refunded" },
  ],
  
  // Monthly summary (for charts)
  monthlySummary: [
    { month: "October", revenue: 892350, orders: 412 },
    { month: "November", revenue: 987650, orders: 438 },
    { month: "December", revenue: 967500, orders: 397 },
  ],
  
  // Top products (for tables/charts)
  topProducts: [
    { name: "Enterprise Suite", unitsSold: 89, revenue: 222500 },
    { name: "Pro License", unitsSold: 338, revenue: 152100 },
    { name: "Premium Add-on", unitsSold: 138, revenue: 103500 },
    { name: "Basic Package", unitsSold: 680, revenue: 67320 },
  ],
};

// Mock 2: Employee Directory - Multi-page staff listing
const employeeDirectoryData = {
  // Report metadata
  reportTitle: "Employee Directory",
  department: "All Departments",
  asOfDate: "2025-12-31",
  
  // Summary stats
  totalEmployees: 48,
  activeEmployees: 45,
  onLeave: 3,
  avgTenureYears: 3.7,
  
  // Department breakdown (for charts)
  departments: [
    { name: "Engineering", count: 18, percentage: 38 },
    { name: "Sales", count: 12, percentage: 25 },
    { name: "Marketing", count: 8, percentage: 17 },
    { name: "Operations", count: 6, percentage: 12 },
    { name: "HR & Admin", count: 4, percentage: 8 },
  ],
  
  // Employee list - enough for pagination
  employees: [
    { id: "EMP-001", name: "Alice Johnson", department: "Engineering", role: "Senior Software Engineer", startDate: "2021-03-15", email: "alice.j@company.com", status: "Active" },
    { id: "EMP-002", name: "Bob Smith", department: "Engineering", role: "Tech Lead", startDate: "2019-08-01", email: "bob.s@company.com", status: "Active" },
    { id: "EMP-003", name: "Carol Williams", department: "Sales", role: "Account Executive", startDate: "2022-01-10", email: "carol.w@company.com", status: "Active" },
    { id: "EMP-004", name: "David Brown", department: "Marketing", role: "Content Manager", startDate: "2020-06-22", email: "david.b@company.com", status: "Active" },
    { id: "EMP-005", name: "Eva Martinez", department: "Engineering", role: "Junior Developer", startDate: "2024-02-14", email: "eva.m@company.com", status: "Active" },
    { id: "EMP-006", name: "Frank Lee", department: "Operations", role: "Operations Manager", startDate: "2018-11-30", email: "frank.l@company.com", status: "Active" },
    { id: "EMP-007", name: "Grace Chen", department: "Engineering", role: "DevOps Engineer", startDate: "2021-09-05", email: "grace.c@company.com", status: "On Leave" },
    { id: "EMP-008", name: "Henry Wilson", department: "Sales", role: "Sales Director", startDate: "2017-04-18", email: "henry.w@company.com", status: "Active" },
    { id: "EMP-009", name: "Iris Patel", department: "HR & Admin", role: "HR Manager", startDate: "2019-12-01", email: "iris.p@company.com", status: "Active" },
    { id: "EMP-010", name: "Jack Thompson", department: "Engineering", role: "Software Engineer", startDate: "2022-07-11", email: "jack.t@company.com", status: "Active" },
    { id: "EMP-011", name: "Karen Davis", department: "Marketing", role: "Marketing Director", startDate: "2018-02-28", email: "karen.d@company.com", status: "Active" },
    { id: "EMP-012", name: "Leo Garcia", department: "Sales", role: "Sales Representative", startDate: "2023-04-03", email: "leo.g@company.com", status: "Active" },
    { id: "EMP-013", name: "Mia Robinson", department: "Engineering", role: "QA Engineer", startDate: "2021-05-17", email: "mia.r@company.com", status: "Active" },
    { id: "EMP-014", name: "Nathan Kim", department: "Engineering", role: "Senior Software Engineer", startDate: "2020-01-06", email: "nathan.k@company.com", status: "Active" },
    { id: "EMP-015", name: "Olivia Scott", department: "Operations", role: "Logistics Coordinator", startDate: "2022-10-24", email: "olivia.s@company.com", status: "Active" },
    { id: "EMP-016", name: "Paul Anderson", department: "Sales", role: "Account Manager", startDate: "2021-08-09", email: "paul.a@company.com", status: "Active" },
    { id: "EMP-017", name: "Quinn Murphy", department: "Engineering", role: "Frontend Developer", startDate: "2023-01-16", email: "quinn.m@company.com", status: "Active" },
    { id: "EMP-018", name: "Rachel Green", department: "Marketing", role: "Social Media Manager", startDate: "2022-03-21", email: "rachel.g@company.com", status: "On Leave" },
    { id: "EMP-019", name: "Samuel Wright", department: "Engineering", role: "Backend Developer", startDate: "2020-11-02", email: "samuel.w@company.com", status: "Active" },
    { id: "EMP-020", name: "Tina Hernandez", department: "HR & Admin", role: "Recruiter", startDate: "2023-06-12", email: "tina.h@company.com", status: "Active" },
    { id: "EMP-021", name: "Uma Sharma", department: "Engineering", role: "Data Engineer", startDate: "2021-02-08", email: "uma.s@company.com", status: "Active" },
    { id: "EMP-022", name: "Victor Nguyen", department: "Sales", role: "Sales Representative", startDate: "2024-01-22", email: "victor.n@company.com", status: "Active" },
    { id: "EMP-023", name: "Wendy Taylor", department: "Marketing", role: "Brand Manager", startDate: "2019-07-14", email: "wendy.t@company.com", status: "Active" },
    { id: "EMP-024", name: "Xavier Lopez", department: "Engineering", role: "Security Engineer", startDate: "2020-04-27", email: "xavier.l@company.com", status: "Active" },
    { id: "EMP-025", name: "Yolanda King", department: "Operations", role: "Facilities Manager", startDate: "2018-09-19", email: "yolanda.k@company.com", status: "Active" },
    { id: "EMP-026", name: "Zachary Hall", department: "Engineering", role: "Mobile Developer", startDate: "2022-12-05", email: "zachary.h@company.com", status: "Active" },
    { id: "EMP-027", name: "Angela White", department: "Sales", role: "Account Executive", startDate: "2021-06-28", email: "angela.w@company.com", status: "Active" },
    { id: "EMP-028", name: "Brian Moore", department: "Marketing", role: "SEO Specialist", startDate: "2023-03-13", email: "brian.m@company.com", status: "On Leave" },
    { id: "EMP-029", name: "Christina Adams", department: "Engineering", role: "Software Engineer", startDate: "2022-08-07", email: "christina.a@company.com", status: "Active" },
    { id: "EMP-030", name: "Derek Nelson", department: "Sales", role: "Sales Manager", startDate: "2019-10-21", email: "derek.n@company.com", status: "Active" },
  ],
  
  // Tenure distribution (for charts)
  tenureDistribution: [
    { range: "0-1 years", count: 8 },
    { range: "1-2 years", count: 12 },
    { range: "2-3 years", count: 10 },
    { range: "3-5 years", count: 14 },
    { range: "5+ years", count: 4 },
  ],
};

// Mock 3: Inventory Report - Product stock levels
const inventoryReportData = {
  reportTitle: "Warehouse Inventory Report",
  warehouseLocation: "Central Distribution Center",
  reportDate: "2025-12-31",
  
  // Summary
  totalSKUs: 35,
  totalUnits: 24680,
  lowStockItems: 8,
  outOfStockItems: 2,
  inventoryValue: 487250,
  
  // Category breakdown
  categories: [
    { name: "Electronics", items: 12, value: 245000 },
    { name: "Furniture", items: 8, value: 125000 },
    { name: "Office Supplies", items: 10, value: 67250 },
    { name: "Accessories", items: 5, value: 50000 },
  ],
  
  // Inventory items
  items: [
    { sku: "SKU-E001", name: "Wireless Keyboard", category: "Electronics", quantity: 450, reorderPoint: 100, unitCost: 45.00, totalValue: 20250, status: "In Stock" },
    { sku: "SKU-E002", name: "USB-C Hub", category: "Electronics", quantity: 280, reorderPoint: 75, unitCost: 65.00, totalValue: 18200, status: "In Stock" },
    { sku: "SKU-E003", name: "27\" Monitor", category: "Electronics", quantity: 85, reorderPoint: 50, unitCost: 350.00, totalValue: 29750, status: "In Stock" },
    { sku: "SKU-E004", name: "Webcam HD", category: "Electronics", quantity: 42, reorderPoint: 60, unitCost: 89.00, totalValue: 3738, status: "Low Stock" },
    { sku: "SKU-E005", name: "Wireless Mouse", category: "Electronics", quantity: 620, reorderPoint: 150, unitCost: 35.00, totalValue: 21700, status: "In Stock" },
    { sku: "SKU-E006", name: "Laptop Stand", category: "Electronics", quantity: 180, reorderPoint: 50, unitCost: 55.00, totalValue: 9900, status: "In Stock" },
    { sku: "SKU-E007", name: "Noise-Canceling Headphones", category: "Electronics", quantity: 0, reorderPoint: 30, unitCost: 199.00, totalValue: 0, status: "Out of Stock" },
    { sku: "SKU-E008", name: "Docking Station", category: "Electronics", quantity: 95, reorderPoint: 40, unitCost: 175.00, totalValue: 16625, status: "In Stock" },
    { sku: "SKU-F001", name: "Standing Desk", category: "Furniture", quantity: 28, reorderPoint: 15, unitCost: 450.00, totalValue: 12600, status: "In Stock" },
    { sku: "SKU-F002", name: "Ergonomic Chair", category: "Furniture", quantity: 12, reorderPoint: 20, unitCost: 380.00, totalValue: 4560, status: "Low Stock" },
    { sku: "SKU-F003", name: "Filing Cabinet", category: "Furniture", quantity: 45, reorderPoint: 20, unitCost: 185.00, totalValue: 8325, status: "In Stock" },
    { sku: "SKU-F004", name: "Bookshelf Unit", category: "Furniture", quantity: 18, reorderPoint: 25, unitCost: 220.00, totalValue: 3960, status: "Low Stock" },
    { sku: "SKU-F005", name: "Conference Table", category: "Furniture", quantity: 8, reorderPoint: 5, unitCost: 850.00, totalValue: 6800, status: "In Stock" },
    { sku: "SKU-F006", name: "Guest Chair", category: "Furniture", quantity: 65, reorderPoint: 30, unitCost: 145.00, totalValue: 9425, status: "In Stock" },
    { sku: "SKU-O001", name: "Printer Paper (Ream)", category: "Office Supplies", quantity: 1200, reorderPoint: 500, unitCost: 8.50, totalValue: 10200, status: "In Stock" },
    { sku: "SKU-O002", name: "Ballpoint Pens (Box)", category: "Office Supplies", quantity: 340, reorderPoint: 100, unitCost: 12.00, totalValue: 4080, status: "In Stock" },
    { sku: "SKU-O003", name: "Sticky Notes (Pack)", category: "Office Supplies", quantity: 580, reorderPoint: 200, unitCost: 6.50, totalValue: 3770, status: "In Stock" },
    { sku: "SKU-O004", name: "Binder Clips (Box)", category: "Office Supplies", quantity: 420, reorderPoint: 150, unitCost: 4.25, totalValue: 1785, status: "In Stock" },
    { sku: "SKU-O005", name: "Whiteboard Markers", category: "Office Supplies", quantity: 75, reorderPoint: 100, unitCost: 15.00, totalValue: 1125, status: "Low Stock" },
    { sku: "SKU-O006", name: "Stapler", category: "Office Supplies", quantity: 0, reorderPoint: 25, unitCost: 18.00, totalValue: 0, status: "Out of Stock" },
    { sku: "SKU-O007", name: "Scissors", category: "Office Supplies", quantity: 145, reorderPoint: 50, unitCost: 7.50, totalValue: 1088, status: "In Stock" },
    { sku: "SKU-A001", name: "Cable Organizer", category: "Accessories", quantity: 890, reorderPoint: 200, unitCost: 12.00, totalValue: 10680, status: "In Stock" },
    { sku: "SKU-A002", name: "Monitor Arm", category: "Accessories", quantity: 55, reorderPoint: 30, unitCost: 125.00, totalValue: 6875, status: "In Stock" },
    { sku: "SKU-A003", name: "Desk Pad", category: "Accessories", quantity: 210, reorderPoint: 75, unitCost: 28.00, totalValue: 5880, status: "In Stock" },
    { sku: "SKU-A004", name: "Phone Stand", category: "Accessories", quantity: 48, reorderPoint: 60, unitCost: 22.00, totalValue: 1056, status: "Low Stock" },
    { sku: "SKU-A005", name: "Desk Lamp", category: "Accessories", quantity: 62, reorderPoint: 80, unitCost: 45.00, totalValue: 2790, status: "Low Stock" },
  ],
};

// Pagination helper data
const paginationConfig = {
  rowsPerPage: 15,  // Typical rows that fit on one page
  pageBreakClass: "page-break",  // CSS class for forcing page breaks
};
```