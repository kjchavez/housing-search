/* Housing search tracker — vanilla JS, no build. Progress persisted in localStorage. */
const LS = "housing-tracker-v1";
const STATUSES = [
  ["new","New"],["to-contact","To contact"],["contacted","Contacted"],
  ["tour","Tour set"],["applied","Applied"],["topchoice","Top choice"],["passed","Passed"]
];
const STATUS_LABEL = Object.fromEntries(STATUSES);
const TIER_LABEL = {"1":"Tier 1","2":"Tier 2","3":"Tier 3","x":"Unavailable"};
const TIER_COLOR = {"1":"var(--t1)","2":"var(--t2)","3":"var(--t3)","x":"var(--tx)"};
const CRIT_LABELS = {beds:"2+ bedrooms",busy:"Off busy street",light:"Natural light",
  yard:"Fenced yard (dog)",dist:"Near Veterans Blvd",ceilings:"Tall ceilings",
  rent:"Rent in range",garage:"Garage gym",house:"House (not apt)"};
const MATCH_ICON = {yes:"✅",partial:"⚠️",no:"❌",unknown:"❓"};

let DATA=[], STORE=loadStore();
const state={q:"",sort:"score",tiers:new Set(),flags:new Set(),status:"all"};

/* ---- cross-device transfer: share link + QR + auto-import on open ---- */
function b64encode(o){return btoa(unescape(encodeURIComponent(JSON.stringify(o))));}
function b64decode(s){return JSON.parse(decodeURIComponent(escape(atob(s))));}
function shareURL(){return location.origin+location.pathname+"#s="+encodeURIComponent(b64encode(STORE));}
function importFromHash(){
  const m=location.hash.match(/[#&]s=([^&]+)/); if(!m) return;
  try{
    const inc=b64decode(decodeURIComponent(m[1])); let n=0;
    for(const k in inc){STORE[k]=Object.assign({},STORE[k]||{},inc[k]);n++;}
    saveStore();
    history.replaceState(null,"",location.pathname+location.search);
    setTimeout(()=>toast(`Loaded saved progress for ${n} home${n!==1?"s":""} from the link.`),350);
  }catch(e){console.warn("share import failed",e);}
}
importFromHash();

function loadStore(){try{return JSON.parse(localStorage.getItem(LS))||{}}catch{return{}}}
function saveStore(){localStorage.setItem(LS,JSON.stringify(STORE))}
function rec(slug){return STORE[slug]||(STORE[slug]={})}
function statusOf(c){return (STORE[c.slug]&&STORE[c.slug].status)||c.defaultStatus||"new"}

fetch("data.json").then(r=>r.json()).then(d=>{
  DATA=d.candidates;
  document.getElementById("updated").textContent=d.meta.updated;
  buildChips(); render();
});

function buildChips(){
  const tw=document.getElementById("tierChips");
  Object.keys(TIER_LABEL).forEach(t=>{
    const c=document.createElement("span");c.className="chip";c.textContent=TIER_LABEL[t];
    c.onclick=()=>{state.tiers.has(t)?state.tiers.delete(t):state.tiers.add(t);c.classList.toggle("on");render()};
    tw.appendChild(c);
  });
  [["petsOk","🐕 Dog OK"],["garage","🏋️ Garage gym"],["yard","🌳 Fenced yard"],["bike","🚲 ≤15min bike"]].forEach(([k,lbl])=>{
    const c=document.createElement("span");c.className="chip";c.textContent=lbl;
    c.onclick=()=>{state.flags.has(k)?state.flags.delete(k):state.flags.add(k);c.classList.toggle("on");render()};
    document.getElementById("flagChips").appendChild(c);
  });
  const sel=document.getElementById("statusFilter");
  sel.innerHTML='<option value="all">All statuses</option>'+STATUSES.map(([v,l])=>`<option value="${v}">${l}</option>`).join("");
  sel.onchange=e=>{state.status=e.target.value;render()};
  document.getElementById("search").oninput=e=>{state.q=e.target.value.toLowerCase();render()};
  document.getElementById("sort").onchange=e=>{state.sort=e.target.value;render()};
  document.getElementById("reset").onclick=()=>{
    state.q="";state.sort="score";state.tiers.clear();state.flags.clear();state.status="all";
    document.getElementById("search").value="";document.getElementById("sort").value="score";
    document.getElementById("statusFilter").value="all";
    document.querySelectorAll(".chip.on").forEach(c=>c.classList.remove("on"));render();
  };
  document.getElementById("export").onclick=exportProgress;
  document.getElementById("importBtn").onclick=()=>document.getElementById("importFile").click();
  document.getElementById("importFile").onchange=importProgress;
  document.getElementById("share").onclick=openShare;
  document.getElementById("copyShare").onclick=()=>{
    const i=document.getElementById("shareUrl"); i.select();
    const done=()=>toast("Link copied — text or email it to your phone, then open it.");
    if(navigator.clipboard) navigator.clipboard.writeText(i.value).then(done).catch(()=>{document.execCommand("copy");done();});
    else{document.execCommand("copy");done();}
  };
}

function passes(c){
  if(state.q){const hay=(c.name+" "+c.city+" "+c.type+" "+c.summary).toLowerCase();if(!hay.includes(state.q))return false;}
  if(state.tiers.size&&!state.tiers.has(c.tier))return false;
  if(state.status!=="all"&&statusOf(c)!==state.status)return false;
  for(const f of state.flags){
    if(f==="petsOk"&&c.petsOk!==true)return false;
    if(f==="garage"&&!(c.criteria.garage==="yes"))return false;
    if(f==="yard"&&!(c.criteria.yard==="yes"))return false;
    if(f==="bike"&&!(c.bikeMin&&c.bikeMin<=15))return false;
  }
  return true;
}
function sortList(list){
  const s=state.sort;
  const by={score:(a,b)=>b.score-a.score,
    rent:(a,b)=>(a.rent??1e9)-(b.rent??1e9),
    dist:(a,b)=>a.distMi-b.distMi,
    beds:(a,b)=>b.beds-a.beds};
  return list.sort(by[s]||by.score);
}

function render(){
  const list=sortList(DATA.filter(passes));
  renderStats();
  const grid=document.getElementById("grid");
  grid.innerHTML="";
  if(!list.length){grid.innerHTML='<div class="empty">No matches with these filters.</div>';return;}
  list.forEach(c=>grid.appendChild(card(c)));
}

function renderStats(){
  const el=document.getElementById("stats");
  const counts={};DATA.forEach(c=>{const s=statusOf(c);counts[s]=(counts[s]||0)+1;});
  const cells=[["Total",DATA.length,""]];
  STATUSES.forEach(([v,l])=>{if(counts[v])cells.push([l,counts[v],v]);});
  el.innerHTML=cells.map(([l,n,s])=>`<div class="stat"><b>${n}</b><span>${s?`<span class="dot s-${s}" style="display:inline-block;vertical-align:middle;margin-right:5px"></span>`:""}${l}</span></div>`).join("");
}

function photoBg(c){return c.photos&&c.photos.length?`background-image:url('${c.photos[0].thumb}')`:"";}

function card(c){
  const el=document.createElement("div");el.className="card";
  const st=statusOf(c);
  el.innerHTML=`
    <div class="photo" style="${photoBg(c)}">
      ${c.photos&&c.photos.length?"":'<div class="ph">no photo — see listing</div>'}
      <span class="ribbon" style="background:${TIER_COLOR[c.tier]}">${TIER_LABEL[c.tier]}</span>
      <span class="score">${c.score.toFixed(1)}</span>
    </div>
    <div class="body">
      <h3>${c.name}</h3>
      <div class="loc">${c.city} · ${c.type}</div>
      <div class="rentline"><span class="rent">${c.rentLabel}</span>
        <span class="meta">${c.beds}bd · ${c.baths}ba · ${c.sqft?c.sqft.toLocaleString()+" sqft":"—"}</span></div>
      <div class="meta">🚲 ~${c.bikeMin}min (${c.distMi}mi) to Veterans · 📅 ${c.avail}</div>
      <div class="badges">${badges(c)}</div>
      <div class="statusbar">
        <span class="dot s-${st}"></span>
        <select onclick="event.stopPropagation()" data-slug="${c.slug}">
          ${STATUSES.map(([v,l])=>`<option value="${v}" ${v===st?"selected":""}>${l}</option>`).join("")}
        </select>
      </div>
    </div>`;
  el.querySelector("select").onchange=e=>{rec(c.slug).status=e.target.value;saveStore();render();};
  el.onclick=()=>openModal(c);
  return el;
}
function badges(c){
  const b=[];
  if(c.petsOk===true)b.push('<span class="badge good">🐕 dog OK</span>');
  else if(c.petsOk===false)b.push('<span class="badge bad">🚫 no pets</span>');
  else b.push('<span class="badge">🐕 pets?</span>');
  const g=c.criteria.garage;
  if(g==="yes")b.push('<span class="badge good">🏋️ garage</span>');
  else if(g==="partial")b.push('<span class="badge warn">garage*</span>');
  else if(g==="no")b.push('<span class="badge bad">no garage</span>');
  const y=c.criteria.yard;
  if(y==="yes")b.push('<span class="badge good">🌳 fenced yard</span>');
  else if(y==="partial")b.push('<span class="badge warn">yard*</span>');
  return b.join("");
}

function openModal(c){
  const st=statusOf(c);const r=rec(c.slug);
  document.getElementById("mTitle").textContent=c.name;
  const sheet=document.getElementById("sheet");
  document.getElementById("gallery").innerHTML=(c.photos||[]).map(p=>`<img loading="lazy" src="${p.thumb}" data-full="${p.full}">`).join("")
    || '<div class="empty" style="padding:24px">No photos captured — open the listing for images.</div>';
  document.querySelectorAll("#gallery img").forEach(im=>im.onclick=()=>lightbox(im.dataset.full));
  document.getElementById("mInfo").innerHTML=`
    <div class="kv">
      <div class="k">Rent</div><div>${c.rentLabel}</div>
      <div class="k">Beds / Baths</div><div>${c.beds} bd / ${c.baths} ba</div>
      <div class="k">Size</div><div>${c.sqft?c.sqft.toLocaleString()+" sqft":"—"}</div>
      <div class="k">Type</div><div>${c.type}</div>
      <div class="k">Pets</div><div>${c.pets}</div>
      <div class="k">Garage</div><div>${c.garage}</div>
      <div class="k">Yard</div><div>${c.yard}</div>
      <div class="k">To Veterans Blvd</div><div>~${c.distMi} mi · ~${c.bikeMin} min bike</div>
      <div class="k">Available</div><div>${c.avail}</div>
      <div class="k">Listing</div><div><a href="${c.source.url}" target="_blank" rel="noopener">${c.source.name} ↗</a></div>
    </div>
    <div class="flags">${(c.flags||[]).map(f=>`<span class="flag">${f}</span>`).join("")}</div>
    <p style="color:var(--muted);font-size:13.5px">${c.summary}</p>`;
  document.getElementById("mCrit").innerHTML=`<table class="crit">${
    Object.entries(c.criteria).map(([k,v])=>`<tr><td>${CRIT_LABELS[k]}</td><td>${MATCH_ICON[v]} ${v}</td></tr>`).join("")
  }</table>`;
  const sel=document.getElementById("mStatus");
  sel.innerHTML=STATUSES.map(([v,l])=>`<option value="${v}" ${v===st?"selected":""}>${l}</option>`).join("");
  sel.onchange=e=>{rec(c.slug).status=e.target.value;saveStore();render();};
  const ta=document.getElementById("mNotes");ta.value=r.notes||"";
  const saved=document.getElementById("mSaved");
  let t;ta.oninput=()=>{rec(c.slug).notes=ta.value;saveStore();saved.textContent="saved ✓";clearTimeout(t);t=setTimeout(()=>saved.textContent="",1200);};
  document.getElementById("modal").classList.add("open");
}
function closeModal(){document.getElementById("modal").classList.remove("open");}
function lightbox(src){const lb=document.getElementById("lightbox");lb.querySelector("img").src=src;lb.classList.add("open");}

document.addEventListener("click",e=>{
  if(e.target.classList.contains("modal"))e.target.classList.remove("open");          // backdrop click
  if(e.target.classList.contains("close")){const m=e.target.closest(".modal");if(m)m.classList.remove("open");}
  if(e.target.id==="lightbox")e.target.classList.remove("open");
});
document.addEventListener("keydown",e=>{if(e.key==="Escape"){document.querySelectorAll(".modal.open,.lightbox.open").forEach(m=>m.classList.remove("open"));}});

function exportProgress(){
  const blob=new Blob([JSON.stringify(STORE,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);
  a.download="housing-progress.json";a.click();
}
function toast(msg){
  let t=document.getElementById("toast");
  if(!t){t=document.createElement("div");t.id="toast";document.body.appendChild(t);}
  t.textContent=msg;t.classList.add("show");
  clearTimeout(toast._t);toast._t=setTimeout(()=>t.classList.remove("show"),4500);
}
function openShare(){
  const empty=!Object.keys(STORE).length;
  const url=shareURL();
  document.getElementById("shareUrl").value=url;
  document.getElementById("shareEmpty").style.display=empty?"block":"none";
  renderQR(url);
  document.getElementById("shareModal").classList.add("open");
}
function renderQR(url){
  const el=document.getElementById("qr"); el.innerHTML="";
  if(url.length>1800){el.innerHTML='<p class="qrnote">Your notes are long, so the QR code would be too dense to scan. Use <b>Copy link</b> instead.</p>';return;}
  try{const t=qrcode(0,"M");t.addData(url);t.make();el.innerHTML=t.createImgTag(5,12);}
  catch(e){el.innerHTML='<p class="qrnote">Couldn’t fit the data in a QR code — use <b>Copy link</b>.</p>';}
}
function importProgress(e){
  const f=e.target.files[0];if(!f)return;
  const fr=new FileReader();fr.onload=()=>{try{STORE=JSON.parse(fr.result);saveStore();render();alert("Progress imported.");}catch{alert("Invalid file.");}};
  fr.readAsText(f);
}
window.closeModal=closeModal;
