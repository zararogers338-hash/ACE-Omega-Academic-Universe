"""
ACE-Omega Page 03: Gravity Grid v4.0
Enhanced with labels, nebula, better colors.
"""
import json
import streamlit as st
import streamlit.components.v1 as components
from utils.theme import inject_theme
from utils.data_processor import papers_to_json
from utils.components import (
    render_export_buttons, render_ai_analysis,
    three_boilerplate, three_orbit_controls, three_tooltip_code,
    three_label_system, three_enhanced_stars, get_search_highlight_js
)

st.set_page_config(page_title="Gravity Grid | ACE-Omega", page_icon="▦", layout="wide")
inject_theme()

st.markdown("# ▦ Gravity Grid — Spacetime Warp")
st.caption("Knowledge propagation bends around high-influence papers like spacetime around mass.")

if not st.session_state.get("data_loaded"):
    st.warning("No data. Go to **Home** to load."); st.stop()

papers = st.session_state.papers
search_term = st.session_state.get("global_search", "")
show_labels = st.session_state.get("show_global_labels", False)

gc1, gc2, gc3 = st.columns(3)
with gc1:
    warp_k = st.slider("Warp strength", 0.5, 5.0, 2.0, 0.1, key="gw_k")
with gc2:
    grid_seg = st.slider("Grid resolution", 20, 120, 60, 10, key="gw_seg")
with gc3:
    exponent = st.slider("Falloff", 1.0, 3.0, 1.8, 0.1, key="gw_exp")

pjson = papers_to_json(papers)

html = three_boilerplate(show_labels_default=show_labels) + f"""
<script>
const P={pjson},K={warp_k},SEG={grid_seg},EXP={exponent};
let scene,cam,ren,paperMeshes=[];
scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x0a0a0f,.003);
cam=new THREE.PerspectiveCamera(55,innerWidth/innerHeight,.1,1000);
cam.position.set(0,55,85);
ren=new THREE.WebGLRenderer({{antialias:true,preserveDrawingBuffer:true}});
ren.setSize(innerWidth,innerHeight);ren.setPixelRatio(Math.min(window.devicePixelRatio,2));
ren.setClearColor(0x0a0a0f);document.body.appendChild(ren.domElement);
scene.add(new THREE.AmbientLight(0x334466,.5));
scene.add(new THREE.DirectionalLight(0xeeeeff,.3));

{three_enhanced_stars(6000)}

var gridSize=140,half=gridSize/2,step=gridSize/SEG;

function warpY(gx,gz){{
    var dy=0;
    for(var j=0;j<P.length;j++){{
        var ddx=gx-P[j].x,ddz=gz-P[j].z,d=Math.sqrt(ddx*ddx+ddz*ddz)+0.1;
        dy-=(P[j].mass*K)/Math.pow(d,EXP);
    }}
    return Math.max(dy,-35);
}}

// Grid lines
var lp=[],lc=[];
for(var iz=0;iz<=SEG;iz++){{
    var gz=-half+iz*step;
    for(var ix=0;ix<SEG;ix++){{
        var gx1=-half+ix*step,gx2=-half+(ix+1)*step;
        var y1=warpY(gx1,gz),y2=warpY(gx2,gz);
        lp.push(gx1,y1,gz,gx2,y2,gz);
        var t1=Math.min(1,Math.abs(y1)/15),t2=Math.min(1,Math.abs(y2)/15);
        lc.push(0.1+t1*0.9,0.3*(1-t1),0.8*(1-t1)+t1*0.1, 0.1+t2*0.9,0.3*(1-t2),0.8*(1-t2)+t2*0.1);
    }}
}}
for(var ix=0;ix<=SEG;ix++){{
    var gx=-half+ix*step;
    for(var iz=0;iz<SEG;iz++){{
        var gz1=-half+iz*step,gz2=-half+(iz+1)*step;
        var y1=warpY(gx,gz1),y2=warpY(gx,gz2);
        lp.push(gx,y1,gz1,gx,y2,gz2);
        var t1=Math.min(1,Math.abs(y1)/15),t2=Math.min(1,Math.abs(y2)/15);
        lc.push(0.1+t1*0.9,0.3*(1-t1),0.8*(1-t1)+t1*0.1, 0.1+t2*0.9,0.3*(1-t2),0.8*(1-t2)+t2*0.1);
    }}
}}
var lg=new THREE.BufferGeometry();
lg.setAttribute('position',new THREE.Float32BufferAttribute(lp,3));
lg.setAttribute('color',new THREE.Float32BufferAttribute(lc,3));
scene.add(new THREE.LineSegments(lg,new THREE.LineBasicMaterial({{vertexColors:true,transparent:true,opacity:0.7}})));

// Paper bodies on the grid
for(var p of P){{
    var sy=warpY(p.x,p.z)+p.radius*0.12+0.5;
    var geo=new THREE.SphereGeometry(p.radius*0.1,p.isBlackhole?20:10,10);
    var mat;
    if(p.isBlackhole) mat=new THREE.MeshBasicMaterial({{color:0x111111}});
    else mat=new THREE.MeshPhongMaterial({{color:new THREE.Color(p.color),emissive:new THREE.Color(p.color),emissiveIntensity:0.15}});
    var m=new THREE.Mesh(geo,mat);
    m.position.set(p.x,sy,p.z);
    m.userData={{title:p.title,authors:p.authors,year:p.year,cited:p.cited,module:p.module,keywords:p.keywords||''}};
    scene.add(m);paperMeshes.push(m);
    if(p.mass>3){{
        var gy=warpY(p.x,p.z);
        var wlg=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(p.x,sy,p.z),new THREE.Vector3(p.x,gy,p.z)]);
        scene.add(new THREE.Line(wlg,new THREE.LineBasicMaterial({{color:new THREE.Color(p.color),transparent:true,opacity:0.25}})));
    }}
}}

document.getElementById('s-total').textContent=P.length;
document.getElementById('s-visible').textContent=paperMeshes.length;

{get_search_highlight_js(search_term)}
{three_label_system()}
for(var i=0;i<paperMeshes.length;i++){{
    createLabel(paperMeshes[i], paperMeshes[i].userData.title, '#d4d4d8');
}}
{three_orbit_controls()}
{three_tooltip_code()}
_height=55;

function ani(){{
    requestAnimationFrame(ani);
    if(!_drag&&!_cameraLocked)_angle+=0.002;
    cam.position.set(Math.sin(_angle)*_dist,_height,Math.cos(_angle)*_dist);
    cam.lookAt(0,0,0);
    updateLabels();
    ren.render(scene,cam);
}}
ani();
</script></body></html>"""

components.html(html, height=640, scrolling=False)
render_export_buttons()

st.markdown("""
**Vertex displacement:** `dz = -Sum(mass_i * k) / (dist_i + 0.1)^exponent`
Color: **blue** (flat) to **red** (deep warp).
""")

render_ai_analysis("Gravity Grid", f"Gravity grid with {len(papers)} papers. Warp={warp_k}, Segments={grid_seg}.")
