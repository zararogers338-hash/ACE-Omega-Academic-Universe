"""
ACE-Omega Page 01: Universe Overview v4.0
- Global node label toggle (shows all names / hover-only)
- Enhanced star field, nebula particles
- Module connection lines
- Animated black hole accretion disks + Dyson sphere wireframe rotation
- Glow effects, improved tooltip
- Legend overlay
- Hover always shows name even with labels off
"""
import json
import streamlit as st
import streamlit.components.v1 as components
from utils.theme import inject_theme
from utils.i18n import t
from utils.data_processor import papers_to_json
from utils.components import (
    render_export_buttons, render_ai_analysis,
    three_boilerplate, three_orbit_controls, three_tooltip_code,
    three_label_system, three_enhanced_stars, three_nebula_particles,
    three_connection_lines, three_legend_html, get_search_highlight_js
)

st.set_page_config(page_title="Universe | ACE-Omega", page_icon="🌌", layout="wide")
inject_theme()
L = lambda k: t(k, st.session_state.get("lang","en"))

st.markdown("# 🌌 Universe Overview")
st.caption("Complete 3D academic celestial system · Labels · Glow · Connections")

if not st.session_state.get("data_loaded"):
    st.warning("No data loaded. Go to **Home** to upload or load demo."); st.stop()

papers = st.session_state.papers
stats = st.session_state.stats

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Papers", stats.get("total_papers",0))
c2.metric("Citations", f"{stats.get('total_citations',0):,}")
c3.metric("Years", f"{stats.get('year_min','?')}-{stats.get('year_max','?')}")
c4.metric("Black Holes", stats.get("blackholes",0))
c5.metric("Dyson", stats.get("dyson_spheres",0))

# Controls
ctrl1, ctrl2 = st.columns([1,1])
with ctrl1:
    show_labels = st.session_state.get("show_global_labels", False)
with ctrl2:
    show_connections = st.checkbox("Show connections", value=True, key="uv_conn")

search_term = st.session_state.get("global_search", "")
search_js = get_search_highlight_js(search_term)
pjson = papers_to_json(papers)
low_p = st.session_state.config.get("visualization",{}).get("low_particle_mode", False)
star_count = 4000 if low_p else 10000
neb_count = 800 if low_p else 2000
modules_dict = stats.get("modules", {})

conn_js = three_connection_lines() if show_connections else ""
legend_js = three_legend_html(modules_dict)

