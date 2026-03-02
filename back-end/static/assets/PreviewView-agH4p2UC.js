import{d as L,K as j,j as O,k as z,L as F,E as V,c as o,a as t,b as u,F as B,r as N,g as S,t as g,q as b,x as v,y as f,U as C,o as l,_ as $}from"./index-_s3yZ24f.js";import{m as P}from"./mustache-lDDT9aR0.js";const H={class:"preview-view"},I={class:"toolbar mb-4 d-flex justify-content-between align-items-center"},q={class:"d-flex align-items-center gap-3"},G=["value"],U=["value"],M={class:"d-flex gap-2"},W=["disabled"],Y={key:0,class:"spinner-border spinner-border-sm me-1",role:"status"},K={key:1,class:"bi bi-file-earmark-pdf me-1"},Z={key:0,class:"alert alert-info mb-4 d-flex align-items-center"},J={key:0},Q={key:1},X={class:"preview-container card"},ee={class:"card-header d-flex justify-content-between align-items-center"},te={key:0,class:"text-muted small"},ae={class:"card-body p-0"},re={key:0,class:"empty-state"},oe={key:1,class:"d-flex justify-content-center align-items-center",style:{"min-height":"400px"}},le=["srcdoc"],ie=`
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
`,se=`
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
<\/script>`,ne=L({__name:"PreviewView",setup(de){const h=j(),w=O(),{data:R}=z(),{data:x}=F(),a=v(()=>{var r;return((r=x.value)==null?void 0:r.find(e=>e.id===h.activeTemplateId))??null}),c=f({}),p=f(!1),d=f(!1);async function D(){if(!a.value){c.value={};return}p.value=!0;try{const r=await C(a.value.id,{limit:10});c.value=r.data}catch{c.value={}}finally{p.value=!1}}V(()=>{var r;return(r=a.value)==null?void 0:r.id},()=>{D()},{immediate:!0});const y=v(()=>{if(!a.value)return"";try{return P.render(a.value.html_content??"",c.value)}catch{return""}});function _(r,e="Report"){return`<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${e}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<style>${ie}</style>
</head>
<body>${r}${se}</body></html>`}const k=v(()=>{var r;return y.value?_(y.value,((r=a.value)==null?void 0:r.name)??"Report"):""});function E(r){h.setActiveTemplate(r)}async function A(){if(!a.value){w.warning("No template selected");return}d.value=!0;try{const r=await C(a.value.id,{limit:1e3}),e=P.render(a.value.html_content??"",r.data),m=_(e,a.value.name),s=document.createElement("iframe");s.style.cssText="position:fixed;left:-9999px;top:0;width:794px;height:1123px;border:none;visibility:hidden;",document.body.appendChild(s),s.srcdoc=m,s.onload=()=>{const n=s.contentWindow,i=()=>{if(n.document.querySelectorAll(".report-bar-chart:empty, .report-pie-chart:empty").length>0&&T<20){T++,setTimeout(i,150);return}n.focus(),n.print(),setTimeout(()=>{try{document.body.removeChild(s)}catch{}},2e3)};let T=0;setTimeout(i,1e3)}}catch{w.warning("Failed to generate PDF")}finally{d.value=!1}}return(r,e)=>{var m,s,n;return l(),o("div",H,[t("div",I,[t("div",q,[e[2]||(e[2]=t("h4",{class:"mb-0"},[t("i",{class:"bi bi-file-earmark-pdf me-2 text-danger"}),u(" Preview & Export")],-1)),t("select",{value:((m=a.value)==null?void 0:m.id)||"",class:"form-select",style:{width:"250px"},onChange:e[0]||(e[0]=i=>E(i.target.value))},[e[1]||(e[1]=t("option",{value:"",disabled:""},"Select Template",-1)),(l(!0),o(B,null,N(S(x)??[],i=>(l(),o("option",{key:i.id,value:i.id},g(i.name),9,U))),128))],40,G)]),t("div",M,[t("button",{class:"btn btn-export",onClick:A,disabled:!a.value||d.value},[d.value?(l(),o("span",Y)):(l(),o("i",K)),u(" "+g(d.value?"Generating PDF...":"Export PDF"),1)],8,W)])]),a.value?(l(),o("div",Z,[e[4]||(e[4]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),t("div",null,[t("strong",null,g(a.value.name),1),e[3]||(e[3]=u(" — ",-1)),p.value?(l(),o("span",J,"Loading data from Unity Catalog...")):(l(),o("span",Q,"Preview shows first 10 rows. Export PDF generates the full report."))])])):b("",!0),t("div",X,[t("div",ee,[e[5]||(e[5]=t("span",null,[t("i",{class:"bi bi-file-richtext me-2"}),u(" Report Preview")],-1)),a.value?(l(),o("span",te," Structure: "+g((n=(s=S(R))==null?void 0:s.find(i=>i.id===a.value.structure_id))==null?void 0:n.name),1)):b("",!0)]),t("div",ae,[a.value?p.value?(l(),o("div",oe,[...e[7]||(e[7]=[t("div",{class:"spinner-border",role:"status"},null,-1)])])):k.value?(l(),o("iframe",{key:2,class:"pdf-preview-frame",srcdoc:k.value},null,8,le)):b("",!0):(l(),o("div",re,[...e[6]||(e[6]=[t("i",{class:"bi bi-file-earmark-x d-block"},null,-1),t("p",null,"Select a template to preview",-1)])]))])])])}}}),ue=$(ne,[["__scopeId","data-v-1ed14a0d"]]);export{ue as default};
