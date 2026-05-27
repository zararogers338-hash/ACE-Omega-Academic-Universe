"""ACE-Omega Page 05: Asteroid Belt"""
import re, json, math, random
from collections import Counter
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from utils.theme import inject_theme
from utils.components import render_export_buttons, render_ai_analysis, three_boilerplate, three_orbit_controls, three_enhanced_stars

st.set_page_config(page_title="Asteroid Belt | ACE-Omega", page_icon="✦", layout="wide")
inject_theme()

st.markdown("# Asteroid Belt")
st.caption("Fragmented keywords, weak-citation long-tail papers.")

if not st.session_state.get("data_loaded"):
    st.warning("No data. Go to **Home** to load."); st.stop()

papers = st.session_state.papers
all_kw = []
for p in papers:
    if p.keywords:
        for kw in re.split(r'[,;|/]', p.keywords):
            kw = kw.strip().lower()
            if len(kw) > 2: all_kw.append(kw)

kw_counts = Counter(all_kw)
top_kw = kw_counts.most_common(30)
long_tail = [p for p in papers if p.cited_by_count < 5]

st.markdown(f"**{len(top_kw)}** keywords | **{len(long_tail)}** long-tail papers")

asteroids = []
for i, (kw, cnt) in enumerate(top_kw):
    angle = i / max(len(top_kw),1) * math.pi * 2
    r = 20 + cnt * 0.5
    asteroids.append({"label": kw, "count": cnt, "x": math.cos(angle)*r, "y": random.gauss(0,3), "z": math.sin(angle)*r})

for p in long_tail[:150]:
    asteroids.append({"label": p.title[:30], "count": p.cited_by_count, "x": p.x*0.5, "y": random.gauss(0,6), "z": p.z*0.5})

adata = json.dumps(asteroids, ensure_ascii=False)
low_p = st.session_state.config.get("visualization",{}).get("low_particle_mode", False)
pcount = 2000 if low_p else 6000

html = three_boilerplate(show_labels_default=st.session_state.get("show_global_labels", False)) + f"""
<script>
const A={adata};
let scene,cam,ren;
scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x0a0a0f,.005);
cam=new THREE.PerspectiveCamera(55,innerWidth/innerHeight,.1,1000);
ren=new THREE.WebGLRenderer({{antialias:true,preserveDrawingBuffer:true}});
ren.setSize(innerWidth,innerHeight);ren.setClearColor(0x0a0a0f);
document.body.appendChild(ren.domElement);
scene.add(new THREE.AmbientLight(0x334466,.5));
scene.add(new THREE.DirectionalLight(0xeeeeff,.3));

var dg=new THREE.BufferGeometry(),dp=new Float32Array({pcount}*3);
for(var i=0;i<{pcount}*3;i++)dp[i]=(Math.random()-0.5)*120;
dg.setAttribute('position',new THREE.BufferAttribute(dp,3));
scene.add(new THREE.Points(dg,new THREE.PointsMaterial({{color:0x555566,size:0.2}})));

for(var a of A){{
    var sz=Math.max(0.3,Math.log(1+a.count)*0.5);
    var g=new THREE.DodecahedronGeometry(sz,0);
    var c=a.count>10?0x6ea8fe:a.count>3?0x75d9a0:0x555566;
    var m=new THREE.Mesh(g,new THREE.MeshPhongMaterial({{color:c,flatShading:true}}));
    m.position.set(a.x,a.y,a.z);m.rotation.set(Math.random()*6,Math.random()*6,Math.random()*6);
    scene.add(m);
}}

{three_orbit_controls()}
_dist=60;_height=20;

function ani(){{requestAnimationFrame(ani);
if(!_drag&&!_cameraLocked)_angle+=0.002;
cam.position.set(Math.sin(_angle)*_dist,_height,Math.cos(_angle)*_dist);cam.lookAt(0,0,0);
ren.render(scene,cam);}}ani();
</script></body></html>"""

components.html(html, height=550, scrolling=False)
render_export_buttons()

st.markdown("---")
if top_kw:
    st.markdown("### Top Keywords")
    kw_df = pd.DataFrame(top_kw, columns=["Keyword", "Count"])
    st.bar_chart(kw_df.set_index("Keyword")["Count"])

render_ai_analysis("Asteroid Belt", f"{len(top_kw)} keywords, {len(long_tail)} long-tail papers.")
