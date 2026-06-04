import streamlit as st
import httpx
import asyncio
import html
import os
import pandas as pd
import plotly.graph_objects as go

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")

INVENTORY_RENAME = {"id": "ID", "product": "Product", "quantity": "Quantity"}
SHIPMENT_RENAME = {
    "id": "ID",
    "product": "Product",
    "quantity": "Quantity",
    "destination": "Destination",
    "status": "Status",
}
SHIPMENT_COL_ORDER = ["ID", "Product", "Quantity", "Destination", "Status"]
INVENTORY_COL_ORDER = ["ID", "Product", "Quantity"]
STATUS_COLORS = {"In Transit": "#4b9cf5", "Delivered": "#34d47a"}
STATUS_ORDER = ["In Transit", "Delivered"]

st.set_page_config(
    page_title="SmartAgro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: #0b0e14 !important;
    color: #dde3ec !important;
}
.stApp { background-color: #0b0e14 !important; }
.main .block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1380px !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0f1319 !important;
    border-right: 1px solid #1c2333 !important;
    min-width: 220px !important; max-width: 220px !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

div[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #111827 !important; border: 1px solid #1c2333 !important;
    border-radius: 6px !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important; color: #dde3ec !important;
}
div[data-testid="stSidebar"] [data-testid="stSelectbox"] label { display: none !important; }

h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important; font-size: 1.75rem !important;
    color: #dde3ec !important; letter-spacing: -0.02em !important; margin-bottom: 0.1rem !important;
}

.slabel {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase;
    color: #2d3a50; padding-bottom: 8px; border-bottom: 1px solid #1c2333;
    margin-top: 1.8rem; margin-bottom: 1.2rem;
}

/* All buttons — default green */
.stButton button {
    background: #34d47a !important; color: #050709 !important;
    border: none !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important; letter-spacing: 0.08em !important;
    font-weight: 500 !important; border-radius: 6px !important;
    padding: 0.45rem 1.1rem !important;
}
.stButton button:hover { opacity: 0.82 !important; }

/* Example query buttons — outlined ghost style */
div[data-testid="column"] .stButton button.ex-btn {
    background: transparent !important;
    border: 1px solid #1c2333 !important;
    color: #4a5a72 !important;
    font-size: 11px !important;
    padding: 0.4rem 0.7rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    width: 100% !important;
}

/* Forms */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #111827 !important; border: 1px solid #1c2333 !important;
    color: #dde3ec !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important; border-radius: 6px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #34d47a !important; box-shadow: 0 0 0 2px rgba(52,212,122,0.1) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 0.1em !important; color: #4a5a72 !important; text-transform: uppercase !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] { border: 1px solid #1c2333 !important; border-radius: 8px !important; overflow: hidden !important; }
div[data-testid="stDataFrame"] th {
    background: #111827 !important; color: #2d3a50 !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important; text-align: left !important;
}
div[data-testid="stDataFrame"] td {
    font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
    color: #8a9ab2 !important; text-align: left !important;
}
div[data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
    --gdg-text-header-align: left !important;
}
div[data-testid="stDataFrame"] [role="gridcell"],
div[data-testid="stDataFrame"] [class*="gdg-header"] {
    text-align: left !important;
    justify-content: flex-start !important;
}

