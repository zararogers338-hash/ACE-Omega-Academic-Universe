"""ACE-Omega Page 12: Holographic Projection — NO matplotlib needed"""
import numpy as np, pandas as pd
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Holographic | ACE-Omega", page_icon="🌐", layout="wide")
inject_theme()
st.markdown("# Holographic Projection")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers

def gini(x):
    x=sorted(x); n=len(x)
    if n==0: return 0
    s=sum((2*i-n+1)*xi for i,xi in enumerate(x))
    return s/(n*sum(x)) if sum(x)>0 else 0

tab1,tab2,tab3 = st.tabs(["Year x Citations","Module Heatmap","Influence"])
with tab1:
    df=pd.DataFrame([{"Year":p.year,"Citations":p.cited_by_count,"Module":p.module} for p in papers])
    st.scatter_chart(df,x="Year",y="Citations",color="Module")
with tab2:
    ym={}
    for p in papers: ym[(p.year,p.module)]=ym.get((p.year,p.module),0)+1
    if ym:
        pivot=pd.DataFrame([{"Year":y,"Module":m,"Count":c} for (y,m),c in ym.items()]).pivot_table(index="Module",columns="Year",values="Count",fill_value=0)
        st.dataframe(pivot, use_container_width=True)
with tab3:
    df2=pd.DataFrame([{"PageRank":round(p.pagerank,3),"Mass":round(p.mass,1),"Module":p.module} for p in papers])
    st.scatter_chart(df2,x="PageRank",y="Mass",color="Module")

cites=[p.cited_by_count for p in papers]
c1,c2,c3=st.columns(3)
c1.metric("Median",int(np.median(cites)))
c2.metric("Gini",f"{gini(cites):.3f}")
c3.metric("Modules",len(set(p.module for p in papers)))
render_ai_analysis("Holographic Projection","2D projections of the universe.")
