import streamlit as st

from utils.database import init_database
from utils.ui import apply_global_styles, sidebar_navigation
from views.dashboard import render as render_dashboard
from views.kanban import render as render_kanban
from views.pdi import render as render_pdi
from views.projeto_detail import render as render_projeto_detail
from views.projetos import render as render_projetos
from views.pdi_detail import render as render_pdi_detail
from views.tarefa_detail import render as render_tarefa_detail

st.set_page_config(
    page_title="Development Hub",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_database()
apply_global_styles()

active_view = sidebar_navigation()
detail_view = st.session_state.get("detail_view")
detail_id = st.session_state.get("detail_id")

if detail_view == "tarefa" and detail_id:
    render_tarefa_detail(detail_id)
elif detail_view == "projeto" and detail_id:
    render_projeto_detail(detail_id)
elif detail_view == "pdi" and detail_id:
    render_pdi_detail(detail_id)
elif active_view == "Dashboard":
    render_dashboard()
elif active_view == "Kanban":
    render_kanban()
elif active_view == "Projetos":
    render_projetos()
else:
    render_pdi()