.stAlert { border-radius: 6px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }
.stSpinner > div { border-top-color: #34d47a !important; }
</style>
""", unsafe_allow_html=True)


def plot_layout(h=230):
    return dict(
        paper_bgcolor="#0f1319", plot_bgcolor="#0b0e14",
        font=dict(family="JetBrains Mono, monospace", color="#4a5a72", size=11),
        margin=dict(l=6, r=6, t=20, b=6),
        xaxis=dict(gridcolor="#1c2333", linecolor="#1c2333", tickcolor="#1c2333", title=""),
        yaxis=dict(gridcolor="#1c2333", linecolor="#1c2333", title="", visible=False),
        showlegend=False, height=h,
    )

PALETTE = ["#34d47a", "#4b9cf5", "#f5a623", "#c084fc", "#f87171"]


# ── API ────────────────────────────────────────────────────────────────────────
async def _get(path):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE_URL}{path}"); r.raise_for_status(); return r.json()

async def _post(path, data):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(f"{BASE_URL}{path}", json=data); r.raise_for_status(); return r.json()

async def _post_params(path, params):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_URL}{path}", params=params); r.raise_for_status(); return r.json()

async def _patch(path):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.patch(f"{BASE_URL}{path}"); r.raise_for_status(); return r.json()

def run(coro): return asyncio.run(coro)


def esc(text):
    return html.escape(str(text))


def sort_by_id(df):
    """Sort rows by ID ascending (1, 2, 3, …)."""
    if df.empty or "ID" not in df.columns:
        return df
    return (
        df.assign(_id_num=pd.to_numeric(df["ID"], errors="coerce"))
        .sort_values("_id_num", ascending=True, kind="stable")
        .drop(columns="_id_num")
        .reset_index(drop=True)
    )


def df_inventory(records):
    df = pd.DataFrame(records)
    if df.empty:
        return df
    df = df.rename(columns={k: v for k, v in INVENTORY_RENAME.items() if k in df.columns})
    cols = [c for c in INVENTORY_COL_ORDER if c in df.columns]
    return sort_by_id(df[cols])


def df_shipments(records):
    df = pd.DataFrame(records)
    if df.empty:
        return df
    df = df.rename(columns={k: v for k, v in SHIPMENT_RENAME.items() if k in df.columns})
    cols = [c for c in SHIPMENT_COL_ORDER if c in df.columns]
    return sort_by_id(df[cols])


def is_shipment_records(records):
    if not records:
        return False
    sample = records[0]
    return isinstance(sample, dict) and (
        "destination" in sample or "status" in sample
    )


def df_ai_result(records):
    df = pd.DataFrame(records)
    if df.empty:
        return df
    if is_shipment_records(records):
        mapping = SHIPMENT_RENAME
        order = SHIPMENT_COL_ORDER
    else:
        mapping = INVENTORY_RENAME
        order = INVENTORY_COL_ORDER
    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
    cols = [c for c in order if c in df.columns]
    df = df[cols]
    df = sort_by_id(df)
    if "Quantity" in df.columns:
        df = df.copy()
        df["Quantity"] = df["Quantity"].apply(
            lambda x: f"{x} tons" if not isinstance(x, str) or not str(x).endswith("tons") else x
        )
    return df


def pie_status_chart(df_s, center_text):
    counts = df_s["status"].value_counts()
    labels, values, colors = [], [], []
    for i, status in enumerate(STATUS_ORDER):
        if status in counts.index:
            labels.append(status)
            values.append(int(counts[status]))
            colors.append(STATUS_COLORS.get(status, PALETTE[i]))
    for status in counts.index:
        if status not in labels:
            labels.append(status)
            values.append(int(counts[status]))
            colors.append(STATUS_COLORS.get(status, PALETTE[len(colors) % len(PALETTE)]))
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68,
        marker=dict(colors=colors, line=dict(color="#0b0e14", width=3)),
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=10, family="JetBrains Mono, monospace", color="#0b0e14"),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#0f1319", height=220,
        font=dict(family="JetBrains Mono, monospace", color="#4a5a72", size=10),
        margin=dict(l=6, r=6, t=20, b=40),
        showlegend=True,
        legend=dict(
            orientation="h", y=-0.15, x=0.5, xanchor="center",
            font=dict(family="JetBrains Mono, monospace", size=10, color="#4a5a72"),
            bgcolor="rgba(0,0,0,0)",
        ),
        annotations=[dict(
            text=f"<b>{center_text}</b>", x=0.5, y=0.5,
            font=dict(size=26, color="#dde3ec", family="Space Grotesk, sans-serif"),
            showarrow=False,
        )],
    )
    return fig


def _supports_column_alignment():
    try:
        st.column_config.TextColumn("_", alignment="left")
        return True
    except TypeError:
        return False


def build_column_config(df):
    """Left-align every column (numeric ID defaults to right otherwise)."""
    align_kw = {"alignment": "left"} if _supports_column_alignment() else {}
    cfg = {}
    for col in df.columns:
        series = df[col]
        if col == "ID" or (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_float_dtype(series)
        ):
            cfg[col] = st.column_config.NumberColumn(
                col, format="%d", width="small", **align_kw
            )
        elif pd.api.types.is_numeric_dtype(series):
            cfg[col] = st.column_config.NumberColumn(col, **align_kw)
        else:
            cfg[col] = st.column_config.TextColumn(col, **align_kw)
    return cfg


def show_data_table(df, column_order=None):
    display = df.copy()
    if "ID" in display.columns and not _supports_column_alignment():
        display["ID"] = display["ID"].apply(
            lambda x: str(int(x)) if pd.notna(x) else ""
        )

    kwargs = dict(
        use_container_width=True,
        hide_index=True,
        column_config=build_column_config(display),
    )
    if column_order:
        cols = [c for c in column_order if c in display.columns]
        if cols:
            kwargs["column_order"] = cols
    st.dataframe(display, **kwargs)


def render_ai_response(res):
    if "status" in res:
        ai_box(res.get("message", ""), "success" if res["status"] == "success" else "error")
    elif "reply" in res:
        ai_box(res["reply"], "info")
    elif isinstance(res, list):
        df_ai = df_ai_result(res)
        sec("Result")
        order = SHIPMENT_COL_ORDER if is_shipment_records(res) else INVENTORY_COL_ORDER
        show_data_table(df_ai, order)
    else:
        ai_box(str(res), "info")


def kpi(label, value, sub, accent):
    return f"""
    <div style="background:#0f1319;border:1px solid #1c2333;border-radius:8px;
                padding:18px 20px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{accent};"></div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.18em;
                  text-transform:uppercase;color:#2d3a50;margin-bottom:10px;">{label}</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
                  color:{accent};line-height:1;margin-bottom:6px;">{value}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#2d3a50;">{sub}</div>
    </div>"""

def sec(text):
    st.markdown(f'<div class="slabel">{text}</div>', unsafe_allow_html=True)

def ai_box(msg, kind="info"):
    colors = {"success": "#34d47a", "error": "#f87171", "info": "#4b9cf5"}
    c = colors.get(kind, colors["info"])
    icon = "✓" if kind == "success" else ("✗" if kind == "error" else "◈")
    st.markdown(f"""
    <div style="background:#0f1319;border:1px solid #1c2333;border-left:3px solid {c};
                border-radius:8px;padding:14px 18px;margin-top:12px;
                font-family:'JetBrains Mono',monospace;font-size:13px;
                color:#8a9ab2;line-height:1.7;">
      <span style="color:{c};margin-right:8px;">{icon}</span>{msg}
    </div>""", unsafe_allow_html=True)

def status_badge(s):
    if s == "Delivered":
        return f'<span style="background:#0d2a1f;color:#34d47a;padding:2px 10px;border-radius:20px;font-family:JetBrains Mono,monospace;font-size:11px;">{s}</span>'
    return f'<span style="background:#0d1f3a;color:#4b9cf5;padding:2px 10px;border-radius:20px;font-family:JetBrains Mono,monospace;font-size:11px;">{s}</span>'

with st.sidebar:
    st.markdown("""
    <div style="padding:28px 20px 22px;border-bottom:1px solid #1c2333;margin-bottom:10px;">
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:20px;
                  color:#34d47a;letter-spacing:-0.02em;">SmartAgro</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.18em;
                  text-transform:uppercase;color:#2d3a50;margin-top:5px;">Supply Chain AI</div>
    </div>
    """, unsafe_allow_html=True)

    NAV = {"Dashboard": "▦", "Inventory": "◫", "Shipments": "◎", "AI Assistant": "◇"}
    page = st.selectbox(
        "Navigation",
        list(NAV.keys()),
        format_func=lambda x: f"{NAV[x]}  {x}",
        label_visibility="collapsed",
        key="main_nav",
    )

if page == "Dashboard":
    st.markdown("# Dashboard")
    st.markdown('<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#2d3a50;margin-bottom:1.8rem;">Real-time warehouse & logistics overview</p>', unsafe_allow_html=True)

    try:
        inventory = run(_get("/inventory/"))
        shipments = run(_get("/shipments/"))
    except Exception as e:
        st.error(f"Backend connection failed: {e}"); st.stop()

    n_prod      = len(inventory)
    n_stock     = sum(i["quantity"] for i in inventory)
    n_ship      = len(shipments)
    n_transit   = sum(1 for s in shipments if s.get("status") == "In Transit")
    n_delivered = sum(1 for s in shipments if s.get("status") == "Delivered")

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1: st.markdown(kpi("Product Types", n_prod,    "SKUs in warehouse",        "#34d47a"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Total Stock",   f"{n_stock:,}", "units on hand",        "#4b9cf5"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Shipments",     n_ship,    f"{n_delivered} delivered",  "#f5a623"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("In Transit",    n_transit, "active deliveries",         "#c084fc"), unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        sec("Stock Levels")
        if inventory:
            df = pd.DataFrame(inventory)
            fig = go.Figure(go.Bar(
                x=df["product"], y=df["quantity"],
                marker=dict(color="#34d47a", opacity=0.85, cornerradius=4),
                text=[f"{q} t" for q in df["quantity"]],
                textposition="outside",
                textfont=dict(size=11, color="#4a5a72"),
            ))
            fig.update_layout(**plot_layout(220))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No products in stock.")

    with col_r:
        sec("Shipment Status")
        if shipments:
            df_s = pd.DataFrame(shipments)
            fig2 = pie_status_chart(df_s, n_ship)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No shipments yet.")

    sec("Recent Shipments")
    if shipments:
        df_r = df_shipments(shipments)
        if len(df_r) > 10:
            df_r = df_r.iloc[-10:]
        df_r = df_r.copy()
        df_r["Quantity"] = df_r["Quantity"].apply(lambda x: f"{x} tons")
        show_data_table(df_r, SHIPMENT_COL_ORDER)
    else:
        st.info("No shipments found.")

elif page == "Inventory":
    st.markdown("# Inventory")
    st.markdown('<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#2d3a50;margin-bottom:1.8rem;">Warehouse stock management</p>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        sec("Current Stock")
        if st.button("↻  Refresh"): st.rerun()
        try:
            inventory = run(_get("/inventory/"))
            if inventory:
                df = df_inventory(inventory)
                fig = go.Figure(go.Bar(
                    x=df["Product"], y=df["Quantity"],
                    marker=dict(color=df["Quantity"].tolist(),
                                colorscale=[[0, "#0d2a1f"], [1, "#34d47a"]],
                                showscale=False, cornerradius=4),
                    text=[f"{q} tons" for q in df["Quantity"]],
                    textposition="outside",
                    textfont=dict(size=11, color="#4a5a72"),
                ))
                fig.update_layout(**plot_layout(220))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                df_d = df.copy()
                df_d["Quantity"] = df_d["Quantity"].apply(lambda x: f"{x} tons")
                show_data_table(df_d, INVENTORY_COL_ORDER)
            else:
                st.info("No products in stock.")
        except Exception as e:
            st.error(f"Error: {e}")

    with col_r:
        sec("Add to Stock")
        with st.form("inv_form", clear_on_submit=True):
            p_name = st.text_input("Product Name", placeholder="e.g. wheat")
            p_qty  = st.number_input("Quantity (tons)", min_value=1, step=1, value=100)
            if st.form_submit_button("Add to Stock"):
                if not p_name.strip():
                    st.warning("Product name cannot be empty.")
                else:
                    try:
                        r = run(_post("/inventory/", {"product_name": p_name.strip(), "quantity": int(p_qty)}))
                        if r.get("status") == "success":
                            ai_box(r.get("message", "Added."), "success"); st.rerun()
                        else:
                            ai_box(r.get("message", "Error."), "error")
                    except Exception as e:
                        st.error(f"API error: {e}")

        st.markdown("""
        <div style="margin-top:1.4rem;padding:14px 16px;background:#0f1319;border:1px solid #1c2333;
                    border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:11px;
                    color:#2d3a50;line-height:2.2;">
          All quantities in <span style="color:#34d47a;">tons</span>.<br>
          Adding an existing product increases its stock.<br>
          New products are created automatically.
        </div>""", unsafe_allow_html=True)

elif page == "Shipments":
    st.markdown("# Shipments")
    st.markdown('<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#2d3a50;margin-bottom:1.8rem;">Create and track outbound shipments</p>', unsafe_allow_html=True)

    col_f, col_l = st.columns([2, 3], gap="large")

    with col_f:
        sec("New Shipment")
        with st.form("ship_form", clear_on_submit=True):
            s_prod = st.text_input("Product Name", placeholder="e.g. wheat")
            s_qty  = st.number_input("Quantity (tons)", min_value=1, step=1, value=50)
            s_dest = st.text_input("Destination", placeholder="e.g. Baku")
            if st.form_submit_button("Create Shipment"):
                if not s_prod.strip() or not s_dest.strip():
                    st.warning("Please fill in all fields.")
                else:
                    try:
                        r = run(_post("/shipment/", {
                            "product_name": s_prod.strip(),
                            "quantity": int(s_qty),
                            "destination": s_dest.strip()
                        }))
                        if r.get("status") == "success":
                            ai_box(r.get("message", "Shipment created."), "success"); st.rerun()
                        else:
                            ai_box(r.get("message", "Insufficient stock or product not found."), "error")
                    except Exception as e:
                        st.error(f"API error: {e}")

        st.markdown("""
        <div style="margin-top:1.4rem;padding:14px 16px;background:#0f1319;border:1px solid #1c2333;
                    border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:11px;
                    color:#2d3a50;line-height:2.2;">
          Quantity in <span style="color:#34d47a;">tons</span>.<br>
          Stock deducted automatically.<br>
          Default status: <span style="color:#4b9cf5;">In Transit</span>.
        </div>""", unsafe_allow_html=True)

    with col_l:
        sec("All Shipments")
        if st.button("↻  Refresh"): st.rerun()

        try:
            shipments = run(_get("/shipments/"))
            if shipments:
                df_s = df_shipments(shipments)

                dc = df_s["Destination"].value_counts().reset_index()
                dc.columns = ["Destination", "Count"]
                fig3 = go.Figure(go.Bar(
                    x=dc["Destination"], y=dc["Count"],
                    marker=dict(color="#4b9cf5", opacity=0.85, cornerradius=4),
                    text=dc["Count"], textposition="outside",
                    textfont=dict(size=11, color="#4a5a72"),
                ))
                fig3.update_layout(**plot_layout(180))
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

                sec("Shipment List")
                df_show = df_s
                df_table = df_show.copy()
                df_table["Quantity"] = df_table["Quantity"].apply(lambda x: f"{x} tons")
                show_data_table(df_table, SHIPMENT_COL_ORDER)

                in_transit = df_show[df_show["Status"] == "In Transit"]
                if not in_transit.empty:
                    sec("Mark Delivered")
                    options = {
                        int(r["ID"]): f"#{int(r['ID'])} · {r['Product']} → {r['Destination']} ({r['Quantity']} t)"
                        for _, r in in_transit.iterrows()
                    }
                    pick = st.selectbox(
                        "Shipment",
                        options=sorted(options.keys()),
                        format_func=lambda sid: options[sid],
                        label_visibility="collapsed",
                        key="deliver_pick",
                    )
                    if st.button("✓ Mark as Delivered", key="deliver_submit"):
                        try:
                            result = run(_patch(f"/shipment/{pick}/deliver"))
                            if result.get("status") == "success":
                                st.success(result.get("message", f"Shipment #{pick} delivered."))
                                st.rerun()
                            else:
                                st.error(result.get("message", "Error updating status."))
                        except Exception as e:
                            st.error(f"API error: {e}")
            else:
                st.info("No shipments yet.")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "AI Assistant":
    if st.session_state.pop("_clear_ai_query", False):
        st.session_state.pop("ai_query_input", None)
    if "ai_query_prefill" in st.session_state:
        st.session_state["ai_query_input"] = st.session_state.pop("ai_query_prefill")

    pending_result = st.session_state.pop("ai_pending_result", None)

    st.markdown("# AI Assistant")
    st.markdown('<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#2d3a50;margin-bottom:1.8rem;">LLaMA 3.3 · Groq · Tool Calling — natural language warehouse control</p>', unsafe_allow_html=True)

    sec("Query")

    EXAMPLES = [
        ("Check stock",        "What products are in the warehouse?"),
        ("Send wheat → Baku",  "Send 50 tons wheat to Baku"),
        ("All shipments",      "Show all shipments"),
        ("Add corn",           "Add 100 tons corn to stock"),
    ]

    st.markdown(
        '<p style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
        'letter-spacing:0.16em;text-transform:uppercase;color:#2d3a50;margin-bottom:8px;">Quick examples</p>',
        unsafe_allow_html=True
    )

    ex_cols = st.columns(4, gap="small")
    for i, (short, full) in enumerate(EXAMPLES):
        with ex_cols[i]:
            
            if st.button(short, key=f"ex_{i}"):
                st.session_state["ai_query_prefill"] = full
                st.rerun()

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    user_q = st.text_area(
        "AI query",
        placeholder="e.g. Send 100 tons wheat to Ganja",
        height=88,
        label_visibility="collapsed",
        key="ai_query_input",
    )

    send_c, _ = st.columns([1, 7])
    with send_c:
        send = st.button("Send →", key="ai_send")

    if pending_result is not None:
        render_ai_response(pending_result)

    if send:
        if not user_q.strip():
            st.warning("Query cannot be empty.")
        else:
            with st.spinner("Processing…"):
                try:
                    res = run(_post_params("/ai-task/", {"user_input": user_q.strip()}))
                    st.session_state["ai_pending_result"] = res
                    st.session_state["_clear_ai_query"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"API error: {e}")

    sec("Capabilities")
    caps = [
        ("check_inventory", "#34d47a", "Query current stock levels"),
        ("log_shipment",    "#4b9cf5", "Create shipment, deduct stock"),
        ("add_inventory",   "#f5a623", "Add new product or restock"),
    ]
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, (name, color, desc) in zip([c1, c2, c3], caps):
        with col:
            st.markdown(f"""
            <div style="background:#0f1319;border:1px solid #1c2333;border-top:2px solid {color};
                        border-radius:8px;padding:16px 18px;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.16em;
                          text-transform:uppercase;color:{color};margin-bottom:8px;">{name}</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;
                          color:#4a5a72;line-height:1.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)