html = three_boilerplate(show_labels_default=show_labels) + f"""
<script>
const P={pjson};
let scene,cam,ren,paperMeshes=[],_bhRings=[],_dyWires=[];
scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x0a0a0f,.0025);
cam=new THREE.PerspectiveCamera(55,innerWidth/innerHeight,.1,2000);
cam.position.set(0,60,100);
ren=new THREE.WebGLRenderer({{antialias:true,preserveDrawingBuffer:true}});
ren.setSize(innerWidth,innerHeight);ren.setPixelRatio(Math.min(window.devicePixelRatio,2));
ren.setClearColor(0x0a0a0f);document.body.appendChild(ren.domElement);

// Lighting
scene.add(new THREE.AmbientLight(0x334466,.5));
var dl=new THREE.DirectionalLight(0xeeeeff,.35);dl.position.set(50,80,30);scene.add(dl);
var pl1=new THREE.PointLight(0x6ea8fe,.3,200);pl1.position.set(-40,40,-40);scene.add(pl1);
var pl2=new THREE.PointLight(0xf28b82,.2,150);pl2.position.set(40,20,40);scene.add(pl2);

{three_enhanced_stars(star_count)}
{three_nebula_particles(neb_count)}

// ===== PAPER CELESTIAL BODIES =====
for(var i=0;i<P.length;i++){{
    var p=P[i];
    var geo=new THREE.SphereGeometry(p.radius*0.12,p.isBlackhole?24:14,p.isBlackhole?24:14);
    var mat;
    if(p.isBlackhole){{
        mat=new THREE.MeshPhongMaterial({{color:0x080810,emissive:0x110011,emissiveIntensity:0.1,shininess:100}});
    }} else if(p.isDyson){{
        mat=new THREE.MeshPhongMaterial({{color:new THREE.Color(p.color),emissive:new THREE.Color(p.color),emissiveIntensity:0.35,shininess:60}});
    }} else {{
        mat=new THREE.MeshPhongMaterial({{color:new THREE.Color(p.color),emissive:new THREE.Color(p.color),emissiveIntensity:0.12,shininess:30}});
    }}
    var m=new THREE.Mesh(geo,mat);
    m.position.set(p.x,p.y,p.z);
    m.userData={{title:p.title,authors:p.authors,year:p.year,cited:p.cited,module:p.module,keywords:p.keywords||''}};
    scene.add(m);paperMeshes.push(m);

    // Black hole accretion disk
    if(p.isBlackhole){{
        var rg=new THREE.TorusGeometry(p.radius*0.22,0.18,8,48);
        var rm=new THREE.Mesh(rg,new THREE.MeshBasicMaterial({{color:0xff3333,transparent:true,opacity:0.45}}));
        rm.position.copy(m.position);rm.rotation.x=Math.PI/2.2;scene.add(rm);
        _bhRings.push(rm);
        // Outer glow ring
        var rg2=new THREE.TorusGeometry(p.radius*0.3,0.08,6,48);
        var rm2=new THREE.Mesh(rg2,new THREE.MeshBasicMaterial({{color:0xff6644,transparent:true,opacity:0.15}}));
        rm2.position.copy(m.position);rm2.rotation.x=Math.PI/2.5;scene.add(rm2);
        _bhRings.push(rm2);
        // Event horizon glow
        var ehGeo=new THREE.SphereGeometry(p.radius*0.14,16,16);
        var ehMat=new THREE.MeshBasicMaterial({{color:0x220022,transparent:true,opacity:0.3}});
        var eh=new THREE.Mesh(ehGeo,ehMat);eh.position.copy(m.position);scene.add(eh);
    }}

    // Dyson sphere wireframe
    if(p.isDyson){{
        var dg=new THREE.IcosahedronGeometry(p.radius*0.18,1);
        var dm=new THREE.Mesh(dg,new THREE.MeshBasicMaterial({{color:new THREE.Color(p.color),wireframe:true,transparent:true,opacity:0.25}}));
        dm.position.copy(m.position);scene.add(dm);_dyWires.push(dm);
        // Second shell
        var dg2=new THREE.IcosahedronGeometry(p.radius*0.22,0);
        var dm2=new THREE.Mesh(dg2,new THREE.MeshBasicMaterial({{color:new THREE.Color(p.color),wireframe:true,transparent:true,opacity:0.1}}));
        dm2.position.copy(m.position);scene.add(dm2);_dyWires.push(dm2);
    }}
}}

// Stats
document.getElementById('s-total').textContent=P.length;
document.getElementById('s-visible').textContent=paperMeshes.length;

{conn_js}
{search_js}
{three_label_system()}

// Create labels for all papers
for(var i=0;i<paperMeshes.length;i++){{
    createLabel(paperMeshes[i], paperMeshes[i].userData.title, paperMeshes[i].material.color?'#'+paperMeshes[i].material.color.getHexString():'#d4d4d8');
}}

{legend_js}
{three_orbit_controls()}
{three_tooltip_code()}

var _time=0;
function ani(){{
    requestAnimationFrame(ani);
    _time+=0.01;
    if(!_drag&&!_cameraLocked)_angle+=0.0015;
    cam.position.set(Math.sin(_angle)*_dist+_targetX,_height,Math.cos(_angle)*_dist+_targetZ);
    cam.lookAt(_targetX,0,_targetZ);

    // Animate black hole rings
    for(var i=0;i<_bhRings.length;i++) _bhRings[i].rotation.z+=0.008+i*0.002;
    // Animate Dyson wireframes
    for(var i=0;i<_dyWires.length;i++){{_dyWires[i].rotation.y+=0.003+i*0.001;_dyWires[i].rotation.x+=0.001;}}
    // Pulse search matches
    if(typeof _searchMatches!=='undefined'){{
        for(var i=0;i<_searchMatches.length;i++){{
            var s=1.5+Math.sin(_time*3+i)*0.15;
            _searchMatches[i].scale.set(s,s,s);
        }}
    }}

    updateLabels();
    ren.render(scene,cam);
}}
ani();
</script></body></html>"""

components.html(html, height=680, scrolling=False)
render_export_buttons()

render_ai_analysis("Universe Overview", f"{stats.get('total_papers',0)} papers visualized in 3D. {stats.get('blackholes',0)} black holes, {stats.get('dyson_spheres',0)} Dyson spheres.")
