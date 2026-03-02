import{d as v,c as r,a as t,b as s,F as b,r as g,t as a,q as n,e as p,y,o as i,z as u,_}from"./index-_s3yZ24f.js";const f={class:"guide-view"},h={class:"row g-4"},w={class:"col-md-3"},x={class:"card sticky-top",style:{top:"calc(var(--pr-navbar-height) + 1rem)"}},S={class:"card-body p-2"},k=["onClick"],A={class:"col-md-9"},C={key:0},T={class:"card mb-4"},R={class:"card-body p-0"},L={class:"table table-sm mb-0"},M={class:"syntax-tag"},E={class:"syntax-tag"},P={class:"syntax-tag"},q={class:"syntax-tag"},U={class:"syntax-tag"},Q={class:"syntax-tag"},V={class:"alert alert-warning"},H={class:"ms-1"},O={class:"card"},j={class:"card-body"},B={class:"code-block"},F={class:"mb-0 small text-muted mt-2"},N={key:1},D={class:"pattern-step"},I={class:"code-block"},Y={class:"pattern-step"},W={class:"code-block"},z={class:"pattern-step"},G={class:"code-block"},K={class:"alert alert-info"},J={key:2},$={class:"pattern-step"},X={class:"code-block"},Z={class:"pattern-step"},tt={class:"code-block"},et={class:"pattern-step"},st={class:"row g-3"},at={class:"col-md-6"},lt={class:"approach-card"},dt={class:"code-block"},ot={class:"small text-muted mt-2 mb-0"},rt={class:"col-md-6"},it={class:"approach-card"},nt={class:"code-block"},ct={key:3},pt={class:"pattern-step"},ut={class:"code-block"},mt={class:"pattern-step"},vt={class:"code-block"},bt={class:"pattern-step"},gt={class:"code-block"},yt={class:"alert alert-info"},_t={key:4},ft={class:"pattern-card mb-4"},ht={class:"card-body"},wt={class:"code-block"},xt={class:"pattern-card mb-4"},St={class:"card-body"},kt={class:"code-block"},At={class:"pattern-card mb-4"},Ct={class:"card-body"},Tt={class:"pattern-step"},Rt={class:"code-block"},Lt={class:"pattern-step"},Mt={class:"code-block"},Et={class:"pattern-step"},Pt={class:"code-block"},qt={key:5},Ut={class:"pattern-card mb-4"},Qt={class:"card-body"},Vt={class:"pattern-step"},Ht={class:"code-block"},Ot={class:"pattern-step"},jt={class:"code-block"},Bt={class:"alert alert-success mb-0"},Ft={class:"pattern-card mb-4"},Nt={class:"card-body"},Dt={class:"small text-muted mb-3"},It={class:"pattern-step"},Yt={class:"code-block"},Wt={class:"pattern-step"},zt={class:"code-block"},Gt=v({__name:"GuideView",setup(Kt){const o=y("mustache"),m=[{id:"mustache",label:"Mustache Syntax",icon:"bi-braces"},{id:"flat-table",label:"Flat Table",icon:"bi-table"},{id:"struct",label:"Struct Fields",icon:"bi-braces-asterisk"},{id:"array-struct",label:"Array of Structs",icon:"bi-list-nested"},{id:"chart-struct",label:"Charts from Structs",icon:"bi-bar-chart"},{id:"conditional-styles",label:"Conditional Styles",icon:"bi-palette"}],l={variable:"{{field}}",triple:"{{{field}}}",section:"{{#section}}...{{/section}}",inverted:"{{^section}}...{{/section}}",dot:"{{.}}",comment:"{{! comment }}",ex_field:"{{cluster_name}}",ex_dot_loop:"{{#tags}}{{.}}{{/tags}}",ex_comment:"{{! TODO: add chart }}",rows_open:"{{#rows}}",rows_close:"{{/rows}}",rows_wrong:"{{/#}}",delete_check:"{{^delete_time}}Active{{/delete_time}}",index:"{{_index}}",total:"{{_total}}",address_open:"{{#address}}",cond_class_example:"status-{{approval_status}}"},d={dataShape:`{
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
{{/rows}}`,chart3_template:`{{#rows}}
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
{{/rows}}`};return(Jt,e)=>(i(),r("div",f,[e[90]||(e[90]=t("div",{class:"guide-header mb-4"},[t("h2",{class:"mb-1"},[t("i",{class:"bi bi-book text-primary me-2"}),s(" Template Guide ")]),t("p",{class:"text-muted mb-0"}," How to structure your data and write Mustache templates for reports ")],-1)),t("div",h,[t("div",w,[t("div",x,[t("div",S,[(i(),r(b,null,g(m,c=>t("button",{key:c.id,class:u(["guide-nav-btn",{active:o.value===c.id}]),onClick:$t=>o.value=c.id},[t("i",{class:u(["bi",c.icon,"me-2"])},null,2),s(" "+a(c.label),1)],10,k)),64))])])]),t("div",A,[o.value==="mustache"?(i(),r("div",C,[e[20]||(e[20]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces me-2 text-primary"}),s("Mustache Syntax Reference")],-1)),e[21]||(e[21]=t("p",{class:"text-muted"},[s("Mustache is a logic-less templating language. All data comes from the "),t("code",null,"rows"),s(" array returned by your SQL query.")],-1)),t("div",T,[t("div",R,[t("table",L,[e[9]||(e[9]=t("thead",{class:"table-dark"},[t("tr",null,[t("th",null,"Syntax"),t("th",null,"Purpose"),t("th",null,"Example")])],-1)),t("tbody",null,[t("tr",null,[t("td",null,[t("code",M,a(l.variable),1)]),e[0]||(e[0]=t("td",null,"Render a value (HTML-escaped)",-1)),t("td",null,[t("code",null,a(l.ex_field),1)])]),t("tr",null,[t("td",null,[t("code",E,a(l.triple),1)]),e[1]||(e[1]=t("td",null,"Render raw HTML (unescaped)",-1)),t("td",null,[t("code",null,a(l.triple),1)])]),t("tr",null,[t("td",null,[t("code",P,a(l.section),1)]),e[2]||(e[2]=t("td",null,[s("Iterate array "),t("strong",null,"or"),s(" render if truthy")],-1)),t("td",null,[t("code",null,a(l.rows_open)+"..."+a(l.rows_close),1)])]),t("tr",null,[t("td",null,[t("code",q,a(l.inverted),1)]),e[3]||(e[3]=t("td",null,"Render if falsy or empty",-1)),t("td",null,[t("code",null,a(l.delete_check),1)])]),t("tr",null,[t("td",null,[t("code",U,a(l.dot),1)]),e[7]||(e[7]=t("td",null,[s("Current item in a "),t("em",null,"scalar"),s(" list only")],-1)),t("td",null,[t("code",null,a(l.ex_dot_loop),1),e[4]||(e[4]=s(" (tags is ",-1)),e[5]||(e[5]=t("code",null,'["a","b"]',-1)),e[6]||(e[6]=s(")",-1))])]),t("tr",null,[t("td",null,[t("code",Q,a(l.comment),1)]),e[8]||(e[8]=t("td",null,"Comment — not rendered",-1)),t("td",null,[t("code",null,a(l.ex_comment),1)])])])])])]),t("div",V,[e[10]||(e[10]=t("i",{class:"bi bi-exclamation-triangle-fill me-2"},null,-1)),e[11]||(e[11]=t("strong",null,"Closing tags must always match the opening name exactly.",-1)),t("code",H,a(l.rows_open),1),e[12]||(e[12]=s(" closes with ",-1)),t("code",null,a(l.rows_close),1),e[13]||(e[13]=s(" — never ",-1)),t("code",null,a(l.rows_wrong),1),e[14]||(e[14]=s(". ",-1))]),t("div",O,[e[19]||(e[19]=t("div",{class:"card-header"},[t("i",{class:"bi bi-lightbulb me-2 text-warning"}),s("Key rule — your data is always "),t("code",null,"rows")],-1)),t("div",j,[e[18]||(e[18]=t("p",{class:"mb-2"},[s("Every query returns a single top-level key "),t("code",null,"rows"),s(", which is a list of objects:")],-1)),t("pre",B,a(d.dataShape),1),t("p",F,[e[15]||(e[15]=s("Each row also receives ",-1)),t("code",null,a(l.index),1),e[16]||(e[16]=s(" (1-based position) and ",-1)),t("code",null,a(l.total),1),e[17]||(e[17]=s(" (total row count) automatically.",-1))])])])])):n("",!0),o.value==="flat-table"?(i(),r("div",N,[e[29]||(e[29]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-table me-2 text-primary"}),s("Flat Table Report")],-1)),e[30]||(e[30]=t("p",{class:"text-muted"},"The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.",-1)),t("div",D,[e[22]||(e[22]=t("div",{class:"step-label"},"1 · Unity Catalog Table",-1)),t("pre",I,a(d.flatTable_sql),1)]),t("div",Y,[e[23]||(e[23]=t("div",{class:"step-label"},"2 · Data Shape delivered to template",-1)),t("pre",W,a(d.flatTable_data),1)]),t("div",z,[e[24]||(e[24]=t("div",{class:"step-label"},"3 · Mustache Template",-1)),t("pre",G,a(d.flatTable_template),1)]),t("div",K,[e[25]||(e[25]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),e[26]||(e[26]=t("strong",null,"Null / empty check:",-1)),e[27]||(e[27]=s(" use ",-1)),t("code",null,a(l.inverted),1),e[28]||(e[28]=s(" to render content when a field is null, false, or empty — no logic needed. ",-1))])])):n("",!0),o.value==="struct"?(i(),r("div",J,[e[38]||(e[38]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces-asterisk me-2 text-primary"}),s("Struct Fields")],-1)),e[39]||(e[39]=t("p",{class:"text-muted"},[s("When a column is "),t("code",null,"STRUCT<...>"),s(", Mustache can push it as a context or access it with dot notation.")],-1)),t("div",$,[e[31]||(e[31]=t("div",{class:"step-label"},"1 · Unity Catalog Table with a STRUCT column",-1)),t("pre",X,a(d.struct_sql),1)]),t("div",Z,[e[32]||(e[32]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",tt,a(d.struct_data),1)]),t("div",et,[e[37]||(e[37]=t("div",{class:"step-label"},"3 · Template — two equivalent approaches",-1)),t("div",st,[t("div",at,[t("div",lt,[e[34]||(e[34]=t("div",{class:"approach-label"},"Context push (recommended)",-1)),t("pre",dt,a(d.struct_context),1),t("p",ot,[t("code",null,a(l.address_open),1),e[33]||(e[33]=s(" pushes the struct as context — child fields are then in scope directly.",-1))])])]),t("div",rt,[t("div",it,[e[35]||(e[35]=t("div",{class:"approach-label"},"Dot notation",-1)),t("pre",nt,a(d.struct_dot),1),e[36]||(e[36]=t("p",{class:"small text-muted mt-2 mb-0"},"Dot notation accesses nested fields without a context push — useful for one or two fields.",-1))])])])])])):n("",!0),o.value==="array-struct"?(i(),r("div",ct,[e[51]||(e[51]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-list-nested me-2 text-primary"}),s("Array of Structs")],-1)),e[52]||(e[52]=t("p",{class:"text-muted"},[s("When a column is "),t("code",null,"ARRAY<STRUCT<...>>"),s(", iterate the outer "),t("code",null,"rows"),s(" first, then the nested array inside.")],-1)),t("div",pt,[e[40]||(e[40]=t("div",{class:"step-label"},"1 · Unity Catalog Table with ARRAY<STRUCT>",-1)),t("pre",ut,a(d.array_sql),1)]),t("div",mt,[e[41]||(e[41]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",vt,a(d.array_data),1)]),t("div",bt,[e[42]||(e[42]=t("div",{class:"step-label"},"3 · Template — nested iteration",-1)),t("pre",gt,a(d.array_template),1)]),t("div",yt,[e[43]||(e[43]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),e[44]||(e[44]=t("strong",null,"One page per order:",-1)),e[45]||(e[45]=s(" the outer ",-1)),t("code",null,a(l.rows_open),1),e[46]||(e[46]=s(" wraps a ",-1)),e[47]||(e[47]=t("code",null,".report-page",-1)),e[48]||(e[48]=s(" div, so each order gets its own page. ",-1)),t("code",null,a(l.index),1),e[49]||(e[49]=s(" and ",-1)),t("code",null,a(l.total),1),e[50]||(e[50]=s(" are available on each row. ",-1))])])):n("",!0),o.value==="chart-struct"?(i(),r("div",_t,[e[64]||(e[64]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-bar-chart me-2 text-primary"}),s("Charts from Struct Columns")],-1)),e[65]||(e[65]=t("p",{class:"text-muted"},[s("Charts read comma-separated strings from "),t("code",null,"data-labels"),s(" and "),t("code",null,"data-values"),s(" attributes. There are three ways to feed data in.")],-1)),t("div",ft,[e[55]||(e[55]=t("div",{class:"pattern-header pattern-1"},[s("Pattern 1 — Aggregate the main "),t("code",null,"rows"),s(" array (simplest)")],-1)),t("div",ht,[e[53]||(e[53]=t("p",{class:"small text-muted mb-3"},"Use when each row already represents one data point you want to plot.",-1)),t("pre",wt,a(d.chart1_template),1),e[54]||(e[54]=t("p",{class:"small text-muted mt-2 mb-0"},[s("Mustache renders the loops into: "),t("code",null,'data-labels="EMEA,APAC,AMER,"'),s(" — trailing commas are ignored by the parser.")],-1))])]),t("div",xt,[e[57]||(e[57]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — Pre-aggregated scalar columns",-1)),t("div",St,[e[56]||(e[56]=t("p",{class:"small text-muted mb-3"},"SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.",-1)),t("pre",kt,a(d.chart2_template),1)])]),t("div",At,[e[63]||(e[63]=t("div",{class:"pattern-header pattern-3"},"Pattern 3 — ARRAY<STRUCT> chart column (self-contained)",-1)),t("div",Ct,[e[61]||(e[61]=t("p",{class:"small text-muted mb-3"},"The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.",-1)),t("div",Tt,[e[58]||(e[58]=t("div",{class:"step-label"},"SQL",-1)),t("pre",Rt,a(d.chart3_sql),1)]),t("div",Lt,[e[59]||(e[59]=t("div",{class:"step-label"},"Data Shape",-1)),t("pre",Mt,a(d.chart3_data),1)]),t("div",Et,[e[60]||(e[60]=t("div",{class:"step-label"},"Template — one page per team, each with its own chart",-1)),t("pre",Pt,a(d.chart3_template),1)]),e[62]||(e[62]=t("div",{class:"alert alert-success mb-0"},[t("i",{class:"bi bi-check-circle-fill me-2"}),t("strong",null,"Why this pattern is powerful:"),s(" each team's chart is driven entirely by its own "),t("code",null,"spend_by_month"),s(" array — no global aggregation needed in the template. The SQL does the work, the template just renders it. ")],-1))])]),e[66]||(e[66]=p('<div class="card" data-v-8ef3a6a0><div class="card-header" data-v-8ef3a6a0><i class="bi bi-table me-2" data-v-8ef3a6a0></i>Pattern comparison</div><div class="card-body p-0" data-v-8ef3a6a0><table class="table table-sm mb-0" data-v-8ef3a6a0><thead class="table-dark" data-v-8ef3a6a0><tr data-v-8ef3a6a0><th data-v-8ef3a6a0>Pattern</th><th data-v-8ef3a6a0>SQL complexity</th><th data-v-8ef3a6a0>Best for</th></tr></thead><tbody data-v-8ef3a6a0><tr data-v-8ef3a6a0><td data-v-8ef3a6a0><span class="badge pattern-badge-1" data-v-8ef3a6a0>1 — Aggregate rows</span></td><td data-v-8ef3a6a0>Low</td><td data-v-8ef3a6a0>Single summary chart across all rows</td></tr><tr data-v-8ef3a6a0><td data-v-8ef3a6a0><span class="badge pattern-badge-2" data-v-8ef3a6a0>2 — Scalar columns</span></td><td data-v-8ef3a6a0>Low–Medium</td><td data-v-8ef3a6a0>Fixed labels, one summary row</td></tr><tr data-v-8ef3a6a0><td data-v-8ef3a6a0><span class="badge pattern-badge-3" data-v-8ef3a6a0>3 — Struct array</span></td><td data-v-8ef3a6a0>Medium</td><td data-v-8ef3a6a0>Per-row charts with different datasets on each page</td></tr></tbody></table></div></div>',1))])):n("",!0),o.value==="conditional-styles"?(i(),r("div",qt,[e[87]||(e[87]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-palette me-2 text-primary"}),s("Conditional Styles")],-1)),e[88]||(e[88]=t("p",{class:"text-muted"},"Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.",-1)),t("div",Ut,[e[80]||(e[80]=t("div",{class:"pattern-header pattern-1"},"Pattern 1 — CSS class from value (styling only, no SQL changes)",-1)),t("div",Qt,[e[79]||(e[79]=t("p",{class:"small text-muted mb-3"},[s(" Interpolate the field value directly into the class name. Add a "),t("code",null,"<style>"),s(" block at the top of your template with one rule per expected value. Best for badge colours, row highlights, or any purely visual difference. ")],-1)),t("div",Vt,[e[67]||(e[67]=t("div",{class:"step-label"},"SQL — no changes needed",-1)),t("pre",Ht,a(d.conditional_sql_pattern1),1)]),t("div",Ot,[e[68]||(e[68]=t("div",{class:"step-label"},"Template",-1)),t("pre",jt,a(d.conditional_template_pattern1),1)]),t("div",Bt,[e[69]||(e[69]=t("i",{class:"bi bi-check-circle-fill me-2"},null,-1)),e[70]||(e[70]=t("strong",null,"How it works:",-1)),e[71]||(e[71]=s()),t("code",null,a(l.cond_class_example),1),e[72]||(e[72]=s(" renders as ",-1)),e[73]||(e[73]=t("code",null,"status-approved",-1)),e[74]||(e[74]=s(", ",-1)),e[75]||(e[75]=t("code",null,"status-pending",-1)),e[76]||(e[76]=s(", or ",-1)),e[77]||(e[77]=t("code",null,"status-rejected",-1)),e[78]||(e[78]=s(". Your CSS rules match on those exact class names. ",-1))])])]),t("div",Ft,[e[86]||(e[86]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — SQL boolean flags (show/hide entire blocks)",-1)),t("div",Nt,[t("p",Dt,[e[81]||(e[81]=s(" Add computed boolean columns to your SQL query. Mustache sections (",-1)),t("code",null,a(l.section),1),e[82]||(e[82]=s(") render only when the value is truthy, giving you a full conditional block — not just a style change. ",-1))]),t("div",It,[e[83]||(e[83]=t("div",{class:"step-label"},"SQL — add boolean columns",-1)),t("pre",Yt,a(d.conditional_sql_pattern2),1)]),t("div",Wt,[e[84]||(e[84]=t("div",{class:"step-label"},"Template — conditional blocks",-1)),t("pre",zt,a(d.conditional_template_pattern2),1)]),e[85]||(e[85]=t("div",{class:"alert alert-info mb-0"},[t("i",{class:"bi bi-info-circle me-2"}),t("strong",null,"When to use Pattern 2:"),s(" when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers. ")],-1))])]),e[89]||(e[89]=p('<div class="card" data-v-8ef3a6a0><div class="card-header" data-v-8ef3a6a0><i class="bi bi-table me-2" data-v-8ef3a6a0></i>Pattern comparison</div><div class="card-body p-0" data-v-8ef3a6a0><table class="table table-sm mb-0" data-v-8ef3a6a0><thead class="table-dark" data-v-8ef3a6a0><tr data-v-8ef3a6a0><th data-v-8ef3a6a0>Pattern</th><th data-v-8ef3a6a0>SQL change?</th><th data-v-8ef3a6a0>Best for</th></tr></thead><tbody data-v-8ef3a6a0><tr data-v-8ef3a6a0><td data-v-8ef3a6a0><span class="badge pattern-badge-1" data-v-8ef3a6a0>1 — CSS class from value</span></td><td data-v-8ef3a6a0>None</td><td data-v-8ef3a6a0>Badge colours, row highlights, status indicators</td></tr><tr data-v-8ef3a6a0><td data-v-8ef3a6a0><span class="badge pattern-badge-2" data-v-8ef3a6a0>2 — SQL boolean flags</span></td><td data-v-8ef3a6a0>Add <code data-v-8ef3a6a0>field = &#39;value&#39; AS is_x</code></td><td data-v-8ef3a6a0>Conditional blocks, different content per status</td></tr></tbody></table></div></div>',1))])):n("",!0)])])]))}}),Zt=_(Gt,[["__scopeId","data-v-8ef3a6a0"]]);export{Zt as default};
