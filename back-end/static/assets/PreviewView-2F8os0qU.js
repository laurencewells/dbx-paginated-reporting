import{d as z,Y as B,j as I,k as V,I as F,Z as N,T as $,c as o,a as r,b as u,w as b,x as v,g as H,B as s,C as h,a6 as S,o as l,_ as q}from"./index-DQn6lqpe.js";import{m as T}from"./mustache-lDDT9aR0.js";const G={class:"preview-view"},Y={class:"toolbar mb-4 d-flex justify-content-between align-items-center"},M=["disabled"],U={key:0,class:"spinner-border spinner-border-sm me-1",role:"status"},W={key:1,class:"bi bi-file-earmark-pdf me-1"},Z={key:0,class:"alert alert-info mb-4 d-flex align-items-center"},J={key:0},K={key:1},Q={class:"preview-container card"},X={class:"card-header d-flex justify-content-between align-items-center"},ee={key:0,class:"text-muted small"},te={class:"card-body p-0"},re={key:0,class:"empty-state"},ae={key:1,class:"d-flex justify-content-center align-items-center",style:{"min-height":"400px"}},oe=["srcdoc"],le=`
  @page { size: A4; margin: 10mm; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; box-sizing: border-box; }
  body { margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #212529; font-size: 14px; overflow-x: hidden; }

  .report-page {
    page-break-after: always;
    padding: 24px 28px;
    position: relative;
    max-width: 100%;
    overflow: hidden;
  }
  .report-page:last-child { page-break-after: auto; }

  h1, h2, h3 { color: #2d3e50; }
  h1 { font-weight: 700; }

  .report-tile {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
  }
  .report-tile.tile-primary {
    background: linear-gradient(135deg, #2d3e50 0%, #34495e 100%);
    box-shadow: 0 4px 15px rgba(45, 62, 80, 0.3);
  }
  .report-tile.tile-success {
    background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
  }
  .report-tile.tile-warning {
    background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
    box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
  }
  .report-tile.tile-danger {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
  }
  .report-tile-title {
    font-size: 0.875rem;
    opacity: 0.9;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .report-tile-value { font-size: 2rem; font-weight: 700; }

  .report-table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
  .report-table thead { background: #2d3e50; color: white; }
  .report-table th { padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.875rem; }
  .report-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }

  .chart-container { background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #eee; overflow: hidden; }
  .chart-title { font-size: 1rem; font-weight: 600; color: #2d3e50; margin-bottom: 1rem; }
  .report-bar-chart, .report-pie-chart { position: relative; width: 100%; max-height: 300px; }

  .page-number { text-align: center; font-size: 0.75rem; color: #999; padding-top: 1.5rem; margin-top: auto; border-top: 1px solid #eee; }

  @media print {
    .row { display: flex !important; flex-wrap: wrap !important; }
    [class*="col-"] { flex-shrink: 0; }
    .col-1, .col-sm-1, .col-md-1, .col-lg-1 { width: 8.3333% !important; }
    .col-2, .col-sm-2, .col-md-2, .col-lg-2 { width: 16.6667% !important; }
    .col-3, .col-sm-3, .col-md-3, .col-lg-3 { width: 25% !important; }
    .col-4, .col-sm-4, .col-md-4, .col-lg-4 { width: 33.3333% !important; }
    .col-5, .col-sm-5, .col-md-5, .col-lg-5 { width: 41.6667% !important; }
    .col-6, .col-sm-6, .col-md-6, .col-lg-6 { width: 50% !important; }
    .col-7, .col-sm-7, .col-md-7, .col-lg-7 { width: 58.3333% !important; }
    .col-8, .col-sm-8, .col-md-8, .col-lg-8 { width: 66.6667% !important; }
    .col-9, .col-sm-9, .col-md-9, .col-lg-9 { width: 75% !important; }
    .col-10, .col-sm-10, .col-md-10, .col-lg-10 { width: 83.3333% !important; }
    .col-11, .col-sm-11, .col-md-11, .col-lg-11 { width: 91.6667% !important; }
    .col-12, .col-sm-12, .col-md-12, .col-lg-12 { width: 100% !important; }
    .d-flex { display: flex !important; }
    .gap-2 { gap: 0.5rem !important; }
    .g-3 { --bs-gutter-x: 1rem; --bs-gutter-y: 1rem; }
  }
`,ie=`
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"><\/script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  var COLORS = [
    'rgba(52,152,219,0.8)','rgba(46,204,113,0.8)','rgba(155,89,182,0.8)',
    'rgba(241,196,15,0.8)','rgba(231,76,60,0.8)','rgba(26,188,156,0.8)',
    'rgba(230,126,34,0.8)'
  ];
  var BORDERS = [
    'rgba(52,152,219,1)','rgba(46,204,113,1)','rgba(155,89,182,1)',
    'rgba(241,196,15,1)','rgba(231,76,60,1)','rgba(26,188,156,1)',
    'rgba(230,126,34,1)'
  ];

  function parse(el) {
    var l = (el.getAttribute('data-labels') || '').replace(/^\\[|]$/g, '');
    var v = (el.getAttribute('data-values') || '').replace(/^\\[|]$/g, '');
    return {
      labels: l.split(',').map(function(s){return s.trim()}).filter(Boolean),
      values: v.split(',').map(function(s){return s.trim()}).filter(Boolean).map(Number)
    };
  }

  function render(selector, type) {
    document.querySelectorAll(selector).forEach(function(el) {
      var d = parse(el);
      if (!d.labels.length) return;
      var canvas = document.createElement('canvas');
      canvas.style.maxHeight = '300px';
      el.innerHTML = '';
      el.appendChild(canvas);
      new Chart(canvas, {
        type: type,
        data: {
          labels: d.labels,
          datasets: [{
            data: d.values,
            backgroundColor: COLORS.slice(0, d.values.length),
            borderColor: type === 'pie' ? '#fff' : BORDERS.slice(0, d.values.length),
            borderWidth: type === 'pie' ? 2 : 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          plugins: { legend: { display: type === 'pie', position: 'bottom' } },
          scales: type === 'bar' ? { y: { beginAtZero: true } } : {}
        }
      });
    });
  }

  render('.report-bar-chart', 'bar');
  render('.report-pie-chart', 'pie');
});
<\/script>`,se=z({__name:"PreviewView",setup(ne){const C=B(),j=I(),f=V(),g=s(()=>j.activeProjectId),w=s(()=>!!g.value),R=s(()=>({project_id:g.value})),D=s(()=>({project_id:g.value})),{data:E}=F(R,{query:{enabled:w}}),{data:A}=N(D,{query:{enabled:w}}),e=s(()=>(A.value??[]).find(a=>a.id===C.activeTemplateId)??null),c=h({}),p=h(!1),n=h(!1);async function L(){if(!e.value){c.value={};return}p.value=!0;try{const a=await S(e.value.id,{limit:10});c.value=a.data}catch{c.value={}}finally{p.value=!1}}$(()=>{var a;return(a=e.value)==null?void 0:a.id},()=>{L()},{immediate:!0});const x=s(()=>{if(!e.value)return"";try{return T.render(e.value.html_content??"",c.value)}catch{return""}});function y(a,t="Report"){return`<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${t}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<style>${le}</style>
</head>
<body>${a}${ie}</body></html>`}const _=s(()=>{var a;return x.value?y(x.value,((a=e.value)==null?void 0:a.name)??"Report"):""});async function O(){if(!e.value){f.warning("No template selected");return}n.value=!0;try{const a=await S(e.value.id,{limit:1e3}),t=T.render(e.value.html_content??"",a.data),m=y(t,e.value.name),i=document.createElement("iframe");i.style.cssText="position:fixed;left:-9999px;top:0;width:794px;height:1123px;border:none;visibility:hidden;",document.body.appendChild(i),i.srcdoc=m,i.onload=()=>{const d=i.contentWindow,k=()=>{if(d.document.querySelectorAll(".report-bar-chart:empty, .report-pie-chart:empty").length>0&&P<20){P++,setTimeout(k,150);return}d.focus(),d.print(),setTimeout(()=>{try{document.body.removeChild(i)}catch{}},2e3)};let P=0;setTimeout(k,1e3)}}catch{f.warning("Failed to generate PDF")}finally{n.value=!1}}return(a,t)=>{var m,i;return l(),o("div",G,[r("div",Y,[t[0]||(t[0]=r("h4",{class:"mb-0"},[r("i",{class:"bi bi-file-earmark-pdf me-2 text-danger"}),u(" Preview & Export")],-1)),r("button",{class:"btn btn-export",onClick:O,disabled:!e.value||n.value},[n.value?(l(),o("span",U)):(l(),o("i",W)),u(" "+b(n.value?"Generating PDF...":"Export PDF"),1)],8,M)]),e.value?(l(),o("div",Z,[t[2]||(t[2]=r("i",{class:"bi bi-info-circle me-2"},null,-1)),r("div",null,[r("strong",null,b(e.value.name),1),t[1]||(t[1]=u(" — ",-1)),p.value?(l(),o("span",J,"Loading data from Unity Catalog...")):(l(),o("span",K,"Preview shows first 10 rows. Export PDF generates the full report."))])])):v("",!0),r("div",Q,[r("div",X,[t[3]||(t[3]=r("span",null,[r("i",{class:"bi bi-file-richtext me-2"}),u(" Report Preview")],-1)),e.value?(l(),o("span",ee," Structure: "+b((i=(m=H(E))==null?void 0:m.find(d=>d.id===e.value.structure_id))==null?void 0:i.name),1)):v("",!0)]),r("div",te,[e.value?p.value?(l(),o("div",ae,[...t[5]||(t[5]=[r("div",{class:"spinner-border",role:"status"},null,-1)])])):_.value?(l(),o("iframe",{key:2,class:"pdf-preview-frame",srcdoc:_.value},null,8,oe)):v("",!0):(l(),o("div",re,[...t[4]||(t[4]=[r("i",{class:"bi bi-file-earmark-x d-block"},null,-1),r("p",null,"Select a template to preview",-1)])]))])])])}}}),me=q(se,[["__scopeId","data-v-75bd5851"]]);export{me as default};
