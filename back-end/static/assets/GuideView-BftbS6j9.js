import{d as u,c as i,a as t,b as e,F as b,t as g,e as p,x as n,w as s,C as h,o as r,v,_ as y}from"./index-DQn6lqpe.js";const _={class:"guide-view"},w={class:"row g-4"},f={class:"col-md-3"},x={class:"card sticky-top",style:{top:"calc(var(--pr-navbar-height) + 1rem)"}},k={class:"card-body p-2"},S=["onClick"],C={class:"col-md-9"},T={key:0},R={key:1},A={class:"card mb-4"},j={class:"card-body p-0"},L={class:"table table-sm mb-0"},P={class:"syntax-tag"},M={class:"syntax-tag"},E={class:"syntax-tag"},U={class:"syntax-tag"},q={class:"syntax-tag"},D={class:"syntax-tag"},I={class:"alert alert-warning"},N={class:"ms-1"},O={class:"card"},V={class:"card-body"},H={class:"code-block"},Q={class:"mb-0 small text-muted mt-2"},B={key:2},G={class:"pattern-step"},Y={class:"code-block"},F={class:"pattern-step"},W={class:"code-block"},z={class:"pattern-step"},K={class:"code-block"},J={class:"alert alert-info"},$={key:3},X={class:"pattern-step"},Z={class:"code-block"},tt={class:"pattern-step"},at={class:"code-block"},et={class:"pattern-step"},st={class:"row g-3"},dt={class:"col-md-6"},lt={class:"approach-card"},ot={class:"code-block"},it={class:"small text-muted mt-2 mb-0"},rt={class:"col-md-6"},nt={class:"approach-card"},ct={class:"code-block"},pt={key:4},vt={class:"pattern-step"},mt={class:"code-block"},ut={class:"pattern-step"},bt={class:"code-block"},gt={class:"pattern-step"},ht={class:"code-block"},yt={class:"alert alert-info"},_t={key:5},wt={class:"pattern-card mb-4"},ft={class:"card-body"},xt={class:"code-block"},kt={class:"pattern-card mb-4"},St={class:"card-body"},Ct={class:"code-block"},Tt={class:"pattern-card mb-4"},Rt={class:"card-body"},At={class:"pattern-step"},jt={class:"code-block"},Lt={class:"pattern-step"},Pt={class:"code-block"},Mt={class:"pattern-step"},Et={class:"code-block"},Ut={key:6},qt={class:"pattern-card mb-4"},Dt={class:"card-body"},It={class:"pattern-step"},Nt={class:"code-block"},Ot={class:"pattern-step"},Vt={class:"code-block"},Ht={class:"alert alert-success mb-0"},Qt={class:"pattern-card mb-4"},Bt={class:"card-body"},Gt={class:"small text-muted mb-3"},Yt={class:"pattern-step"},Ft={class:"code-block"},Wt={class:"pattern-step"},zt={class:"code-block"},Kt={key:7},Jt={class:"pattern-card mb-4"},$t={class:"card-body"},Xt={class:"pattern-step"},Zt={class:"code-block"},ta={class:"pattern-step"},aa={class:"code-block"},ea={class:"pattern-step"},sa={class:"code-block"},da=u({__name:"GuideView",setup(la){const o=h("projects"),m=[{id:"projects",label:"Projects",icon:"bi-folder2-open"},{id:"mustache",label:"Mustache Syntax",icon:"bi-braces"},{id:"flat-table",label:"Flat Table",icon:"bi-table"},{id:"struct",label:"Struct Fields",icon:"bi-braces-asterisk"},{id:"array-struct",label:"Array of Structs",icon:"bi-list-nested"},{id:"chart-struct",label:"Charts from Structs",icon:"bi-bar-chart"},{id:"conditional-styles",label:"Conditional Styles",icon:"bi-palette"},{id:"images",label:"Images",icon:"bi-images"}],d={variable:"{{field}}",triple:"{{{field}}}",section:"{{#section}}...{{/section}}",inverted:"{{^section}}...{{/section}}",dot:"{{.}}",comment:"{{! comment }}",ex_field:"{{cluster_name}}",ex_dot_loop:"{{#tags}}{{.}}{{/tags}}",ex_comment:"{{! TODO: add chart }}",rows_open:"{{#rows}}",rows_close:"{{/rows}}",rows_wrong:"{{/#}}",delete_check:"{{^delete_time}}Active{{/delete_time}}",index:"{{_index}}",total:"{{_total}}",address_open:"{{#address}}",cond_class_example:"status-{{approval_status}}"},l={dataShape:`{
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
{{/rows}}`};return(oa,a)=>(r(),i("div",_,[a[98]||(a[98]=t("div",{class:"guide-header mb-4"},[t("h2",{class:"mb-1"},[t("i",{class:"bi bi-book text-primary me-2"}),e(" Template Guide ")]),t("p",{class:"text-muted mb-0"}," How to structure your data and write Mustache templates for reports ")],-1)),t("div",w,[t("div",f,[t("div",x,[t("div",k,[(r(),i(b,null,g(m,c=>t("button",{key:c.id,class:v(["guide-nav-btn",{active:o.value===c.id}]),onClick:ia=>o.value=c.id},[t("i",{class:v(["bi",c.icon,"me-2"])},null,2),e(" "+s(c.label),1)],10,S)),64))])])]),t("div",C,[o.value==="projects"?(r(),i("div",T,[...a[0]||(a[0]=[p('<h4 class="section-title" data-v-6e799a52><i class="bi bi-folder2-open me-2 text-primary" data-v-6e799a52></i>Projects</h4><p class="text-muted" data-v-6e799a52>Projects group related data structures and templates together, making it easy to organise, share, and lock your work.</p><div class="card mb-4" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-lightning me-2 text-warning" data-v-6e799a52></i>Getting started</div><div class="card-body" data-v-6e799a52><ol class="mb-0" data-v-6e799a52><li class="mb-2" data-v-6e799a52>Navigate to <strong data-v-6e799a52>Projects</strong> and click <strong data-v-6e799a52>New Project</strong>.</li><li class="mb-2" data-v-6e799a52>Give it a name (e.g. &quot;Q1 Sales Reports&quot;) and click <strong data-v-6e799a52>Create</strong>.</li><li class="mb-2" data-v-6e799a52>Click <strong data-v-6e799a52>Open</strong> to set it as your active project — you&#39;ll see a banner in the sidebar.</li><li class="mb-2" data-v-6e799a52>Now go to <strong data-v-6e799a52>Data Structures</strong> — any structures you create will automatically belong to this project.</li><li data-v-6e799a52>Create templates linked to those structures and preview them as usual.</li></ol></div></div><div class="row g-4 mb-4" data-v-6e799a52><div class="col-md-6" data-v-6e799a52><div class="card h-100" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-diagram-3 me-2 text-primary" data-v-6e799a52></i>How structures are linked</div><div class="card-body" data-v-6e799a52><p class="small mb-2" data-v-6e799a52>When a project is active, new structures are automatically associated with it via a <code data-v-6e799a52>project_id</code> field.</p><p class="small mb-2" data-v-6e799a52>The Data Structures and Template Editor pages filter their lists to show only items belonging to the active project.</p><p class="small mb-0 text-muted" data-v-6e799a52>Clear the project filter (click the <i class="bi bi-x-lg" data-v-6e799a52></i> in the sidebar banner) to see all structures across all projects.</p></div></div></div><div class="col-md-6" data-v-6e799a52><div class="card h-100" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-file-code me-2 text-success" data-v-6e799a52></i>How templates are linked</div><div class="card-body" data-v-6e799a52><p class="small mb-2" data-v-6e799a52>Templates don&#39;t have a direct project link — they&#39;re associated through their <strong data-v-6e799a52>structure</strong>.</p><p class="small mb-0" data-v-6e799a52>When filtering by project, the app shows templates whose linked structure belongs to the active project.</p></div></div></div></div><div class="card mb-4" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-lock me-2 text-warning" data-v-6e799a52></i>Locking</div><div class="card-body" data-v-6e799a52><p class="small mb-2" data-v-6e799a52>Only the project <strong data-v-6e799a52>owner</strong> can lock or unlock a project.</p><p class="small mb-2" data-v-6e799a52>When a project is <strong data-v-6e799a52>locked</strong>, all create, update, and delete operations on its structures and templates are blocked with a <code data-v-6e799a52>423 Locked</code> response.</p><p class="small mb-0 text-muted" data-v-6e799a52>This is useful when a report set is finalised and you want to prevent accidental edits.</p></div></div><div class="card mb-4" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-people me-2 text-info" data-v-6e799a52></i>Sharing</div><div class="card-body" data-v-6e799a52><p class="small mb-2" data-v-6e799a52>Share a project with colleagues by entering their email address on the project detail panel.</p><p class="small mb-2" data-v-6e799a52>Shared users can <strong data-v-6e799a52>view</strong> and <strong data-v-6e799a52>edit</strong> structures and templates in the project (unless it&#39;s locked).</p><p class="small mb-2" data-v-6e799a52>Only the project <strong data-v-6e799a52>owner</strong> can:</p><ul class="small mb-0" data-v-6e799a52><li data-v-6e799a52>Lock / unlock the project</li><li data-v-6e799a52>Add or remove shares</li><li data-v-6e799a52>Delete the project</li></ul></div></div><div class="card" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-table me-2" data-v-6e799a52></i>Permission summary</div><div class="card-body p-0" data-v-6e799a52><table class="table table-sm mb-0" data-v-6e799a52><thead class="table-dark" data-v-6e799a52><tr data-v-6e799a52><th data-v-6e799a52>Action</th><th data-v-6e799a52>Owner</th><th data-v-6e799a52>Shared user</th></tr></thead><tbody data-v-6e799a52><tr data-v-6e799a52><td data-v-6e799a52>View structures &amp; templates</td><td class="text-success" data-v-6e799a52>Yes</td><td class="text-success" data-v-6e799a52>Yes</td></tr><tr data-v-6e799a52><td data-v-6e799a52>Create / edit / delete structures &amp; templates</td><td class="text-success" data-v-6e799a52>Yes (if unlocked)</td><td class="text-success" data-v-6e799a52>Yes (if unlocked)</td></tr><tr data-v-6e799a52><td data-v-6e799a52>Lock / unlock project</td><td class="text-success" data-v-6e799a52>Yes</td><td class="text-danger" data-v-6e799a52>No</td></tr><tr data-v-6e799a52><td data-v-6e799a52>Share / unshare project</td><td class="text-success" data-v-6e799a52>Yes</td><td class="text-danger" data-v-6e799a52>No</td></tr><tr data-v-6e799a52><td data-v-6e799a52>Delete project</td><td class="text-success" data-v-6e799a52>Yes</td><td class="text-danger" data-v-6e799a52>No</td></tr><tr data-v-6e799a52><td data-v-6e799a52>Rename project</td><td class="text-success" data-v-6e799a52>Yes</td><td class="text-danger" data-v-6e799a52>No</td></tr></tbody></table></div></div>',7)])])):n("",!0),o.value==="mustache"?(r(),i("div",R,[a[21]||(a[21]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces me-2 text-primary"}),e("Mustache Syntax Reference")],-1)),a[22]||(a[22]=t("p",{class:"text-muted"},[e("Mustache is a logic-less templating language. All data comes from the "),t("code",null,"rows"),e(" array returned by your SQL query.")],-1)),t("div",A,[t("div",j,[t("table",L,[a[10]||(a[10]=t("thead",{class:"table-dark"},[t("tr",null,[t("th",null,"Syntax"),t("th",null,"Purpose"),t("th",null,"Example")])],-1)),t("tbody",null,[t("tr",null,[t("td",null,[t("code",P,s(d.variable),1)]),a[1]||(a[1]=t("td",null,"Render a value (HTML-escaped)",-1)),t("td",null,[t("code",null,s(d.ex_field),1)])]),t("tr",null,[t("td",null,[t("code",M,s(d.triple),1)]),a[2]||(a[2]=t("td",null,"Render raw HTML (unescaped)",-1)),t("td",null,[t("code",null,s(d.triple),1)])]),t("tr",null,[t("td",null,[t("code",E,s(d.section),1)]),a[3]||(a[3]=t("td",null,[e("Iterate array "),t("strong",null,"or"),e(" render if truthy")],-1)),t("td",null,[t("code",null,s(d.rows_open)+"..."+s(d.rows_close),1)])]),t("tr",null,[t("td",null,[t("code",U,s(d.inverted),1)]),a[4]||(a[4]=t("td",null,"Render if falsy or empty",-1)),t("td",null,[t("code",null,s(d.delete_check),1)])]),t("tr",null,[t("td",null,[t("code",q,s(d.dot),1)]),a[8]||(a[8]=t("td",null,[e("Current item in a "),t("em",null,"scalar"),e(" list only")],-1)),t("td",null,[t("code",null,s(d.ex_dot_loop),1),a[5]||(a[5]=e(" (tags is ",-1)),a[6]||(a[6]=t("code",null,'["a","b"]',-1)),a[7]||(a[7]=e(")",-1))])]),t("tr",null,[t("td",null,[t("code",D,s(d.comment),1)]),a[9]||(a[9]=t("td",null,"Comment — not rendered",-1)),t("td",null,[t("code",null,s(d.ex_comment),1)])])])])])]),t("div",I,[a[11]||(a[11]=t("i",{class:"bi bi-exclamation-triangle-fill me-2"},null,-1)),a[12]||(a[12]=t("strong",null,"Closing tags must always match the opening name exactly.",-1)),t("code",N,s(d.rows_open),1),a[13]||(a[13]=e(" closes with ",-1)),t("code",null,s(d.rows_close),1),a[14]||(a[14]=e(" — never ",-1)),t("code",null,s(d.rows_wrong),1),a[15]||(a[15]=e(". ",-1))]),t("div",O,[a[20]||(a[20]=t("div",{class:"card-header"},[t("i",{class:"bi bi-lightbulb me-2 text-warning"}),e("Key rule — your data is always "),t("code",null,"rows")],-1)),t("div",V,[a[19]||(a[19]=t("p",{class:"mb-2"},[e("Every query returns a single top-level key "),t("code",null,"rows"),e(", which is a list of objects:")],-1)),t("pre",H,s(l.dataShape),1),t("p",Q,[a[16]||(a[16]=e("Each row also receives ",-1)),t("code",null,s(d.index),1),a[17]||(a[17]=e(" (1-based position) and ",-1)),t("code",null,s(d.total),1),a[18]||(a[18]=e(" (total row count) automatically.",-1))])])])])):n("",!0),o.value==="flat-table"?(r(),i("div",B,[a[30]||(a[30]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-table me-2 text-primary"}),e("Flat Table Report")],-1)),a[31]||(a[31]=t("p",{class:"text-muted"},"The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.",-1)),t("div",G,[a[23]||(a[23]=t("div",{class:"step-label"},"1 · Unity Catalog Table",-1)),t("pre",Y,s(l.flatTable_sql),1)]),t("div",F,[a[24]||(a[24]=t("div",{class:"step-label"},"2 · Data Shape delivered to template",-1)),t("pre",W,s(l.flatTable_data),1)]),t("div",z,[a[25]||(a[25]=t("div",{class:"step-label"},"3 · Mustache Template",-1)),t("pre",K,s(l.flatTable_template),1)]),t("div",J,[a[26]||(a[26]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),a[27]||(a[27]=t("strong",null,"Null / empty check:",-1)),a[28]||(a[28]=e(" use ",-1)),t("code",null,s(d.inverted),1),a[29]||(a[29]=e(" to render content when a field is null, false, or empty — no logic needed. ",-1))])])):n("",!0),o.value==="struct"?(r(),i("div",$,[a[39]||(a[39]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces-asterisk me-2 text-primary"}),e("Struct Fields")],-1)),a[40]||(a[40]=t("p",{class:"text-muted"},[e("When a column is "),t("code",null,"STRUCT<...>"),e(", Mustache can push it as a context or access it with dot notation.")],-1)),t("div",X,[a[32]||(a[32]=t("div",{class:"step-label"},"1 · Unity Catalog Table with a STRUCT column",-1)),t("pre",Z,s(l.struct_sql),1)]),t("div",tt,[a[33]||(a[33]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",at,s(l.struct_data),1)]),t("div",et,[a[38]||(a[38]=t("div",{class:"step-label"},"3 · Template — two equivalent approaches",-1)),t("div",st,[t("div",dt,[t("div",lt,[a[35]||(a[35]=t("div",{class:"approach-label"},"Context push (recommended)",-1)),t("pre",ot,s(l.struct_context),1),t("p",it,[t("code",null,s(d.address_open),1),a[34]||(a[34]=e(" pushes the struct as context — child fields are then in scope directly.",-1))])])]),t("div",rt,[t("div",nt,[a[36]||(a[36]=t("div",{class:"approach-label"},"Dot notation",-1)),t("pre",ct,s(l.struct_dot),1),a[37]||(a[37]=t("p",{class:"small text-muted mt-2 mb-0"},"Dot notation accesses nested fields without a context push — useful for one or two fields.",-1))])])])])])):n("",!0),o.value==="array-struct"?(r(),i("div",pt,[a[52]||(a[52]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-list-nested me-2 text-primary"}),e("Array of Structs")],-1)),a[53]||(a[53]=t("p",{class:"text-muted"},[e("When a column is "),t("code",null,"ARRAY<STRUCT<...>>"),e(", iterate the outer "),t("code",null,"rows"),e(" first, then the nested array inside.")],-1)),t("div",vt,[a[41]||(a[41]=t("div",{class:"step-label"},"1 · Unity Catalog Table with ARRAY<STRUCT>",-1)),t("pre",mt,s(l.array_sql),1)]),t("div",ut,[a[42]||(a[42]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",bt,s(l.array_data),1)]),t("div",gt,[a[43]||(a[43]=t("div",{class:"step-label"},"3 · Template — nested iteration",-1)),t("pre",ht,s(l.array_template),1)]),t("div",yt,[a[44]||(a[44]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),a[45]||(a[45]=t("strong",null,"One page per order:",-1)),a[46]||(a[46]=e(" the outer ",-1)),t("code",null,s(d.rows_open),1),a[47]||(a[47]=e(" wraps a ",-1)),a[48]||(a[48]=t("code",null,".report-page",-1)),a[49]||(a[49]=e(" div, so each order gets its own page. ",-1)),t("code",null,s(d.index),1),a[50]||(a[50]=e(" and ",-1)),t("code",null,s(d.total),1),a[51]||(a[51]=e(" are available on each row. ",-1))])])):n("",!0),o.value==="chart-struct"?(r(),i("div",_t,[a[65]||(a[65]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-bar-chart me-2 text-primary"}),e("Charts from Struct Columns")],-1)),a[66]||(a[66]=t("p",{class:"text-muted"},[e("Charts read comma-separated strings from "),t("code",null,"data-labels"),e(" and "),t("code",null,"data-values"),e(" attributes. There are three ways to feed data in.")],-1)),t("div",wt,[a[56]||(a[56]=t("div",{class:"pattern-header pattern-1"},[e("Pattern 1 — Aggregate the main "),t("code",null,"rows"),e(" array (simplest)")],-1)),t("div",ft,[a[54]||(a[54]=t("p",{class:"small text-muted mb-3"},"Use when each row already represents one data point you want to plot.",-1)),t("pre",xt,s(l.chart1_template),1),a[55]||(a[55]=t("p",{class:"small text-muted mt-2 mb-0"},[e("Mustache renders the loops into: "),t("code",null,'data-labels="EMEA,APAC,AMER,"'),e(" — trailing commas are ignored by the parser.")],-1))])]),t("div",kt,[a[58]||(a[58]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — Pre-aggregated scalar columns",-1)),t("div",St,[a[57]||(a[57]=t("p",{class:"small text-muted mb-3"},"SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.",-1)),t("pre",Ct,s(l.chart2_template),1)])]),t("div",Tt,[a[64]||(a[64]=t("div",{class:"pattern-header pattern-3"},"Pattern 3 — ARRAY<STRUCT> chart column (self-contained)",-1)),t("div",Rt,[a[62]||(a[62]=t("p",{class:"small text-muted mb-3"},"The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.",-1)),t("div",At,[a[59]||(a[59]=t("div",{class:"step-label"},"SQL",-1)),t("pre",jt,s(l.chart3_sql),1)]),t("div",Lt,[a[60]||(a[60]=t("div",{class:"step-label"},"Data Shape",-1)),t("pre",Pt,s(l.chart3_data),1)]),t("div",Mt,[a[61]||(a[61]=t("div",{class:"step-label"},"Template — one page per team, each with its own chart",-1)),t("pre",Et,s(l.chart3_template),1)]),a[63]||(a[63]=t("div",{class:"alert alert-success mb-0"},[t("i",{class:"bi bi-check-circle-fill me-2"}),t("strong",null,"Why this pattern is powerful:"),e(" each team's chart is driven entirely by its own "),t("code",null,"spend_by_month"),e(" array — no global aggregation needed in the template. The SQL does the work, the template just renders it. ")],-1))])]),a[67]||(a[67]=p('<div class="card" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-table me-2" data-v-6e799a52></i>Pattern comparison</div><div class="card-body p-0" data-v-6e799a52><table class="table table-sm mb-0" data-v-6e799a52><thead class="table-dark" data-v-6e799a52><tr data-v-6e799a52><th data-v-6e799a52>Pattern</th><th data-v-6e799a52>SQL complexity</th><th data-v-6e799a52>Best for</th></tr></thead><tbody data-v-6e799a52><tr data-v-6e799a52><td data-v-6e799a52><span class="badge pattern-badge-1" data-v-6e799a52>1 — Aggregate rows</span></td><td data-v-6e799a52>Low</td><td data-v-6e799a52>Single summary chart across all rows</td></tr><tr data-v-6e799a52><td data-v-6e799a52><span class="badge pattern-badge-2" data-v-6e799a52>2 — Scalar columns</span></td><td data-v-6e799a52>Low–Medium</td><td data-v-6e799a52>Fixed labels, one summary row</td></tr><tr data-v-6e799a52><td data-v-6e799a52><span class="badge pattern-badge-3" data-v-6e799a52>3 — Struct array</span></td><td data-v-6e799a52>Medium</td><td data-v-6e799a52>Per-row charts with different datasets on each page</td></tr></tbody></table></div></div>',1))])):n("",!0),o.value==="conditional-styles"?(r(),i("div",Ut,[a[88]||(a[88]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-palette me-2 text-primary"}),e("Conditional Styles")],-1)),a[89]||(a[89]=t("p",{class:"text-muted"},"Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.",-1)),t("div",qt,[a[81]||(a[81]=t("div",{class:"pattern-header pattern-1"},"Pattern 1 — CSS class from value (styling only, no SQL changes)",-1)),t("div",Dt,[a[80]||(a[80]=t("p",{class:"small text-muted mb-3"},[e(" Interpolate the field value directly into the class name. Add a "),t("code",null,"<style>"),e(" block at the top of your template with one rule per expected value. Best for badge colours, row highlights, or any purely visual difference. ")],-1)),t("div",It,[a[68]||(a[68]=t("div",{class:"step-label"},"SQL — no changes needed",-1)),t("pre",Nt,s(l.conditional_sql_pattern1),1)]),t("div",Ot,[a[69]||(a[69]=t("div",{class:"step-label"},"Template",-1)),t("pre",Vt,s(l.conditional_template_pattern1),1)]),t("div",Ht,[a[70]||(a[70]=t("i",{class:"bi bi-check-circle-fill me-2"},null,-1)),a[71]||(a[71]=t("strong",null,"How it works:",-1)),a[72]||(a[72]=e()),t("code",null,s(d.cond_class_example),1),a[73]||(a[73]=e(" renders as ",-1)),a[74]||(a[74]=t("code",null,"status-approved",-1)),a[75]||(a[75]=e(", ",-1)),a[76]||(a[76]=t("code",null,"status-pending",-1)),a[77]||(a[77]=e(", or ",-1)),a[78]||(a[78]=t("code",null,"status-rejected",-1)),a[79]||(a[79]=e(". Your CSS rules match on those exact class names. ",-1))])])]),t("div",Qt,[a[87]||(a[87]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — SQL boolean flags (show/hide entire blocks)",-1)),t("div",Bt,[t("p",Gt,[a[82]||(a[82]=e(" Add computed boolean columns to your SQL query. Mustache sections (",-1)),t("code",null,s(d.section),1),a[83]||(a[83]=e(") render only when the value is truthy, giving you a full conditional block — not just a style change. ",-1))]),t("div",Yt,[a[84]||(a[84]=t("div",{class:"step-label"},"SQL — add boolean columns",-1)),t("pre",Ft,s(l.conditional_sql_pattern2),1)]),t("div",Wt,[a[85]||(a[85]=t("div",{class:"step-label"},"Template — conditional blocks",-1)),t("pre",zt,s(l.conditional_template_pattern2),1)]),a[86]||(a[86]=t("div",{class:"alert alert-info mb-0"},[t("i",{class:"bi bi-info-circle me-2"}),t("strong",null,"When to use Pattern 2:"),e(" when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers. ")],-1))])]),a[90]||(a[90]=p('<div class="card" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-table me-2" data-v-6e799a52></i>Pattern comparison</div><div class="card-body p-0" data-v-6e799a52><table class="table table-sm mb-0" data-v-6e799a52><thead class="table-dark" data-v-6e799a52><tr data-v-6e799a52><th data-v-6e799a52>Pattern</th><th data-v-6e799a52>SQL change?</th><th data-v-6e799a52>Best for</th></tr></thead><tbody data-v-6e799a52><tr data-v-6e799a52><td data-v-6e799a52><span class="badge pattern-badge-1" data-v-6e799a52>1 — CSS class from value</span></td><td data-v-6e799a52>None</td><td data-v-6e799a52>Badge colours, row highlights, status indicators</td></tr><tr data-v-6e799a52><td data-v-6e799a52><span class="badge pattern-badge-2" data-v-6e799a52>2 — SQL boolean flags</span></td><td data-v-6e799a52>Add <code data-v-6e799a52>field = &#39;value&#39; AS is_x</code></td><td data-v-6e799a52>Conditional blocks, different content per status</td></tr></tbody></table></div></div>',1))])):n("",!0),o.value==="images"?(r(),i("div",Kt,[a[96]||(a[96]=p('<h4 class="section-title" data-v-6e799a52><i class="bi bi-images me-2 text-primary" data-v-6e799a52></i>Images in Templates</h4><p class="text-muted" data-v-6e799a52>Upload images to the gallery and reference them in your report templates using standard HTML <code data-v-6e799a52>&lt;img&gt;</code> tags.</p><div class="card mb-4" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-lightning me-2 text-warning" data-v-6e799a52></i>Quick start</div><div class="card-body" data-v-6e799a52><ol class="mb-0" data-v-6e799a52><li class="mb-2" data-v-6e799a52>Go to <strong data-v-6e799a52>Image Gallery</strong> (make sure you have an active project).</li><li class="mb-2" data-v-6e799a52>Upload an image — drag &amp; drop or click <strong data-v-6e799a52>Upload</strong>. Supported formats: JPEG, PNG, GIF, WebP, SVG (max 2 MB).</li><li class="mb-2" data-v-6e799a52>Click the <i class="bi bi-link-45deg" data-v-6e799a52></i> button on the image card to copy its URL.</li><li data-v-6e799a52>Paste the URL into an <code data-v-6e799a52>&lt;img&gt;</code> tag in your template.</li></ol></div></div>',3)),t("div",Jt,[a[95]||(a[95]=t("div",{class:"pattern-header pattern-1"},"Using images in templates",-1)),t("div",$t,[a[94]||(a[94]=t("p",{class:"small text-muted mb-3"},[e("Use the image URL directly in an "),t("code",null,"<img>"),e(" tag. You can also use just the path (without the domain) since the report renders on the same origin.")],-1)),t("div",Xt,[a[91]||(a[91]=t("div",{class:"step-label"},"Basic image",-1)),t("pre",Zt,s(l.image_basic),1)]),t("div",ta,[a[92]||(a[92]=t("div",{class:"step-label"},"Logo in a report header",-1)),t("pre",aa,s(l.image_header),1)]),t("div",ea,[a[93]||(a[93]=t("div",{class:"step-label"},"Sized and styled",-1)),t("pre",sa,s(l.image_styled),1)])])]),a[97]||(a[97]=p('<div class="card mb-4" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-6e799a52></i>Limitations</div><div class="card-body" data-v-6e799a52><table class="table table-sm mb-0" data-v-6e799a52><thead class="table-dark" data-v-6e799a52><tr data-v-6e799a52><th data-v-6e799a52>Works</th><th data-v-6e799a52>Does not work</th></tr></thead><tbody data-v-6e799a52><tr data-v-6e799a52><td data-v-6e799a52><code data-v-6e799a52>&lt;img src=&quot;/api/v1/images/ID/data&quot;&gt;</code></td><td data-v-6e799a52><code data-v-6e799a52>background-image: url(/api/v1/images/ID/data)</code></td></tr><tr data-v-6e799a52><td data-v-6e799a52>Standard <code data-v-6e799a52>&lt;img&gt;</code> tags with inline styles</td><td data-v-6e799a52>CSS <code data-v-6e799a52>url()</code> references to gallery images (blocked by sanitizer)</td></tr></tbody></table><p class="small text-muted mt-2 mb-0" data-v-6e799a52> The template CSS sanitizer strips non-<code data-v-6e799a52>data:</code> URLs in stylesheets for security. Use <code data-v-6e799a52>&lt;img&gt;</code> tags instead of CSS background images. </p></div></div><div class="card" data-v-6e799a52><div class="card-header" data-v-6e799a52><i class="bi bi-info-circle me-2 text-info" data-v-6e799a52></i>Tips</div><div class="card-body" data-v-6e799a52><ul class="small mb-0" data-v-6e799a52><li class="mb-2" data-v-6e799a52>Each project can hold up to <strong data-v-6e799a52>20 images</strong>, each up to <strong data-v-6e799a52>2 MB</strong>.</li><li class="mb-2" data-v-6e799a52>Images are served with a 24-hour browser cache header, so they load quickly in previews.</li><li class="mb-2" data-v-6e799a52>Use the <strong data-v-6e799a52>Rename</strong> button to give images descriptive names for easy identification.</li><li data-v-6e799a52>For logos and icons, <strong data-v-6e799a52>SVG</strong> or <strong data-v-6e799a52>WebP</strong> formats give the best quality-to-size ratio.</li></ul></div></div>',2))])):n("",!0)])])]))}}),na=y(da,[["__scopeId","data-v-6e799a52"]]);export{na as default};
