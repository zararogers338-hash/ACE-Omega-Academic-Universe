"""ACE-Omega Page 04: Satellite Rings"""
import json
import streamlit as st
import streamlit.components.v1 as components
from utils.theme import inject_theme
from utils.data_processor import papers_to_json
from utils.components import render_export_buttons, render_ai_analysis, three_boilerplate, three_orbit_controls, three_tooltip_code, three_label_system, three_enhanced_stars

st.set_page_config(page_title="Satellite Rings | ACE-Omega", page_icon="◎", layout="wide")
inject_theme()

st.markdown("# Satellite Rings")
st.caption("Core papers surrounded by orbiting follow-up works.")

if not st.session_state.get("data_loaded"):
    st.warning("No data. Go to **Home** to load."); st.stop()

papers = st.session_state.papers
cores = sorted([p for p in papers if p.cited_by_count > 50], key=lambda x: -x.cited_by_count)[:15]

if not cores:
    st.info("No core papers (need citations > 50)."); st.stop()

systems = []
for core in cores:
    sats = [p for p in papers if p.id != core.id and p.module == core.module
            and 0 <= p.year - core.year <= 5 and p.cited_by_count < core.cited_by_count][:12]
    systems.append({"core": core, "sats": sats})

sys_data = json.dumps([{
    "core": {"title": s["core"].title[:50], "radius": s["core"].radius, "color": s["core"].color, "cited": s["core"].cited_by_count},
    "sats": [{"title": sat.title[:40], "radius": sat.radius, "color": sat.color, "cited": sat.cited_by_count} for sat in s["sats"]]
} for s in systems], ensure_ascii=False)

html = three_boilerplate(show_labels_default=st.session_state.get("show_global_labels", False)) + """
<script>
const SYS=""" + sys_data + """;
let scene,cam,ren,paperMeshes=[],satMeshes=[];
scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x0a0a0f,.002);
cam=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.1,2000);
ren=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
ren.setSize(innerWidth,innerHeight);ren.setClearColor(0x0a0a0f);
document.body.appendChild(ren.domElement);
scene.add(new THREE.AmbientLight(0x334466,.5));
scene.add(new THREE.DirectionalLight(0xeeeeff,.3));

var cols=Math.ceil(Math.sqrt(SYS.length));
for(var si=0;si<SYS.length;si++){
    var s=SYS[si],ox=(si%cols-cols/2)*40,oz=(Math.floor(si/cols)-Math.floor(SYS.length/cols)/2)*40;
    var cg=new THREE.SphereGeometry(s.core.radius*0.15,20,20);
    var cm=new THREE.Mesh(cg,new THREE.MeshPhongMaterial({color:new THREE.Color(s.core.color),emissive:new THREE.Color(s.core.color),emissiveIntensity:0.2}));
    cm.position.set(ox,0,oz);cm.userData={title:s.core.title,authors:'Core',year:0,cited:s.core.cited,module:'Core'};
    scene.add(cm);paperMeshes.push(cm);
    var ring=new THREE.TorusGeometry(s.core.radius*0.35,0.05,8,64);
    var rm=new THREE.Mesh(ring,new THREE.MeshBasicMaterial({color:new THREE.Color(s.core.color),transparent:true,opacity:0.2}));
    rm.position.set(ox,0,oz);rm.rotation.x=Math.PI/2;scene.add(rm);
    for(var j=0;j<s.sats.length;j++){
        var sat=s.sats[j],angle=j/s.sats.length*Math.PI*2,r=s.core.radius*0.35;
        var sg2=new THREE.SphereGeometry(sat.radius*0.06,8,8);
        var sm=new THREE.Mesh(sg2,new THREE.MeshPhongMaterial({color:new THREE.Color(sat.color)}));
        sm.position.set(ox+Math.cos(angle)*r,0,oz+Math.sin(angle)*r);
        sm.userData={title:sat.title,authors:'Satellite',year:0,cited:sat.cited,module:'Sat'};
        sm._oc=new THREE.Vector3(ox,0,oz);sm._or=r;sm._oa=angle;sm._os=0.3+Math.random()*0.3;
        scene.add(sm);paperMeshes.push(sm);satMeshes.push(sm);
    }
}
""" + three_orbit_controls() + three_tooltip_code() + three_label_system() + """
// Create labels for core papers
for(var i=0;i<paperMeshes.length;i++){
    createLabel(paperMeshes[i], paperMeshes[i].userData.title, '#d4d4d8');
}
document.getElementById('s-total').textContent=SYS.length;
document.getElementById('s-visible').textContent=paperMeshes.length;
_dist=80;_height=50;
function ani(){requestAnimationFrame(ani);
    var t=Date.now()*0.001;
    for(var s of satMeshes){s._oa+=s._os*0.01;s.position.x=s._oc.x+Math.cos(s._oa)*s._or;s.position.z=s._oc.z+Math.sin(s._oa)*s._or;}
    if(!_drag&&!_cameraLocked)_angle+=0.002;
    cam.position.set(Math.sin(_angle)*_dist,_height,Math.cos(_angle)*_dist);cam.lookAt(0,0,0);
    updateLabels();
    ren.render(scene,cam);
}ani();
</script></body></html>"""

components.html(html, height=620, scrolling=False)
render_export_buttons()

for i, s in enumerate(systems):
    with st.expander(f"{s['core'].title[:60]} ({s['core'].cited_by_count} cites, {len(s['sats'])} satellites)"):
        for sat in s['sats']:
            st.markdown(f"- **{sat.title[:60]}** — {sat.year}, {sat.cited_by_count} cites")

render_ai_analysis("Satellite Rings", f"{len(systems)} core papers with satellite clusters.")
