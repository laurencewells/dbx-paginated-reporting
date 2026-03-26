import{d as m,c as r,a as t,b as a,F as u,w as f,e as c,z as n,y as d,E as g,o,x as v,_ as h}from"./index-DuJWz9Ao.js";const y={class:"guide-view"},_={class:"row g-4"},w={class:"col-md-3"},x={class:"card sticky-top",style:{top:"calc(var(--pr-navbar-height) + 1rem)"}},k={class:"card-body p-2"},S=["onClick"],T={class:"col-md-9"},C={key:0},A={key:1},R={class:"card mb-4"},j={class:"card-body p-0"},E={class:"table table-sm mb-0"},L={class:"syntax-tag"},P={class:"syntax-tag"},M={class:"syntax-tag"},U={class:"syntax-tag"},q={class:"syntax-tag"},I={class:"syntax-tag"},D={class:"alert alert-warning"},N={class:"ms-1"},O={class:"card"},Q={class:"card-body"},B={class:"code-block"},F={class:"mb-0 small text-muted mt-2"},H={key:2},V={class:"pattern-step"},G={class:"code-block"},Y={class:"pattern-step"},W={class:"code-block"},z={class:"pattern-step"},K={class:"code-block"},J={class:"alert alert-info"},$={key:3},X={class:"pattern-step"},Z={class:"code-block"},tt={class:"pattern-step"},et={class:"code-block"},at={class:"pattern-step"},dt={class:"row g-3"},st={class:"col-md-6"},lt={class:"approach-card"},it={class:"code-block"},rt={class:"small text-muted mt-2 mb-0"},ot={class:"col-md-6"},nt={class:"approach-card"},ct={class:"code-block"},bt={key:4},vt={class:"pattern-step"},pt={class:"code-block"},mt={class:"pattern-step"},ut={class:"code-block"},ft={class:"pattern-step"},gt={class:"code-block"},ht={class:"alert alert-info"},yt={key:5},_t={class:"pattern-card mb-4"},wt={class:"card-body"},xt={class:"code-block"},kt={class:"pattern-card mb-4"},St={class:"card-body"},Tt={class:"code-block"},Ct={class:"pattern-card mb-4"},At={class:"card-body"},Rt={class:"pattern-step"},jt={class:"code-block"},Et={class:"pattern-step"},Lt={class:"code-block"},Pt={class:"pattern-step"},Mt={class:"code-block"},Ut={key:6},qt={class:"pattern-card mb-4"},It={class:"card-body"},Dt={class:"pattern-step"},Nt={class:"code-block"},Ot={class:"pattern-step"},Qt={class:"code-block"},Bt={class:"alert alert-success mb-0"},Ft={class:"pattern-card mb-4"},Ht={class:"card-body"},Vt={class:"small text-muted mb-3"},Gt={class:"pattern-step"},Yt={class:"code-block"},Wt={class:"pattern-step"},zt={class:"code-block"},Kt={key:7},Jt={class:"pattern-card mb-4"},$t={class:"card-body"},Xt={class:"pattern-step"},Zt={class:"code-block"},te={class:"pattern-step"},ee={class:"code-block"},ae={class:"pattern-step"},de={class:"code-block"},se={key:8},le=m({__name:"GuideView",setup(ie){const i=g("projects"),p=[{id:"projects",label:"Projects",icon:"bi-folder2-open"},{id:"mustache",label:"Mustache Syntax",icon:"bi-braces"},{id:"flat-table",label:"Flat Table",icon:"bi-table"},{id:"struct",label:"Struct Fields",icon:"bi-braces-asterisk"},{id:"array-struct",label:"Array of Structs",icon:"bi-list-nested"},{id:"chart-struct",label:"Charts from Structs",icon:"bi-bar-chart"},{id:"conditional-styles",label:"Conditional Styles",icon:"bi-palette"},{id:"images",label:"Images",icon:"bi-images"},{id:"scheduling",label:"Scheduling",icon:"bi-clock-history"}],s={variable:"{{field}}",triple:"{{{field}}}",section:"{{#section}}...{{/section}}",inverted:"{{^section}}...{{/section}}",dot:"{{.}}",comment:"{{! comment }}",ex_field:"{{cluster_name}}",ex_dot_loop:"{{#tags}}{{.}}{{/tags}}",ex_comment:"{{! TODO: add chart }}",rows_open:"{{#rows}}",rows_close:"{{/rows}}",rows_wrong:"{{/#}}",delete_check:"{{^delete_time}}Active{{/delete_time}}",index:"{{_index}}",total:"{{_total}}",address_open:"{{#address}}",cond_class_example:"status-{{approval_status}}"},l={dataShape:`{
  "rows": [
    { "field1": "value", "field2": 42 },
    { "field1": "value", "field2": 99 }
  ]
}`,flatTable_sql:`-- system.compute.clusters (example)
cluster_name   VARCHAR
cluster_id     VARCHAR
owned_by       VARCHAR
worker_count   INT
create_time    TIMESTAMP
delete_time    TIMESTAMP   -- NULL if still active`,flatTable_data:`{
  "rows": [
    {
      "cluster_name": "ml-team-gpu",
      "cluster_id": "0120-123456-abc",
      "owned_by": "user@example.com",
      "worker_count": 4,
      "create_time": "2024-01-15T10:30:00",
      "delete_time": null,
      "_index": 1,
      "_total": 42
    },
    ...
  ]
}`,flatTable_template:`<div class="report-page">
  <div class="p-4">
    <h1 class="fw-bold text-primary">Cluster Report</h1>
    <hr>

    <table class="report-table table table-striped">
      <thead>
        <tr>
          <th>Cluster Name</th>
          <th>Owner</th>
          <th>Workers</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {{#rows}}
        <tr>
          <td class="fw-semibold">{{cluster_name}}</td>
          <td>{{owned_by}}</td>
          <td><span class="badge bg-primary">{{worker_count}}</span></td>
          <td>
            {{^delete_time}}<span class="badge bg-success">Active</span>{{/delete_time}}
            {{#delete_time}}<span class="badge bg-danger">Terminated</span>{{/delete_time}}
          </td>
        </tr>
        {{/rows}}
        {{^rows}}
        <tr><td colspan="4" class="text-center text-muted py-4">No data</td></tr>
        {{/rows}}
      </tbody>
    </table>

    <div class="page-number">Page {{_index}} of {{_total}}</div>
  </div>
</div>`,struct_sql:`-- employee table
name          VARCHAR
department    VARCHAR
address       STRUCT<
                city:    VARCHAR,
                country: VARCHAR,
                zip:     VARCHAR
              >`,struct_data:`{
  "rows": [
    {
      "name": "Alice",
      "department": "Engineering",
      "address": {
        "city": "London",
        "country": "UK",
        "zip": "EC1A 1BB"
      }
    }
  ]
}`,struct_context:`{{#rows}}
  <td>{{name}}</td>

  {{#address}}
    <td>{{city}}</td>
    <td>{{country}}</td>
    <td>{{zip}}</td>
  {{/address}}
{{/rows}}`,struct_dot:`{{#rows}}
  <td>{{name}}</td>
  <td>{{address.city}}</td>
  <td>{{address.country}}</td>
  <td>{{address.zip}}</td>
{{/rows}}`,array_sql:`-- order table
order_id      VARCHAR
customer      VARCHAR
items         ARRAY<STRUCT<
                product: VARCHAR,
                qty:     INT,
                price:   DOUBLE
              >>`,array_data:`{
  "rows": [
    {
      "order_id": "ORD-001",
      "customer": "Acme Corp",
      "items": [
        { "product": "Widget A", "qty": 3, "price": 9.99 },
        { "product": "Widget B", "qty": 1, "price": 24.99 }
      ]
    }
  ]
}`,array_template:`{{#rows}}
<div class="report-page">
  <div class="p-4">
    <h2>Order: {{order_id}}</h2>
    <p class="text-muted">Customer: {{customer}}</p>

    <table class="report-table table">
      <thead>
        <tr>
          <th>Product</th>
          <th>Qty</th>
          <th>Unit Price</th>
        </tr>
      </thead>
      <tbody>
        {{#items}}
        <tr>
          <td>{{product}}</td>
          <td>{{qty}}</td>
          <td>£{{price}}</td>
        </tr>
        {{/items}}
      </tbody>
    </table>

    <div class="page-number">Page {{_index}} of {{_total}}</div>
  </div>
</div>
{{/rows}}`,chart1_template:`<!-- SQL: SELECT region, SUM(revenue) as total FROM sales GROUP BY region -->

<div class="chart-container">
  <div class="chart-title">Revenue by Region</div>
  <div class="report-bar-chart"
    data-labels="{{#rows}}{{region}},{{/rows}}"
    data-values="{{#rows}}{{total}},{{/rows}}">
  </div>
</div>`,chart2_template:`<!-- SQL: SELECT active_count, terminated_count FROM cluster_summary -->

<div class="chart-container">
  <div class="chart-title">Cluster Status</div>
  <div class="report-pie-chart"
    data-labels="Active,Terminated"
    data-values="{{#rows}}{{active_count}},{{terminated_count}}{{/rows}}">
  </div>
</div>`,chart3_sql:`SELECT
  team_name,
  headcount,
  -- pre-aggregate monthly spend into an array
  array_agg(
    named_struct('month', month_name, 'spend', monthly_spend)
    ORDER BY month_num
  ) AS spend_by_month
FROM team_metrics
GROUP BY team_name, headcount`,chart3_data:`{
  "rows": [
    {
      "team_name": "Engineering",
      "headcount": 24,
      "spend_by_month": [
        { "month": "Jan", "spend": 48000 },
        { "month": "Feb", "spend": 52000 },
        { "month": "Mar", "spend": 51000 }
      ]
    }
  ]
}`,conditional_sql_pattern1:`-- No changes needed — use the field value directly as a CSS class
SELECT
  supplier_name,
  approval_status,   -- e.g. 'approved', 'pending', 'rejected'
  category,
  onboarded_date
FROM procurement.suppliers`,conditional_template_pattern1:`<style>
  /* Class name = "status-" + the field value */
  .status-approved { background-color: #198754; color: white; }
  .status-pending  { background-color: #fd7e14; color: white; }
  .status-rejected { background-color: #dc3545; color: white; }
</style>

{{#rows}}
<div class="report-page">
  <div class="report-page-header d-flex justify-content-between align-items-center">
    <h2>{{supplier_name}}</h2>
    <span class="badge fs-6 status-{{approval_status}}">{{approval_status}}</span>
  </div>

  <div class="row mb-4">
    <div class="col-md-6">
      <p class="text-muted mb-1">Category</p>
      <p class="fw-semibold">{{category}}</p>
    </div>
    <div class="col-md-6">
      <p class="text-muted mb-1">Onboarded</p>
      <p class="fw-semibold">{{onboarded_date}}</p>
    </div>
  </div>

  <div class="page-number">Supplier {{_index}} of {{_total}}</div>
</div>
{{/rows}}`,conditional_sql_pattern2:`-- Add boolean columns in SQL for full block conditionals
SELECT
  supplier_name,
  approval_status,
  category,
  onboarded_date,
  approval_status = 'approved' AS is_approved,
  approval_status = 'pending'  AS is_pending,
  approval_status = 'rejected' AS is_rejected
FROM procurement.suppliers`,conditional_template_pattern2:`{{#rows}}
<div class="report-page">
  <div class="report-page-header">
    <h2>{{supplier_name}}</h2>
  </div>

  {{#is_approved}}
  <div class="alert alert-success">
    <i class="bi bi-check-circle-fill me-2"></i>
    This supplier is <strong>approved</strong> and active.
  </div>
  {{/is_approved}}

  {{#is_pending}}
  <div class="alert alert-warning">
    <i class="bi bi-hourglass-split me-2"></i>
    Approval is <strong>pending</strong> — review in progress.
  </div>
  {{/is_pending}}

  {{#is_rejected}}
  <div class="alert alert-danger">
    <i class="bi bi-x-circle-fill me-2"></i>
    This supplier has been <strong>rejected</strong>.
  </div>
  {{/is_rejected}}

  <div class="page-number">Supplier {{_index}} of {{_total}}</div>
</div>
{{/rows}}`,image_basic:'<img src="/api/v1/images/IMAGE_ID/data" alt="Description" />',image_header:`<div class="report-page">
  <div class="report-page-header d-flex align-items-center gap-3">
    <img src="/api/v1/images/IMAGE_ID/data"
         alt="Company Logo"
         style="height: 48px;" />
    <h1 class="mb-0">Monthly Report</h1>
  </div>

  <div class="report-page-content">
    <!-- report content here -->
  </div>
</div>`,image_styled:`<img src="/api/v1/images/IMAGE_ID/data"
     alt="Product photo"
     style="max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />`,chart3_template:`{{#rows}}
<div class="report-page">
  <div class="p-4">

    <!-- KPI tiles -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="report-tile tile-primary">
          <div class="report-tile-title">Team</div>
          <div class="report-tile-value">{{team_name}}</div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="report-tile tile-success">
          <div class="report-tile-title">Headcount</div>
          <div class="report-tile-value">{{headcount}}</div>
        </div>
      </div>
    </div>

    <!-- Chart driven by the struct array column -->
    <div class="chart-container">
      <div class="chart-title">Monthly Spend</div>
      <div class="report-bar-chart"
        data-labels="{{#spend_by_month}}{{month}},{{/spend_by_month}}"
        data-values="{{#spend_by_month}}{{spend}},{{/spend_by_month}}">
      </div>
    </div>

    <div class="page-number">Page {{_index}} of {{_total}}</div>
  </div>
</div>
{{/rows}}`};return(re,e)=>(o(),r("div",y,[e[99]||(e[99]=t("div",{class:"guide-header mb-4"},[t("h2",{class:"mb-1"},[t("i",{class:"bi bi-book text-primary me-2"}),a(" Template Guide ")]),t("p",{class:"text-muted mb-0"}," How to structure your data and write Mustache templates for reports ")],-1)),t("div",_,[t("div",w,[t("div",x,[t("div",k,[(o(),r(u,null,f(p,b=>t("button",{key:b.id,class:v(["guide-nav-btn",{active:i.value===b.id}]),onClick:oe=>i.value=b.id},[t("i",{class:v(["bi",b.icon,"me-2"])},null,2),a(" "+d(b.label),1)],10,S)),64))])])]),t("div",T,[i.value==="projects"?(o(),r("div",C,[...e[0]||(e[0]=[c('<h4 class="section-title" data-v-7ef7db27><i class="bi bi-folder2-open me-2 text-primary" data-v-7ef7db27></i>Projects</h4><p class="text-muted" data-v-7ef7db27>Projects group related data structures and templates together, making it easy to organise, share, and lock your work.</p><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-lightning me-2 text-warning" data-v-7ef7db27></i>Getting started</div><div class="card-body" data-v-7ef7db27><ol class="mb-0" data-v-7ef7db27><li class="mb-2" data-v-7ef7db27>Navigate to <strong data-v-7ef7db27>Projects</strong> and click <strong data-v-7ef7db27>New Project</strong>.</li><li class="mb-2" data-v-7ef7db27>Give it a name (e.g. &quot;Q1 Sales Reports&quot;) and click <strong data-v-7ef7db27>Create</strong>.</li><li class="mb-2" data-v-7ef7db27>Click <strong data-v-7ef7db27>Open</strong> to set it as your active project — you&#39;ll see a banner in the sidebar.</li><li class="mb-2" data-v-7ef7db27>Now go to <strong data-v-7ef7db27>Data Structures</strong> — any structures you create will automatically belong to this project.</li><li data-v-7ef7db27>Create templates linked to those structures, then use the <strong data-v-7ef7db27>Export</strong> button in the Template Editor to preview and export PDF.</li></ol></div></div><div class="row g-4 mb-4" data-v-7ef7db27><div class="col-md-6" data-v-7ef7db27><div class="card h-100" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-diagram-3 me-2 text-primary" data-v-7ef7db27></i>How structures are linked</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27>When a project is active, new structures are automatically associated with it via a <code data-v-7ef7db27>project_id</code> field.</p><p class="small mb-2" data-v-7ef7db27>The Data Structures and Template Editor pages filter their lists to show only items belonging to the active project.</p><p class="small mb-0 text-muted" data-v-7ef7db27>Clear the project filter (click the <i class="bi bi-x-lg" data-v-7ef7db27></i> in the sidebar banner) to see all structures across all projects.</p></div></div></div><div class="col-md-6" data-v-7ef7db27><div class="card h-100" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-file-code me-2 text-success" data-v-7ef7db27></i>How templates are linked</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27>Templates don&#39;t have a direct project link — they&#39;re associated through their <strong data-v-7ef7db27>structure</strong>.</p><p class="small mb-0" data-v-7ef7db27>When filtering by project, the app shows templates whose linked structure belongs to the active project.</p></div></div></div></div><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-lock me-2 text-warning" data-v-7ef7db27></i>Locking</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27>Only the project <strong data-v-7ef7db27>owner</strong> can lock or unlock a project.</p><p class="small mb-2" data-v-7ef7db27>When a project is <strong data-v-7ef7db27>locked</strong>, all create, update, and delete operations on its structures and templates are blocked with a <code data-v-7ef7db27>423 Locked</code> response.</p><p class="small mb-0 text-muted" data-v-7ef7db27>This is useful when a report set is finalised and you want to prevent accidental edits.</p></div></div><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-people me-2 text-info" data-v-7ef7db27></i>Sharing</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27>Share a project with colleagues by entering their email address on the project detail panel.</p><p class="small mb-2" data-v-7ef7db27>Shared users can <strong data-v-7ef7db27>view</strong> and <strong data-v-7ef7db27>edit</strong> structures and templates in the project (unless it&#39;s locked).</p><p class="small mb-2" data-v-7ef7db27>Only the project <strong data-v-7ef7db27>owner</strong> can:</p><ul class="small mb-0" data-v-7ef7db27><li data-v-7ef7db27>Lock / unlock the project</li><li data-v-7ef7db27>Add or remove shares</li><li data-v-7ef7db27>Delete the project</li></ul></div></div><div class="card" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-table me-2" data-v-7ef7db27></i>Permission summary</div><div class="card-body p-0" data-v-7ef7db27><table class="table table-sm mb-0" data-v-7ef7db27><thead class="table-dark" data-v-7ef7db27><tr data-v-7ef7db27><th data-v-7ef7db27>Action</th><th data-v-7ef7db27>Owner</th><th data-v-7ef7db27>Shared user</th></tr></thead><tbody data-v-7ef7db27><tr data-v-7ef7db27><td data-v-7ef7db27>View structures &amp; templates</td><td class="text-success" data-v-7ef7db27>Yes</td><td class="text-success" data-v-7ef7db27>Yes</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27>Create / edit / delete structures &amp; templates</td><td class="text-success" data-v-7ef7db27>Yes (if unlocked)</td><td class="text-success" data-v-7ef7db27>Yes (if unlocked)</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27>Lock / unlock project</td><td class="text-success" data-v-7ef7db27>Yes</td><td class="text-danger" data-v-7ef7db27>No</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27>Share / unshare project</td><td class="text-success" data-v-7ef7db27>Yes</td><td class="text-danger" data-v-7ef7db27>No</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27>Delete project</td><td class="text-success" data-v-7ef7db27>Yes</td><td class="text-danger" data-v-7ef7db27>No</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27>Rename project</td><td class="text-success" data-v-7ef7db27>Yes</td><td class="text-danger" data-v-7ef7db27>No</td></tr></tbody></table></div></div>',7)])])):n("",!0),i.value==="mustache"?(o(),r("div",A,[e[21]||(e[21]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces me-2 text-primary"}),a("Mustache Syntax Reference")],-1)),e[22]||(e[22]=t("p",{class:"text-muted"},[a("Mustache is a logic-less templating language. All data comes from the "),t("code",null,"rows"),a(" array returned by your SQL query.")],-1)),t("div",R,[t("div",j,[t("table",E,[e[10]||(e[10]=t("thead",{class:"table-dark"},[t("tr",null,[t("th",null,"Syntax"),t("th",null,"Purpose"),t("th",null,"Example")])],-1)),t("tbody",null,[t("tr",null,[t("td",null,[t("code",L,d(s.variable),1)]),e[1]||(e[1]=t("td",null,"Render a value (HTML-escaped)",-1)),t("td",null,[t("code",null,d(s.ex_field),1)])]),t("tr",null,[t("td",null,[t("code",P,d(s.triple),1)]),e[2]||(e[2]=t("td",null,"Render raw HTML (unescaped)",-1)),t("td",null,[t("code",null,d(s.triple),1)])]),t("tr",null,[t("td",null,[t("code",M,d(s.section),1)]),e[3]||(e[3]=t("td",null,[a("Iterate array "),t("strong",null,"or"),a(" render if truthy")],-1)),t("td",null,[t("code",null,d(s.rows_open)+"..."+d(s.rows_close),1)])]),t("tr",null,[t("td",null,[t("code",U,d(s.inverted),1)]),e[4]||(e[4]=t("td",null,"Render if falsy or empty",-1)),t("td",null,[t("code",null,d(s.delete_check),1)])]),t("tr",null,[t("td",null,[t("code",q,d(s.dot),1)]),e[8]||(e[8]=t("td",null,[a("Current item in a "),t("em",null,"scalar"),a(" list only")],-1)),t("td",null,[t("code",null,d(s.ex_dot_loop),1),e[5]||(e[5]=a(" (tags is ",-1)),e[6]||(e[6]=t("code",null,'["a","b"]',-1)),e[7]||(e[7]=a(")",-1))])]),t("tr",null,[t("td",null,[t("code",I,d(s.comment),1)]),e[9]||(e[9]=t("td",null,"Comment — not rendered",-1)),t("td",null,[t("code",null,d(s.ex_comment),1)])])])])])]),t("div",D,[e[11]||(e[11]=t("i",{class:"bi bi-exclamation-triangle-fill me-2"},null,-1)),e[12]||(e[12]=t("strong",null,"Closing tags must always match the opening name exactly.",-1)),t("code",N,d(s.rows_open),1),e[13]||(e[13]=a(" closes with ",-1)),t("code",null,d(s.rows_close),1),e[14]||(e[14]=a(" — never ",-1)),t("code",null,d(s.rows_wrong),1),e[15]||(e[15]=a(". ",-1))]),t("div",O,[e[20]||(e[20]=t("div",{class:"card-header"},[t("i",{class:"bi bi-lightbulb me-2 text-warning"}),a("Key rule — your data is always "),t("code",null,"rows")],-1)),t("div",Q,[e[19]||(e[19]=t("p",{class:"mb-2"},[a("Every query returns a single top-level key "),t("code",null,"rows"),a(", which is a list of objects:")],-1)),t("pre",B,d(l.dataShape),1),t("p",F,[e[16]||(e[16]=a("Each row also receives ",-1)),t("code",null,d(s.index),1),e[17]||(e[17]=a(" (1-based position) and ",-1)),t("code",null,d(s.total),1),e[18]||(e[18]=a(" (total row count) automatically.",-1))])])])])):n("",!0),i.value==="flat-table"?(o(),r("div",H,[e[30]||(e[30]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-table me-2 text-primary"}),a("Flat Table Report")],-1)),e[31]||(e[31]=t("p",{class:"text-muted"},"The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.",-1)),t("div",V,[e[23]||(e[23]=t("div",{class:"step-label"},"1 · Unity Catalog Table",-1)),t("pre",G,d(l.flatTable_sql),1)]),t("div",Y,[e[24]||(e[24]=t("div",{class:"step-label"},"2 · Data Shape delivered to template",-1)),t("pre",W,d(l.flatTable_data),1)]),t("div",z,[e[25]||(e[25]=t("div",{class:"step-label"},"3 · Mustache Template",-1)),t("pre",K,d(l.flatTable_template),1)]),t("div",J,[e[26]||(e[26]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),e[27]||(e[27]=t("strong",null,"Null / empty check:",-1)),e[28]||(e[28]=a(" use ",-1)),t("code",null,d(s.inverted),1),e[29]||(e[29]=a(" to render content when a field is null, false, or empty — no logic needed. ",-1))])])):n("",!0),i.value==="struct"?(o(),r("div",$,[e[39]||(e[39]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces-asterisk me-2 text-primary"}),a("Struct Fields")],-1)),e[40]||(e[40]=t("p",{class:"text-muted"},[a("When a column is "),t("code",null,"STRUCT<...>"),a(", Mustache can push it as a context or access it with dot notation.")],-1)),t("div",X,[e[32]||(e[32]=t("div",{class:"step-label"},"1 · Unity Catalog Table with a STRUCT column",-1)),t("pre",Z,d(l.struct_sql),1)]),t("div",tt,[e[33]||(e[33]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",et,d(l.struct_data),1)]),t("div",at,[e[38]||(e[38]=t("div",{class:"step-label"},"3 · Template — two equivalent approaches",-1)),t("div",dt,[t("div",st,[t("div",lt,[e[35]||(e[35]=t("div",{class:"approach-label"},"Context push (recommended)",-1)),t("pre",it,d(l.struct_context),1),t("p",rt,[t("code",null,d(s.address_open),1),e[34]||(e[34]=a(" pushes the struct as context — child fields are then in scope directly.",-1))])])]),t("div",ot,[t("div",nt,[e[36]||(e[36]=t("div",{class:"approach-label"},"Dot notation",-1)),t("pre",ct,d(l.struct_dot),1),e[37]||(e[37]=t("p",{class:"small text-muted mt-2 mb-0"},"Dot notation accesses nested fields without a context push — useful for one or two fields.",-1))])])])])])):n("",!0),i.value==="array-struct"?(o(),r("div",bt,[e[52]||(e[52]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-list-nested me-2 text-primary"}),a("Array of Structs")],-1)),e[53]||(e[53]=t("p",{class:"text-muted"},[a("When a column is "),t("code",null,"ARRAY<STRUCT<...>>"),a(", iterate the outer "),t("code",null,"rows"),a(" first, then the nested array inside.")],-1)),t("div",vt,[e[41]||(e[41]=t("div",{class:"step-label"},"1 · Unity Catalog Table with ARRAY<STRUCT>",-1)),t("pre",pt,d(l.array_sql),1)]),t("div",mt,[e[42]||(e[42]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",ut,d(l.array_data),1)]),t("div",ft,[e[43]||(e[43]=t("div",{class:"step-label"},"3 · Template — nested iteration",-1)),t("pre",gt,d(l.array_template),1)]),t("div",ht,[e[44]||(e[44]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),e[45]||(e[45]=t("strong",null,"One page per order:",-1)),e[46]||(e[46]=a(" the outer ",-1)),t("code",null,d(s.rows_open),1),e[47]||(e[47]=a(" wraps a ",-1)),e[48]||(e[48]=t("code",null,".report-page",-1)),e[49]||(e[49]=a(" div, so each order gets its own page. ",-1)),t("code",null,d(s.index),1),e[50]||(e[50]=a(" and ",-1)),t("code",null,d(s.total),1),e[51]||(e[51]=a(" are available on each row. ",-1))])])):n("",!0),i.value==="chart-struct"?(o(),r("div",yt,[e[65]||(e[65]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-bar-chart me-2 text-primary"}),a("Charts from Struct Columns")],-1)),e[66]||(e[66]=t("p",{class:"text-muted"},[a("Charts read comma-separated strings from "),t("code",null,"data-labels"),a(" and "),t("code",null,"data-values"),a(" attributes. There are three ways to feed data in.")],-1)),t("div",_t,[e[56]||(e[56]=t("div",{class:"pattern-header pattern-1"},[a("Pattern 1 — Aggregate the main "),t("code",null,"rows"),a(" array (simplest)")],-1)),t("div",wt,[e[54]||(e[54]=t("p",{class:"small text-muted mb-3"},"Use when each row already represents one data point you want to plot.",-1)),t("pre",xt,d(l.chart1_template),1),e[55]||(e[55]=t("p",{class:"small text-muted mt-2 mb-0"},[a("Mustache renders the loops into: "),t("code",null,'data-labels="EMEA,APAC,AMER,"'),a(" — trailing commas are ignored by the parser.")],-1))])]),t("div",kt,[e[58]||(e[58]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — Pre-aggregated scalar columns",-1)),t("div",St,[e[57]||(e[57]=t("p",{class:"small text-muted mb-3"},"SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.",-1)),t("pre",Tt,d(l.chart2_template),1)])]),t("div",Ct,[e[64]||(e[64]=t("div",{class:"pattern-header pattern-3"},"Pattern 3 — ARRAY<STRUCT> chart column (self-contained)",-1)),t("div",At,[e[62]||(e[62]=t("p",{class:"small text-muted mb-3"},"The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.",-1)),t("div",Rt,[e[59]||(e[59]=t("div",{class:"step-label"},"SQL",-1)),t("pre",jt,d(l.chart3_sql),1)]),t("div",Et,[e[60]||(e[60]=t("div",{class:"step-label"},"Data Shape",-1)),t("pre",Lt,d(l.chart3_data),1)]),t("div",Pt,[e[61]||(e[61]=t("div",{class:"step-label"},"Template — one page per team, each with its own chart",-1)),t("pre",Mt,d(l.chart3_template),1)]),e[63]||(e[63]=t("div",{class:"alert alert-success mb-0"},[t("i",{class:"bi bi-check-circle-fill me-2"}),t("strong",null,"Why this pattern is powerful:"),a(" each team's chart is driven entirely by its own "),t("code",null,"spend_by_month"),a(" array — no global aggregation needed in the template. The SQL does the work, the template just renders it. ")],-1))])]),e[67]||(e[67]=c('<div class="card" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-table me-2" data-v-7ef7db27></i>Pattern comparison</div><div class="card-body p-0" data-v-7ef7db27><table class="table table-sm mb-0" data-v-7ef7db27><thead class="table-dark" data-v-7ef7db27><tr data-v-7ef7db27><th data-v-7ef7db27>Pattern</th><th data-v-7ef7db27>SQL complexity</th><th data-v-7ef7db27>Best for</th></tr></thead><tbody data-v-7ef7db27><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge pattern-badge-1" data-v-7ef7db27>1 — Aggregate rows</span></td><td data-v-7ef7db27>Low</td><td data-v-7ef7db27>Single summary chart across all rows</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge pattern-badge-2" data-v-7ef7db27>2 — Scalar columns</span></td><td data-v-7ef7db27>Low–Medium</td><td data-v-7ef7db27>Fixed labels, one summary row</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge pattern-badge-3" data-v-7ef7db27>3 — Struct array</span></td><td data-v-7ef7db27>Medium</td><td data-v-7ef7db27>Per-row charts with different datasets on each page</td></tr></tbody></table></div></div>',1))])):n("",!0),i.value==="conditional-styles"?(o(),r("div",Ut,[e[88]||(e[88]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-palette me-2 text-primary"}),a("Conditional Styles")],-1)),e[89]||(e[89]=t("p",{class:"text-muted"},"Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.",-1)),t("div",qt,[e[81]||(e[81]=t("div",{class:"pattern-header pattern-1"},"Pattern 1 — CSS class from value (styling only, no SQL changes)",-1)),t("div",It,[e[80]||(e[80]=t("p",{class:"small text-muted mb-3"},[a(" Interpolate the field value directly into the class name. Add a "),t("code",null,"<style>"),a(" block at the top of your template with one rule per expected value. Best for badge colours, row highlights, or any purely visual difference. ")],-1)),t("div",Dt,[e[68]||(e[68]=t("div",{class:"step-label"},"SQL — no changes needed",-1)),t("pre",Nt,d(l.conditional_sql_pattern1),1)]),t("div",Ot,[e[69]||(e[69]=t("div",{class:"step-label"},"Template",-1)),t("pre",Qt,d(l.conditional_template_pattern1),1)]),t("div",Bt,[e[70]||(e[70]=t("i",{class:"bi bi-check-circle-fill me-2"},null,-1)),e[71]||(e[71]=t("strong",null,"How it works:",-1)),e[72]||(e[72]=a()),t("code",null,d(s.cond_class_example),1),e[73]||(e[73]=a(" renders as ",-1)),e[74]||(e[74]=t("code",null,"status-approved",-1)),e[75]||(e[75]=a(", ",-1)),e[76]||(e[76]=t("code",null,"status-pending",-1)),e[77]||(e[77]=a(", or ",-1)),e[78]||(e[78]=t("code",null,"status-rejected",-1)),e[79]||(e[79]=a(". Your CSS rules match on those exact class names. ",-1))])])]),t("div",Ft,[e[87]||(e[87]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — SQL boolean flags (show/hide entire blocks)",-1)),t("div",Ht,[t("p",Vt,[e[82]||(e[82]=a(" Add computed boolean columns to your SQL query. Mustache sections (",-1)),t("code",null,d(s.section),1),e[83]||(e[83]=a(") render only when the value is truthy, giving you a full conditional block — not just a style change. ",-1))]),t("div",Gt,[e[84]||(e[84]=t("div",{class:"step-label"},"SQL — add boolean columns",-1)),t("pre",Yt,d(l.conditional_sql_pattern2),1)]),t("div",Wt,[e[85]||(e[85]=t("div",{class:"step-label"},"Template — conditional blocks",-1)),t("pre",zt,d(l.conditional_template_pattern2),1)]),e[86]||(e[86]=t("div",{class:"alert alert-info mb-0"},[t("i",{class:"bi bi-info-circle me-2"}),t("strong",null,"When to use Pattern 2:"),a(" when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers. ")],-1))])]),e[90]||(e[90]=c('<div class="card" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-table me-2" data-v-7ef7db27></i>Pattern comparison</div><div class="card-body p-0" data-v-7ef7db27><table class="table table-sm mb-0" data-v-7ef7db27><thead class="table-dark" data-v-7ef7db27><tr data-v-7ef7db27><th data-v-7ef7db27>Pattern</th><th data-v-7ef7db27>SQL change?</th><th data-v-7ef7db27>Best for</th></tr></thead><tbody data-v-7ef7db27><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge pattern-badge-1" data-v-7ef7db27>1 — CSS class from value</span></td><td data-v-7ef7db27>None</td><td data-v-7ef7db27>Badge colours, row highlights, status indicators</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge pattern-badge-2" data-v-7ef7db27>2 — SQL boolean flags</span></td><td data-v-7ef7db27>Add <code data-v-7ef7db27>field = &#39;value&#39; AS is_x</code></td><td data-v-7ef7db27>Conditional blocks, different content per status</td></tr></tbody></table></div></div>',1))])):n("",!0),i.value==="images"?(o(),r("div",Kt,[e[96]||(e[96]=c('<h4 class="section-title" data-v-7ef7db27><i class="bi bi-images me-2 text-primary" data-v-7ef7db27></i>Images in Templates</h4><p class="text-muted" data-v-7ef7db27>Upload images to the gallery and reference them in your report templates using standard HTML <code data-v-7ef7db27>&lt;img&gt;</code> tags.</p><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-lightning me-2 text-warning" data-v-7ef7db27></i>Quick start</div><div class="card-body" data-v-7ef7db27><ol class="mb-0" data-v-7ef7db27><li class="mb-2" data-v-7ef7db27>Go to <strong data-v-7ef7db27>Image Gallery</strong> (make sure you have an active project).</li><li class="mb-2" data-v-7ef7db27>Upload an image — drag &amp; drop or click <strong data-v-7ef7db27>Upload</strong>. Supported formats: JPEG, PNG, GIF, WebP, SVG (max 2 MB).</li><li class="mb-2" data-v-7ef7db27>Click the <i class="bi bi-link-45deg" data-v-7ef7db27></i> button on the image card to copy its URL.</li><li data-v-7ef7db27>Paste the URL into an <code data-v-7ef7db27>&lt;img&gt;</code> tag in your template.</li></ol></div></div>',3)),t("div",Jt,[e[95]||(e[95]=t("div",{class:"pattern-header pattern-1"},"Using images in templates",-1)),t("div",$t,[e[94]||(e[94]=t("p",{class:"small text-muted mb-3"},[a("Use the image URL directly in an "),t("code",null,"<img>"),a(" tag. You can also use just the path (without the domain) since the report renders on the same origin.")],-1)),t("div",Xt,[e[91]||(e[91]=t("div",{class:"step-label"},"Basic image",-1)),t("pre",Zt,d(l.image_basic),1)]),t("div",te,[e[92]||(e[92]=t("div",{class:"step-label"},"Logo in a report header",-1)),t("pre",ee,d(l.image_header),1)]),t("div",ae,[e[93]||(e[93]=t("div",{class:"step-label"},"Sized and styled",-1)),t("pre",de,d(l.image_styled),1)])])]),e[97]||(e[97]=c('<div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-7ef7db27></i>Limitations</div><div class="card-body" data-v-7ef7db27><table class="table table-sm mb-0" data-v-7ef7db27><thead class="table-dark" data-v-7ef7db27><tr data-v-7ef7db27><th data-v-7ef7db27>Works</th><th data-v-7ef7db27>Does not work</th></tr></thead><tbody data-v-7ef7db27><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>&lt;img src=&quot;/api/v1/images/ID/data&quot;&gt;</code></td><td data-v-7ef7db27><code data-v-7ef7db27>background-image: url(/api/v1/images/ID/data)</code></td></tr><tr data-v-7ef7db27><td data-v-7ef7db27>Standard <code data-v-7ef7db27>&lt;img&gt;</code> tags with inline styles</td><td data-v-7ef7db27>CSS <code data-v-7ef7db27>url()</code> references to gallery images (blocked by sanitizer)</td></tr></tbody></table><p class="small text-muted mt-2 mb-0" data-v-7ef7db27> The template CSS sanitizer strips non-<code data-v-7ef7db27>data:</code> URLs in stylesheets for security. Use <code data-v-7ef7db27>&lt;img&gt;</code> tags instead of CSS background images. </p></div></div><div class="card" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-info-circle me-2 text-info" data-v-7ef7db27></i>Tips</div><div class="card-body" data-v-7ef7db27><ul class="small mb-0" data-v-7ef7db27><li class="mb-2" data-v-7ef7db27>Each project can hold up to <strong data-v-7ef7db27>20 images</strong>, each up to <strong data-v-7ef7db27>2 MB</strong>.</li><li class="mb-2" data-v-7ef7db27>Images are served with a 24-hour browser cache header, so they load quickly in previews.</li><li class="mb-2" data-v-7ef7db27>Use the <strong data-v-7ef7db27>Rename</strong> button to give images descriptive names for easy identification.</li><li data-v-7ef7db27>For logos and icons, <strong data-v-7ef7db27>SVG</strong> or <strong data-v-7ef7db27>WebP</strong> formats give the best quality-to-size ratio.</li></ul></div></div>',2))])):n("",!0),i.value==="scheduling"?(o(),r("div",se,[...e[98]||(e[98]=[c('<h4 class="section-title" data-v-7ef7db27><i class="bi bi-clock-history me-2 text-primary" data-v-7ef7db27></i>Scheduling</h4><p class="text-muted" data-v-7ef7db27>Schedules automate report rendering on a recurring basis using standard cron expressions. The app&#39;s service principal executes the query and renders the template server-side — no user session is required.</p><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-lightning me-2 text-warning" data-v-7ef7db27></i>Quick start</div><div class="card-body" data-v-7ef7db27><ol class="mb-0" data-v-7ef7db27><li class="mb-2" data-v-7ef7db27>Make sure the app&#39;s service principal has <code data-v-7ef7db27>SELECT</code> privilege on every Unity Catalog table used by the report&#39;s data structure.</li><li class="mb-2" data-v-7ef7db27>Open <strong data-v-7ef7db27>Schedules</strong> from the sidebar (an active project must be selected).</li><li class="mb-2" data-v-7ef7db27>Click <strong data-v-7ef7db27>New Schedule</strong>, choose a data structure and template, set a frequency, and click <strong data-v-7ef7db27>Create Schedule</strong>.</li><li class="mb-2" data-v-7ef7db27>The schedule is registered immediately. Use the <i class="bi bi-play-fill" data-v-7ef7db27></i> button to trigger a test run without waiting for the next cron tick.</li><li data-v-7ef7db27>Switch to the <strong data-v-7ef7db27>Execution History</strong> tab and click <i class="bi bi-list-check" data-v-7ef7db27></i> on any schedule to review past runs and error messages.</li></ol></div></div><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-7ef7db27></i>Service principal requirement</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27> Scheduled executions run in the background without a user session. The app queries Databricks using the <strong data-v-7ef7db27>service principal credentials</strong> configured in the environment (<code data-v-7ef7db27>DATABRICKS_CLIENT_ID</code> / <code data-v-7ef7db27>DATABRICKS_CLIENT_SECRET</code> or <code data-v-7ef7db27>DATABRICKS_TOKEN</code>). </p><p class="small mb-0 text-danger fw-semibold" data-v-7ef7db27> If the service principal does not have <code data-v-7ef7db27>SELECT</code> on the relevant UC tables, every scheduled execution will fail with a permissions error. </p></div></div><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-calendar-week me-2" data-v-7ef7db27></i>Cron expression format</div><div class="card-body" data-v-7ef7db27><p class="small text-muted mb-3" data-v-7ef7db27>Schedules use standard 5-field cron syntax: <code data-v-7ef7db27>minute hour day month day_of_week</code>.</p><table class="table table-sm mb-3" data-v-7ef7db27><thead class="table-dark" data-v-7ef7db27><tr data-v-7ef7db27><th data-v-7ef7db27>Expression</th><th data-v-7ef7db27>Meaning</th></tr></thead><tbody data-v-7ef7db27><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>0 9 * * *</code></td><td data-v-7ef7db27>Every day at 09:00</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>0 9 * * 1-5</code></td><td data-v-7ef7db27>Weekdays (Mon–Fri) at 09:00</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>0 8 * * 1</code></td><td data-v-7ef7db27>Every Monday at 08:00</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>0 6 1 * *</code></td><td data-v-7ef7db27>1st of every month at 06:00</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>*/15 * * * *</code></td><td data-v-7ef7db27>Every 15 minutes</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><code data-v-7ef7db27>30 17 * * 5</code></td><td data-v-7ef7db27>Every Friday at 17:30</td></tr></tbody></table><p class="small text-muted mb-0" data-v-7ef7db27> The schedule builder&#39;s <strong data-v-7ef7db27>Simple</strong> mode generates a cron expression for you. Switch to <strong data-v-7ef7db27>Cron</strong> mode to enter one manually. </p></div></div><div class="card mb-4" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-list-check me-2" data-v-7ef7db27></i>Execution statuses</div><div class="card-body p-0" data-v-7ef7db27><table class="table table-sm mb-0" data-v-7ef7db27><thead class="table-dark" data-v-7ef7db27><tr data-v-7ef7db27><th data-v-7ef7db27>Status</th><th data-v-7ef7db27>Meaning</th></tr></thead><tbody data-v-7ef7db27><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge bg-primary" data-v-7ef7db27>running</span></td><td data-v-7ef7db27>The execution is in progress. The history panel auto-refreshes every 10 seconds while a run is active.</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge bg-success" data-v-7ef7db27>success</span></td><td data-v-7ef7db27>The report rendered without error.</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge bg-danger" data-v-7ef7db27>failed</span></td><td data-v-7ef7db27>The run failed — check the <strong data-v-7ef7db27>Error</strong> column for details (missing UC privilege, bad Mustache syntax, warehouse timeout, etc.).</td></tr><tr data-v-7ef7db27><td data-v-7ef7db27><span class="badge bg-secondary" data-v-7ef7db27>pending</span></td><td data-v-7ef7db27>Queued but not yet started.</td></tr></tbody></table></div></div><div class="row g-4 mb-4" data-v-7ef7db27><div class="col-md-6" data-v-7ef7db27><div class="card h-100" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-pencil me-2 text-primary" data-v-7ef7db27></i>Editing a schedule</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27>Click the <i class="bi bi-pencil" data-v-7ef7db27></i> button to change a schedule&#39;s <strong data-v-7ef7db27>name</strong>, <strong data-v-7ef7db27>cron expression</strong>, or <strong data-v-7ef7db27>active</strong> status.</p><p class="small mb-2" data-v-7ef7db27>The linked structure and template cannot be changed after creation — delete and recreate the schedule if you need a different template.</p><p class="small mb-0 text-muted" data-v-7ef7db27>Saving a cron change re-registers the APScheduler job immediately.</p></div></div></div><div class="col-md-6" data-v-7ef7db27><div class="card h-100" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-toggle-on me-2 text-success" data-v-7ef7db27></i>Active vs Inactive</div><div class="card-body" data-v-7ef7db27><p class="small mb-2" data-v-7ef7db27>Inactive schedules are not registered with the scheduler — they will not fire automatically.</p><p class="small mb-2" data-v-7ef7db27>Toggling a schedule back to <strong data-v-7ef7db27>Active</strong> immediately re-registers the cron job with no further action required.</p><p class="small mb-0 text-muted" data-v-7ef7db27>The manual trigger button (<i class="bi bi-play-fill" data-v-7ef7db27></i>) works regardless of the active flag.</p></div></div></div></div><div class="card" data-v-7ef7db27><div class="card-header" data-v-7ef7db27><i class="bi bi-info-circle me-2 text-info" data-v-7ef7db27></i>Tips &amp; limitations</div><div class="card-body" data-v-7ef7db27><ul class="small mb-0" data-v-7ef7db27><li class="mb-2" data-v-7ef7db27>Schedules are scoped to a project — select the project in the sidebar before navigating to the Schedules page.</li><li class="mb-2" data-v-7ef7db27>The scheduler runs in the same process as the FastAPI back-end. If the app restarts, all active schedules are automatically re-registered from the database on startup.</li><li class="mb-2" data-v-7ef7db27>Execution history is paginated to the last 50 runs by default. Use the offset/limit query parameters on the API if you need older entries.</li><li class="mb-2" data-v-7ef7db27>Only the project owner and shared members can create or modify schedules. The <code data-v-7ef7db27>check_schedule_project_access</code> guard applies the same access + lock rules as structures and templates.</li><li data-v-7ef7db27>Scheduled renders use a <strong data-v-7ef7db27>10,000 row limit</strong> on the SQL query — the same as a full PDF export.</li></ul></div></div>',8)])])):n("",!0)])])]))}}),ce=h(le,[["__scopeId","data-v-7ef7db27"]]);export{ce as default};
