"""
ACE-Omega Shared Components v4.0
- Global node label toggle (show all names / hover-only)
- Enhanced visual effects: glow, nebula, connections, animated rings
- Per-page AI analysis widget (scrollable)
- Lock camera button in 3D views
- Export PNG button
- Session save/load
- Legend overlay
"""
import json, base64, time, hashlib
from datetime import datetime
from pathlib import Path
import streamlit as st
from utils.i18n import t

def L(k):
    return t(k, st.session_state.get("lang", "en"))


# ═══════════════════════════════════════
# PER-PAGE AI ANALYSIS WIDGET
# ═══════════════════════════════════════

def render_ai_analysis(page_name, context_text):
    """Render an AI analysis section at the bottom of any page."""
    st.markdown("---")
    st.markdown(f"### 🤖 AI Analysis — {page_name}")
    papers = st.session_state.get("papers", [])
    stats = st.session_state.get("stats", {})
    dataset_summary = f"Dataset: {stats.get('total_papers',0)} papers, {stats.get('total_citations',0)} citations. "
    dataset_summary += f"Year range: {stats.get('year_min','?')}–{stats.get('year_max','?')}. "
    dataset_summary += f"Modules: {', '.join(f'{k}({v})' for k,v in stats.get('modules',{}).items())}. "
    dataset_summary += f"Page context: {context_text}"
    key_prefix = f"ai_{page_name.replace(' ','_').lower()}"
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        q1 = st.button("Summarize", key=f"{key_prefix}_sum", use_container_width=True)
    with qc2:
        q2 = st.button("Find Patterns", key=f"{key_prefix}_pat", use_container_width=True)
    with qc3:
        q3 = st.button("Suggest Next Steps", key=f"{key_prefix}_next", use_container_width=True)
    custom_q = st.text_input("Ask anything about this view...", key=f"{key_prefix}_custom", placeholder="e.g. What anomalies do you see?")
    query = None
    if q1: query = f"Summarize the key findings on the {page_name} page."
    elif q2: query = f"What patterns or anomalies do you see in the {page_name} data?"
    elif q3: query = f"Based on the {page_name} analysis, what should the researcher do next?"
    elif custom_q and st.button("Ask", key=f"{key_prefix}_ask"):
        query = custom_q
    if query:
        from utils.ace_model import infer
        with st.spinner("Analyzing..."):
            system = f"You are ACE-Omega, an academic universe analysis AI. You are analyzing the '{page_name}' view. Be specific, cite paper titles when possible. Respond in the user's language."
            full_prompt = f"Context:\n{dataset_summary}\n\nQuestion: {query}"
            mcfg = st.session_state.config.get("model", {})
            r = infer(full_prompt, mcfg, system)
        if r.error:
            st.error(f"Error: {r.error}")
        else:
            st.markdown(f"""<div style="max-height:300px;overflow-y:auto;background:#16161a;
                border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:16px;margin-top:8px;">
                <div style="margin-bottom:8px;">
                    <span style="background:rgba(110,168,254,0.12);color:#6ea8fe;padding:2px 8px;border-radius:3px;font-size:10px;">{r.backend}</span>
                    <span style="background:rgba(117,217,160,0.12);color:#75d9a0;padding:2px 8px;border-radius:3px;font-size:10px;margin-left:4px;">{r.latency_ms:.0f}ms</span>
                </div>
                <div style="color:#d4d4d8;font-size:14px;line-height:1.6;white-space:pre-wrap;">{r.text}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════
# EXPORT PNG BUTTON
# ═══════════════════════════════════════

EXPORT_JS = """
<div style="display:flex;gap:6px;margin-top:8px;">
<button onclick="(function(){var c=document.querySelector('canvas');if(!c){var f=document.querySelectorAll('iframe');for(var i=0;i<f.length;i++){try{c=f[i].contentDocument.querySelector('canvas');if(c)break;}catch(e){}}}if(c){var a=document.createElement('a');a.download='ace_omega.png';a.href=c.toDataURL('image/png');a.click();}else{alert('No canvas found');}})()"
style="background:#2a2a30;color:#d4d4d8;border:1px solid rgba(255,255,255,0.06);
border-radius:4px;padding:5px 14px;font-size:12px;cursor:pointer;font-family:Inter,sans-serif;">
Export PNG</button>
</div>
"""

def render_export_buttons():
    st.markdown(EXPORT_JS, unsafe_allow_html=True)


# ═══════════════════════════════════════
# THREE.JS BOILERPLATE — ENHANCED v4
# ═══════════════════════════════════════

def three_boilerplate(show_labels_default=False):
    """HTML head for Three.js with tooltip + label toggle + enhanced UI."""
    label_init = "true" if show_labels_default else "false"
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0a0f;overflow:hidden;font-family:Inter,'Noto Sans SC',sans-serif}}
#tooltip{{position:fixed;display:none;background:rgba(10,10,15,0.96);color:#e0e0e8;
border:1px solid rgba(110,168,254,0.25);border-radius:6px;padding:10px 14px;
font-size:12px;max-width:320px;pointer-events:none;z-index:100;line-height:1.5;
box-shadow:0 4px 24px rgba(0,0,0,0.6),0 0 12px rgba(110,168,254,0.08);
backdrop-filter:blur(12px)}}
#tooltip b{{color:#fff;font-size:13px}}
#tooltip .tip-meta{{color:#6ea8fe;font-size:11px;margin-top:4px}}
#tooltip .tip-kw{{color:#75d9a0;font-size:10px;margin-top:3px;opacity:0.8}}

/* Control bar */
#ctrl-bar{{position:fixed;top:8px;left:8px;z-index:200;display:flex;gap:5px;align-items:center}}
#ctrl-bar button{{background:rgba(30,30,35,0.92);color:#d4d4d8;
border:1px solid rgba(255,255,255,0.1);border-radius:5px;padding:5px 12px;
font-size:11px;cursor:pointer;font-family:Inter,sans-serif;
backdrop-filter:blur(8px);transition:all .2s}}
#ctrl-bar button:hover{{background:rgba(110,168,254,0.15);color:#6ea8fe;border-color:rgba(110,168,254,0.3)}}
#ctrl-bar button.active{{background:rgba(110,168,254,0.2);color:#6ea8fe;border-color:#6ea8fe;
box-shadow:0 0 8px rgba(110,168,254,0.15)}}

/* Legend */
#legend{{position:fixed;bottom:12px;right:12px;z-index:200;background:rgba(10,10,15,0.88);
border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:10px 14px;
font-size:11px;color:#8b8b94;backdrop-filter:blur(8px);max-width:180px}}
#legend .lg-title{{color:#d4d4d8;font-weight:600;margin-bottom:6px;font-size:12px}}
#legend .lg-item{{display:flex;align-items:center;gap:6px;margin-bottom:3px}}
#legend .lg-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
#legend .lg-special{{display:flex;align-items:center;gap:6px;margin-top:6px;padding-top:6px;
border-top:1px solid rgba(255,255,255,0.06)}}

/* Stats bar */
#stats-bar{{position:fixed;top:8px;right:12px;z-index:200;background:rgba(10,10,15,0.85);
border:1px solid rgba(255,255,255,0.06);border-radius:5px;padding:5px 12px;
font-size:10px;color:#8b8b94;backdrop-filter:blur(8px)}}
#stats-bar span{{margin:0 6px}}
#stats-bar .sv{{color:#6ea8fe}}
</style></head><body>
<div id="tooltip"></div>
<div id="ctrl-bar">
    <button id="lockBtn" onclick="toggleLock()">🔒 Lock</button>
    <button id="labelBtn" onclick="toggleLabels()" class="{('active' if show_labels_default else '')}">🏷️ {('Labels ON' if show_labels_default else 'Labels')}</button>
</div>
<div id="stats-bar">
    <span>Papers: <span class="sv" id="s-total">0</span></span>
    <span>Visible: <span class="sv" id="s-visible">0</span></span>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
var _cameraLocked=false, _showLabels={label_init};
function toggleLock(){{
    _cameraLocked=!_cameraLocked;
    var btn=document.getElementById('lockBtn');
    btn.textContent=_cameraLocked?'🔓 Unlock':'🔒 Lock';
    btn.className=_cameraLocked?'active':'';
}}
function toggleLabels(){{
    _showLabels=!_showLabels;
    var btn=document.getElementById('labelBtn');
    btn.className=_showLabels?'active':'';
    btn.textContent=_showLabels?'🏷️ Labels ON':'🏷️ Labels';
    if(typeof updateLabels==='function') updateLabels();
}}
</script>
"""


def three_label_system():
    """CSS2D-like label system using HTML overlays for node names."""
    return """
// ===== TEXT LABEL SYSTEM =====
var _labelContainer = document.createElement('div');
_labelContainer.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:50;overflow:hidden';
document.body.appendChild(_labelContainer);

var _labels = [];
function createLabel(mesh, text, color) {
    var el = document.createElement('div');
    el.textContent = text.length > 24 ? text.substring(0,22) + '…' : text;
    el.style.cssText = 'position:absolute;color:' + (color||'#d4d4d8') +
        ';font-size:9px;font-family:Inter,sans-serif;white-space:nowrap;opacity:0;' +
        'text-shadow:0 0 4px rgba(0,0,0,0.95),0 0 8px rgba(0,0,0,0.8),0 1px 2px rgba(0,0,0,0.9);' +
        'pointer-events:none;transition:opacity 0.25s;letter-spacing:0.3px';
    _labelContainer.appendChild(el);
    _labels.push({el: el, mesh: mesh});
}

function updateLabels() {
    if (!cam || !ren) return;
    var w2 = ren.domElement.clientWidth / 2;
    var h2 = ren.domElement.clientHeight / 2;
    for (var i = 0; i < _labels.length; i++) {
        var lb = _labels[i];
        if (_showLabels) {
            var pos = lb.mesh.position.clone();
            var r = 1.0;
            try { r = lb.mesh.geometry.parameters.radius || 1; } catch(e){}
            pos.y += r * 1.3 + 0.8;
            pos.project(cam);
            if (pos.z > 1) { lb.el.style.opacity = '0'; continue; }
            var sx = (pos.x * w2) + w2;
            var sy = -(pos.y * h2) + h2;
            lb.el.style.left = sx + 'px';
            lb.el.style.top = (sy - 14) + 'px';
            lb.el.style.transform = 'translateX(-50%)';
            // Distance-based fade
            var dist = cam.position.distanceTo(lb.mesh.position);
            var alpha = dist < 30 ? 0.95 : dist < 80 ? 0.95 - (dist-30)/100 : 0.12;
            lb.el.style.opacity = String(Math.max(0.08, alpha));
        } else {
            lb.el.style.opacity = '0';
        }
    }
}
"""


def three_orbit_controls():
    """Mouse orbit control code with lock support."""
    return """
let _drag=0,_pm={x:0,y:0},_angle=0,_dist=90,_height=60,_targetX=0,_targetZ=0;
ren.domElement.addEventListener('mousedown',e=>{if(!_cameraLocked){_drag=1;_pm={x:e.clientX,y:e.clientY}}});
ren.domElement.addEventListener('mousemove',e=>{if(_drag&&!_cameraLocked){_angle+=(e.clientX-_pm.x)*.005;_height+=(e.clientY-_pm.y)*.3;_height=Math.max(5,Math.min(150,_height));_pm={x:e.clientX,y:e.clientY}}});
ren.domElement.addEventListener('mouseup',()=>_drag=0);
ren.domElement.addEventListener('mouseleave',()=>_drag=0);
ren.domElement.addEventListener('wheel',e=>{if(!_cameraLocked){_dist+=e.deltaY*.05;_dist=Math.max(15,Math.min(250,_dist));}e.preventDefault()},{passive:false});
addEventListener('resize',()=>{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();ren.setSize(innerWidth,innerHeight)});
"""


def three_tooltip_code():
    """Enhanced raycaster tooltip with keywords and module info + hover label."""
    return """
var _ray=new THREE.Raycaster(),_mouse=new THREE.Vector2(),_tip=document.getElementById('tooltip');
var _hoveredMesh=null;

// Single hover label element
var _hoverLabel=document.createElement('div');
_hoverLabel.style.cssText='position:fixed;color:#fff;font-size:11px;font-family:Inter,sans-serif;'+
    'white-space:nowrap;pointer-events:none;z-index:90;opacity:0;transition:opacity 0.15s;'+
    'text-shadow:0 0 6px rgba(110,168,254,0.5),0 0 3px rgba(0,0,0,0.9);font-weight:500;letter-spacing:0.2px';
document.body.appendChild(_hoverLabel);

ren.domElement.addEventListener('mousemove',function(e){
    _mouse.x=(e.clientX/innerWidth)*2-1;_mouse.y=-(e.clientY/innerHeight)*2+1;
    _ray.setFromCamera(_mouse,cam);
    if(typeof paperMeshes!=='undefined'){
        var hits=_ray.intersectObjects(paperMeshes);
        if(hits.length>0){
            var obj=hits[0].object, d=obj.userData;
            _tip.style.display='block';
            _tip.style.left=(e.clientX+14)+'px';_tip.style.top=(e.clientY+14)+'px';
            var html='<b>'+d.title+'</b><br><span style="color:#8b8b94">'+d.authors+'</span>';
            html+='<div class="tip-meta">'+d.year+' · '+d.cited+' citations · '+d.module+'</div>';
            if(d.keywords) html+='<div class="tip-kw">'+d.keywords+'</div>';
            _tip.innerHTML=html;

            // Show hover label above the node (always, even if global labels off)
            if(!_showLabels){
                var lpos=obj.position.clone();
                try{lpos.y+=obj.geometry.parameters.radius*1.3+1;}catch(ex){lpos.y+=2;}
                lpos.project(cam);
                if(lpos.z<1){
                    var lsx=(lpos.x*(innerWidth/2))+(innerWidth/2);
                    var lsy=-(lpos.y*(innerHeight/2))+(innerHeight/2);
                    _hoverLabel.style.left=lsx+'px';_hoverLabel.style.top=(lsy-16)+'px';
                    _hoverLabel.style.transform='translateX(-50%)';
                    _hoverLabel.textContent=d.title.length>30?d.title.substring(0,28)+'…':d.title;
                    _hoverLabel.style.opacity='1';
                }
            }

            // Hover glow
            if(_hoveredMesh && _hoveredMesh!==obj && _hoveredMesh._origEmissive!==undefined){
                _hoveredMesh.material.emissiveIntensity=_hoveredMesh._origEmissive;
                if(_hoveredMesh._origScale) _hoveredMesh.scale.copy(_hoveredMesh._origScale);
            }
            if(obj.material.emissive){
                if(obj._origEmissive===undefined) obj._origEmissive=obj.material.emissiveIntensity||0;
                obj.material.emissiveIntensity=0.65;
            }
            if(!obj._origScale){obj._origScale=obj.scale.clone();}
            obj.scale.set(obj._origScale.x*1.15, obj._origScale.y*1.15, obj._origScale.z*1.15);
            _hoveredMesh=obj;
        } else {
            _tip.style.display='none';
            _hoverLabel.style.opacity='0';
            if(_hoveredMesh){
                if(_hoveredMesh._origEmissive!==undefined) _hoveredMesh.material.emissiveIntensity=_hoveredMesh._origEmissive;
                if(_hoveredMesh._origScale) _hoveredMesh.scale.copy(_hoveredMesh._origScale);
                _hoveredMesh=null;
            }
        }
    }
});
"""


def three_enhanced_stars(count=10000):
    """Multi-layer star field with varying sizes and subtle colors."""
    return f"""
// ===== ENHANCED STAR FIELD =====
function makeStarLayer(n, spread, size, color) {{
    var g = new THREE.BufferGeometry();
    var pos = new Float32Array(n*3);
    for(var i=0;i<n*3;i++) pos[i]=(Math.random()-0.5)*spread;
    g.setAttribute('position',new THREE.BufferAttribute(pos,3));
    return new THREE.Points(g, new THREE.PointsMaterial({{color:color,size:size,transparent:true,opacity:0.8}}));
}}
scene.add(makeStarLayer({count}, 600, 0.15, 0x666677));
scene.add(makeStarLayer({count//3}, 500, 0.35, 0x8888aa));
scene.add(makeStarLayer({count//8}, 400, 0.6, 0xaabbdd));
scene.add(makeStarLayer({count//15}, 450, 0.4, 0xffddaa));
"""


def three_nebula_particles(count=2000):
    """Soft nebula cloud particles for background atmosphere."""
    return f"""
// ===== NEBULA PARTICLES =====
var _nebGeo=new THREE.BufferGeometry();
var _nebPos=new Float32Array({count}*3), _nebCol=new Float32Array({count}*3);
var nebColors=[[0.25,0.35,0.65],[0.45,0.2,0.55],[0.15,0.45,0.45],[0.55,0.25,0.35]];
for(var i=0;i<{count};i++){{
    _nebPos[i*3]=(Math.random()-0.5)*400;
    _nebPos[i*3+1]=(Math.random()-0.5)*200;
    _nebPos[i*3+2]=(Math.random()-0.5)*400;
    var nc=nebColors[Math.floor(Math.random()*nebColors.length)];
    _nebCol[i*3]=nc[0];_nebCol[i*3+1]=nc[1];_nebCol[i*3+2]=nc[2];
}}
_nebGeo.setAttribute('position',new THREE.BufferAttribute(_nebPos,3));
_nebGeo.setAttribute('color',new THREE.BufferAttribute(_nebCol,3));
var _nebMat=new THREE.PointsMaterial({{size:2.5,vertexColors:true,transparent:true,opacity:0.06,blending:THREE.AdditiveBlending}});
scene.add(new THREE.Points(_nebGeo,_nebMat));
"""


def three_connection_lines():
    """Draw faint lines between nearby papers in the same module cluster."""
    return """
// ===== MODULE CONNECTION LINES =====
var _connLines=[];
var modGroups={};
for(var i=0;i<paperMeshes.length;i++){
    var mod=paperMeshes[i].userData.module;
    if(!modGroups[mod]) modGroups[mod]=[];
    modGroups[mod].push(i);
}
for(var mod in modGroups){
    var grp=modGroups[mod];
    var maxConn=Math.min(grp.length*2, 100);
    var connCount=0;
    for(var i=0;i<grp.length && connCount<maxConn;i++){
        var mi=paperMeshes[grp[i]];
        var dists=[];
        for(var j=i+1;j<grp.length;j++){
            var mj=paperMeshes[grp[j]];
            var d=mi.position.distanceTo(mj.position);
            if(d<25) dists.push({j:j,d:d});
        }
        dists.sort(function(a,b){return a.d-b.d});
        for(var k=0;k<Math.min(2,dists.length);k++){
            var mj=paperMeshes[grp[dists[k].j]];
            var lg=new THREE.BufferGeometry().setFromPoints([mi.position, mj.position]);
            var col=new THREE.Color(mi.material.color||0x6ea8fe);
            var lm=new THREE.Line(lg,new THREE.LineBasicMaterial({color:col,transparent:true,opacity:0.05}));
            scene.add(lm);_connLines.push(lm);
            connCount++;
        }
    }
}
"""


def three_legend_html(modules_dict=None):
    """Generate legend HTML+JS for the 3D scene."""
    if not modules_dict:
        return ""
    from utils.data_processor import MODULE_COLORS
    items = ""
    for mod in sorted(modules_dict.keys()):
        color = MODULE_COLORS.get(mod, "#8ab4f8")
        items += f'<div class="lg-item"><div class="lg-dot" style="background:{color}"></div>{mod}</div>'
    return f"""
    var _lgEl=document.createElement('div');_lgEl.id='legend';
    _lgEl.innerHTML='<div class="lg-title">Modules</div>{items}'+
        '<div class="lg-special"><div class="lg-dot" style="background:#111;border:1px solid #f44"></div>Black Hole</div>'+
        '<div class="lg-special"><div class="lg-dot" style="background:transparent;border:1px solid #6ea8fe;box-shadow:0 0 4px #6ea8fe"></div>Dyson Sphere</div>';
    document.body.appendChild(_lgEl);
    """


def get_search_highlight_js(search_term):
    """JS to highlight matching papers with pulse effect."""
    if not search_term:
        return ""
    safe = search_term.replace("'", "\\'").replace('"', '\\"').lower()
    return f"""
    var _sq='{safe}';var _searchMatches=[];
    if(_sq && typeof paperMeshes!=='undefined'){{
        for(var i=0;i<paperMeshes.length;i++){{
            var pm=paperMeshes[i],pd=pm.userData;
            var match=(pd.title||'').toLowerCase().includes(_sq)||(pd.authors||'').toLowerCase().includes(_sq)||(pd.keywords||'').toLowerCase().includes(_sq);
            if(match){{pm.scale.set(1.6,1.6,1.6);pm.material.color.set(0xfdd663);
            if(pm.material.emissive){{pm.material.emissive.set(0xfdd663);pm.material.emissiveIntensity=0.5;}}
            _searchMatches.push(pm);}}
        }}
    }}
    """


# ═══════════════════════════════════════
# SESSION SAVE / LOAD
# ═══════════════════════════════════════

def serialize_session():
    papers = st.session_state.get("papers", [])
    data = {
        "version": "4.0", "timestamp": datetime.now().isoformat(),
        "lang": st.session_state.get("lang", "en"),
        "papers": [{
            "id": p.id, "title": p.title, "authors": p.authors, "year": p.year,
            "cited_by_count": p.cited_by_count, "abstract": p.abstract,
            "keywords": p.keywords, "doi": p.doi, "module": p.module,
            "journal": p.journal, "mass": p.mass, "x": p.x, "y": p.y, "z": p.z,
            "radius": p.radius, "color": p.color, "is_blackhole": p.is_blackhole,
            "is_dyson": p.is_dyson, "pagerank": p.pagerank, "cluster": p.cluster,
        } for p in papers],
        "search_term": st.session_state.get("global_search", ""),
        "timeline_year": st.session_state.get("timeline_year", 2026),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)

def deserialize_session(json_str):
    from utils.data_processor import Paper
    data = json.loads(json_str)
    papers = []
    for pd_item in data.get("papers", []):
        p = Paper(**{k: v for k, v in pd_item.items() if hasattr(Paper, k)})
        papers.append(p)
    return papers, data
