"""
Reward360 Transaction Intelligence Engine — Streamlit Frontend (Stitch Re-creation)

Recreates the corporate Stitch visual design mockup with pixel accuracy, including
sidebar, header tabs, KPI cards, uploader, results table, details drawer, and footer.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
import textwrap

from src.pipeline import Pipeline


# Configure Streamlit page for exact layout
st.set_page_config(
    page_title="Transaction Intelligence Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper to render raw HTML without markdown parsing issues
def render_html(html_str):
    cleaned = "\n".join(line.lstrip() for line in html_str.split("\n"))
    st.markdown(cleaned, unsafe_allow_html=True)

# ---------------------------------------------------------
# Visual Pipeline Component
# ---------------------------------------------------------
def render_pipeline_flow(method):
    steps = [
        {"name": "Raw Text", "key": "Raw"},
        {"name": "Preprocessor", "key": "Prep"},
        {"name": "Dictionary", "key": "Dictionary"},
        {"name": "Regex", "key": "Regex"},
        {"name": "RapidFuzz", "key": "Fuzzy"},
        {"name": "Groq LLM", "key": "LLM"},
        {"name": "Category Mapping", "key": "Cat"},
        {"name": "Confidence", "key": "Conf"},
        {"name": "Output", "key": "Out"}
    ]
    
    states = {}
    if not method:
        for s in steps:
            states[s["key"]] = "bypassed"
    elif method == "Dictionary":
        states = {"Raw": "passed", "Prep": "passed", "Dictionary": "resolved", "Regex": "bypassed", "Fuzzy": "bypassed", "LLM": "bypassed", "Cat": "passed", "Conf": "passed", "Out": "passed"}
    elif method == "Regex":
        states = {"Raw": "passed", "Prep": "passed", "Dictionary": "failed", "Regex": "resolved", "Fuzzy": "bypassed", "LLM": "bypassed", "Cat": "passed", "Conf": "passed", "Out": "passed"}
    elif method == "Fuzzy":
        states = {"Raw": "passed", "Prep": "passed", "Dictionary": "failed", "Regex": "failed", "Fuzzy": "resolved", "LLM": "bypassed", "Cat": "passed", "Conf": "passed", "Out": "passed"}
    elif method == "LLM":
        states = {"Raw": "passed", "Prep": "passed", "Dictionary": "failed", "Regex": "failed", "Fuzzy": "failed", "LLM": "resolved", "Cat": "passed", "Conf": "passed", "Out": "passed"}
    else:
        states = {"Raw": "passed", "Prep": "passed", "Dictionary": "failed", "Regex": "failed", "Fuzzy": "failed", "LLM": "failed", "Cat": "passed", "Conf": "passed", "Out": "passed"}
        
    html = '<div class="pipeline-flow">'
    for i, step in enumerate(steps):
        state = states.get(step["key"], "bypassed")
        
        node_cls = ""
        if state == "passed":
            node_cls = "node-passed"
            sym = "✓"
        elif state == "resolved":
            node_cls = "node-resolved"
            sym = "★"
        elif state == "failed":
            node_cls = "node-failed"
            sym = "✗"
        else:
            node_cls = "node-bypassed"
            sym = str(i+1)
            
        html += f"""
        <div class="pipeline-node {node_cls}">
            <div class="node-circle">{sym}</div>
            <div class="node-label">{step['name']}</div>
        </div>
        """
        
        if i < len(steps) - 1:
            next_st = states.get(steps[i+1]["key"], "bypassed")
            conn_cls = "connector-bypassed"
            if next_st in ["passed", "resolved"]:
                conn_cls = "connector-passed"
            elif next_st == "failed":
                conn_cls = "connector-failed"
            html += f'<div class="pipeline-connector {conn_cls}"></div>'
            
    html += '</div>'
    return html

# Helper to extract location from transaction text
def get_location_for_txn(raw_text: str) -> str:
    raw_upper = str(raw_text).upper()
    if "SFO" in raw_upper or " CA" in raw_upper:
        return "San Francisco, CA"
    elif "WA" in raw_upper or "AMZN" in raw_upper or "SEATTLE" in raw_upper:
        return "Seattle, WA"
    elif "NY" in raw_upper or "NEW YORK" in raw_upper:
        return "New York, NY"
    elif "TX" in raw_upper or "DALLAS" in raw_upper:
        return "Dallas, TX"
    elif "IL" in raw_upper or "CHICAGO" in raw_upper:
        return "Chicago, IL"
    elif "MUMBAI" in raw_upper or "MUM" in raw_upper or "BOMBAY" in raw_upper:
        return "Mumbai, IN"
    elif "BANGALORE" in raw_upper or "BLR" in raw_upper or "BENGALURU" in raw_upper:
        return "Bangalore, IN"
    elif "DELHI" in raw_upper or "DEL" in raw_upper:
        return "Delhi, IN"
    elif "HYDERABAD" in raw_upper or "HYD" in raw_upper:
        return "Hyderabad, IN"
    elif "CHENNAI" in raw_upper or "CHE" in raw_upper or "MAS" in raw_upper:
        return "Chennai, IN"
    elif "INDIA" in raw_upper or " IN" in raw_upper:
        return "Mumbai, IN"
    return "Online"

# Helper to generate trace logs
def generate_transaction_logs(raw, merchant, category, method, confidence, time_val, reason):
    import re
    try:
        t_ms = float(re.findall(r"[\d\.]+", str(time_val))[0])
    except:
        t_ms = 15.0
        
    t_init = max(0.1, round(t_ms * 0.1, 1))
    t_prep = max(0.1, round(t_ms * 0.15, 1))
    t_match = max(0.1, round(t_ms * 0.65, 1))
    t_infer = max(0.1, round(t_ms * 0.1, 1))
    
    logs = [
        f"[{t_init:.1f}ms] INIT: Initiating resolution pipeline for transaction",
        f"[{t_prep:.1f}ms] PRE-PROCESS: Standardizing description and stripping noise",
    ]
    
    base_method = method.replace(" (Cached)", "")
    if "Cached" in method:
        logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: Cache hit for cleaned key")
        logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: Reused previous resolution ({reason})")
    else:
        logs.append(f"[{t_prep + 1.0:.1f}ms] MATCH: Cache miss")
        if base_method == "Dictionary":
            logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: Dictionary matcher found match: {reason}")
        elif base_method == "Regex":
            logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: Regex pattern matched: {reason}")
        elif base_method == "Fuzzy":
            logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: Fuzzy matcher found match: {reason}")
        elif base_method == "LLM":
            logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: LLM API request completed: {reason}")
        else:
            logs.append(f"[{t_prep + t_match:.1f}ms] MATCH: All matcher tiers failed. Fallback applied.")
            
    logs.append(f"[{t_prep + t_match + t_infer:.1f}ms] INFER: Category mapping resolved to: {category}")
    logs.append(f"[{t_ms:.1f}ms] RESOLVE: Completed. Confidence {confidence}%.")
    return logs

# ---------------------------------------------------------
# Load custom CSS stylesheet
# ---------------------------------------------------------
styles_path = Path(__file__).resolve().parent / "styles.css"
if styles_path.exists():
    with open(styles_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    # Load fallback inline styles
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
            .stApp { background-color: #F8FAFC; }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Initialize Session State Mock Data
# ---------------------------------------------------------
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = Pipeline()

if 'results' not in st.session_state:
    st.session_state.results = [
        {
            "raw": "UBER *TRIP SFO TO PA 11/04 CA",
            "merchant": "Uber",
            "category": "Transportation > Ride Share",
            "category_short": "Transportation",
            "confidence": 88,
            "method": "Dictionary",
            "time": "12ms",
            "reason": "Dictionary Match (Rule ID: D-442)",
            "location": "San Francisco, CA",
            "logs": [
                "[08ms] INTTTATE: TXN-99201-B",
                "[02ms] PRE-PROCESS: Cleaning whitespace, symbols",
                "[05ms] MATCH: Cache miss",
                "[10ms] MATCH: Dictionary hit \"UBER\" -> Merchant:Uber",
                "[12ms] INFER: Category mapping successful",
                "[12ms] RESOLVE: Completed. Confidence 98%."
            ]
        },
        {
            "raw": "AMZN Mktp US*2J8A39R Anzn.com/billWA",
            "merchant": "Amazon",
            "category": "Shopping > E-commerce",
            "category_short": "Shopping",
            "confidence": 95,
            "method": "Regex",
            "time": "18ms",
            "reason": "Regex Match [Pattern: ^AMZN Mkt...]",
            "location": "Seattle, WA",
            "logs": [
                "[05ms] INTTTATE: TXN-99202-B",
                "[02ms] PRE-PROCESS: Cleaning whitespace, symbols",
                "[05ms] MATCH: Cache miss",
                "[10ms] MATCH: Regex pattern matched -> Merchant:Amazon",
                "[15ms] INFER: Category mapping successful",
                "[18ms] RESOLVE: Completed. Confidence 95%."
            ]
        },
        {
            "raw": "TST* LOCAL COFFEE SHOP NY",
            "merchant": "Local Coffee Shop",
            "category": "Food & Dining > Cafe",
            "category_short": "Food & Dining",
            "confidence": 82,
            "method": "LLM",
            "time": "145ms",
            "reason": "LLM Resolution [Model: Llama 3.3]",
            "location": "New York, NY",
            "logs": [
                "[05ms] INTTTATE: TXN-99203-B",
                "[02ms] PRE-PROCESS: Cleaning whitespace, symbols",
                "[05ms] MATCH: Cache miss",
                "[120ms] MATCH: LLM API request completed -> Merchant:Local Coffee Shop",
                "[135ms] INFER: Category mapping successful",
                "[145ms] RESOLVE: Completed. Confidence 82%."
            ]
        },
        {
            "raw": "SQ *FARMERS MKT VENDOR",
            "merchant": "Unknown Vendor",
            "category": "Groceries > Market",
            "category_short": "Groceries",
            "confidence": 65,
            "method": "Fuzzy",
            "time": "85ms",
            "reason": "Fuzzy Match [RapidFuzz Score: 87%]",
            "location": "Dallas, TX",
            "logs": [
                "[05ms] INTTTATE: TXN-99204-B",
                "[02ms] PRE-PROCESS: Cleaning whitespace, symbols",
                "[05ms] MATCH: Cache miss",
                "[65ms] MATCH: Fuzzy similarity matched -> Merchant:Unknown Vendor",
                "[78ms] INFER: Category mapping successful",
                "[85ms] RESOLVE: Completed. Confidence 65%."
            ]
        },
        {
            "raw": "MCDONALDS*RESTAURANT",
            "merchant": "McDonald's",
            "category": "Food & Dining > Fast Food",
            "category_short": "Food & Dining",
            "confidence": 99,
            "method": "Dictionary",
            "time": "8ms",
            "reason": "Dictionary Exact Match",
            "location": "Chicago, IL",
            "logs": [
                "[00ms] INTTTATE: TXN-99205-B",
                "[01ms] PRE-PROCESS: Cleaning whitespace",
                "[04ms] MATCH: Dictionary hit -> McDonald's",
                "[08ms] RESOLVE: Completed. Confidence 99%."
            ]
        },
        {
            "raw": "KFC ONLINE DELIVERY",
            "merchant": "KFC",
            "category": "Food & Dining > Fast Food",
            "category_short": "Food & Dining",
            "confidence": 99,
            "method": "Dictionary",
            "time": "10ms",
            "reason": "Dictionary Substring Match",
            "location": "Mumbai, IN",
            "logs": [
                "[00ms] INTTTATE: TXN-99206-B",
                "[01ms] PRE-PROCESS: Cleaning whitespace",
                "[05ms] MATCH: Dictionary hit -> KFC",
                "[10ms] RESOLVE: Completed. Confidence 99%."
            ]
        },
        {
            "raw": "JIO PREPAID RECHARGE",
            "merchant": "Reliance Jio",
            "category": "Utilities > Telecom",
            "category_short": "Utilities",
            "confidence": 97,
            "method": "Regex",
            "time": "24ms",
            "reason": "Regex Substring Match",
            "location": "Mumbai, IN",
            "logs": [
                "[00ms] INTTTATE: TXN-99207-B",
                "[02ms] PRE-PROCESS: Cleaning whitespace",
                "[15ms] MATCH: Regex pattern matched -> Reliance Jio",
                "[24ms] RESOLVE: Completed. Confidence 97%."
            ]
        }
    ]

if 'raw_transaction_input' not in st.session_state:
    st.session_state.raw_transaction_input = ""
if 'editing_mapping' not in st.session_state:
    st.session_state.editing_mapping = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# ---------------------------------------------------------
# Parse URL Query Parameters for State Management
# ---------------------------------------------------------
query_params = st.query_params

# Tab selection (default: dashboard)
active_tab = query_params.get("tab", "dashboard")
st.session_state.active_tab = active_tab

# Sidebar selection (default: dashboard)
active_menu = query_params.get("menu", "dashboard")
st.session_state.active_menu = active_menu

# Selected transaction index
selected_param = query_params.get("selected", None)
selected_idx = None
if selected_param is not None and selected_param != "":
    try:
        selected_idx = int(selected_param)
    except:
        pass
st.session_state.selected_transaction_index = selected_idx

# Page selection
page_param = query_params.get("page", None)
if page_param is not None and page_param != "":
    try:
        st.session_state.current_page = int(page_param)
    except:
        pass

# Edit state selection
edit_param = query_params.get("edit", None)
st.session_state.editing_mapping = (edit_param == "true")

# Actions (e.g. New Analysis)
action_param = query_params.get("action", None)
if action_param == "new":
    # Reset
    st.session_state.pipeline = Pipeline()
    st.session_state.results = st.session_state.results[:7] # keep original mock values
    st.session_state.selected_transaction_index = None
    st.session_state.current_page = 0
    st.query_params.clear()
    st.toast("Active analysis session reset!", icon="🧹")
    st.rerun()

# ---------------------------------------------------------
# Sidebar Rendering
# ---------------------------------------------------------
def render_sidebar():
    active_dashboard = "active" if active_menu == "dashboard" else ""
    active_dict = "active" if active_menu == "dict" else ""
    active_logs = "active" if active_menu == "logs" else ""

    render_html(f"""
    <div class="stitch-sidebar">
        <div class="sidebar-logo-section">
            <div class="logo-text">TX Intelligence</div>
            <div class="logo-version">v2.4.0-prod</div>
        </div>
        <div class="sidebar-menu">
            <a href="?menu=dashboard" target="_self" class="menu-item {active_dashboard}">
                <span class="menu-icon">📊</span> Dashboard
            </a>
            <a href="?menu=dict" target="_self" class="menu-item {active_dict}">
                <span class="menu-icon">📖</span> Merchant Dictionary
            </a>
            <a href="?menu=logs" target="_self" class="menu-item {active_logs}">
                <span class="menu-icon">🕒</span> Processing Logs
            </a>
        </div>
    </div>
    """)

with st.sidebar:
    render_sidebar()

# ---------------------------------------------------------
# Top Header Navbar Rendering
# ---------------------------------------------------------
def render_header_navbar():
    render_html(f"""
    <div class="top-navbar">
        <div class="navbar-title-section">
            <h2 class="navbar-title">Transaction Intelligence Engine</h2>
            <span class="navbar-subtitle">AI-powered Merchant Intelligence for Banking Transactions</span>
        </div>
        <div class="navbar-icons">
            <div class="nav-icon-bell">
                🔔<span class="bell-dot"></span>
            </div>
            <div class="nav-icon-profile">👤</div>
        </div>
    </div>
    """)

render_header_navbar()

# ---------------------------------------------------------
# Page Router & Content Panels
# ---------------------------------------------------------

if active_menu == "dict":
    st.markdown("### Merchant Lookup Dictionary")
    st.markdown("Search or browse our curated alias mapping directory. Matches found here are resolved instantly via our high-priority Tier 1 Dictionary Matcher.")
    
    search_d = st.text_input("Search dictionary...", placeholder="Search by alias, canonical merchant, or category...", label_visibility="collapsed")
    
    from data.merchant_dictionary import MERCHANT_ALIASES
    from src.category_mapper import CategoryMapper
    
    dict_data = []
    for alias, merchant in MERCHANT_ALIASES.items():
        category = CategoryMapper.get_category(merchant) or "Other"
        dict_data.append({"Alias": alias, "Merchant": merchant, "Category": category})
        
    # Sort by Alias alphabetically
    dict_data = sorted(dict_data, key=lambda x: x["Alias"])
        
    if search_d:
        q = search_d.lower()
        dict_data = [d for d in dict_data if q in d["Alias"].lower() or q in d["Merchant"].lower() or q in d["Category"].lower()]
        
    st.dataframe(pd.DataFrame(dict_data), use_container_width=True, hide_index=True, height=450)

elif active_menu == "logs":
    st.markdown("### Processing Logs")
    st.markdown("Real-time logging output from the active Transaction Intelligence hybrid resolution pipeline:")
    
    log_file_path = Path(__file__).resolve().parent / "logs" / "pipeline.log"
    if log_file_path.exists():
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_lines = f.readlines()
        
        # Filter and display the last 40 lines of log entries to avoid overflow
        recent_logs = "".join(log_lines[-40:])
        st.code(recent_logs, language="text")
    else:
        st.info("No active pipeline log file found.")



else:
    # ---------------------------------------------------------
    # Main Dashboard Page (Analytics tab - ACTIVE in mockup)
    # ---------------------------------------------------------
    st.markdown('<div class="main-content-area">', unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # Upload and Test Panel (Two-Column Layout)
    # ---------------------------------------------------------
    col_up_left, col_up_right = st.columns([1.1, 1])
    
    with col_up_left:
        with st.container(border=True):
            col_c_title, col_c_link = st.columns([1.5, 1])
            with col_c_title:
                st.markdown('<h4 class="card-title">Batch Processing</h4>', unsafe_allow_html=True)
            with col_c_link:
                st.markdown('<div style="text-align:right;"><a href="data:text/csv;charset=utf-8,Raw%20Transaction%0AUBER%20*TRIP%20SFO%20TO%20PA%2011%2F04%20CA%0AAMZN%20Mktp%20US*2J8A39R%20Anzn.com%2FbillWA%0ATST*%20LOCAL%20COFFEE%20SHOP%20NY%0ASQ%20*FARMERS%20MKT%20VENDOR" download="sample_transactions.csv" class="link-download-sample">Download Sample CSV</a></div>', unsafe_allow_html=True)
                
            st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)
            
            # Streamlit Native File Uploader
            uploaded_file = st.file_uploader(
                "Drag and drop CSV file here, or click to browse",
                type=["csv"],
                label_visibility="collapsed",
                key="dashboard_csv_uploader"
            )
            
            # Display simulated file state
            if uploaded_file is not None:
                st.success(f"File loaded: {uploaded_file.name}")
        
    with col_up_right:
        with st.container(border=True):
            st.markdown('<h4 class="card-title">Single Transaction Analysis</h4>', unsafe_allow_html=True)
            st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="label-input">Raw Transaction String</div>', unsafe_allow_html=True)
            
            raw_txn_text = st.text_area(
                "Raw Transaction Input field",
                value=st.session_state.raw_transaction_input,
                placeholder="e.g., UBER *TRIP SFO TO PA 11/04 CA...",
                label_visibility="collapsed",
                height=108,
                key="dashboard_raw_txn_field"
            )
            
            st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)
            
            col_act_space, col_act_btns = st.columns([1, 2])
            with col_act_btns:
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    process_csv_click = st.button("Process CSV", key="dashboard_process_btn")
                with col_b2:
                    analyze_click = st.button("⚡ Analyze", key="dashboard_analyze_btn", type="primary")

    # ---------------------------------------------------------
    # Handle Button Clicks (Real Pipeline Integration)
    # ---------------------------------------------------------
    if analyze_click and raw_txn_text:
        res = st.session_state.pipeline.process_single_transaction(raw_txn_text)
        raw_val = res["Raw Transaction"]
        merch_val = res["Clean Merchant"]
        cat_val = res["Category"]
        cat_short = cat_val.split(">")[0].strip()
        conf_val = res["Confidence"]
        meth_val = res["Method Used"]
        time_val = f"{res['Processing Time (ms)']}ms"
        reason_val = res["Reason"]
        loc_val = get_location_for_txn(raw_val)
        logs_val = generate_transaction_logs(raw_val, merch_val, cat_val, meth_val, conf_val, time_val, reason_val)
        
        new_row = {
            "raw": raw_val,
            "merchant": merch_val,
            "category": cat_val,
            "category_short": cat_short,
            "confidence": conf_val,
            "method": meth_val,
            "time": time_val,
            "reason": reason_val,
            "location": loc_val,
            "logs": logs_val
        }
        st.session_state.results.insert(0, new_row)
        st.session_state.selected_transaction_index = 0
        st.session_state.raw_transaction_input = "" # clear
        st.query_params["selected"] = "0"
        st.toast("Transaction resolved!", icon="✅")
        st.rerun()

    if process_csv_click:
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                # Find transaction column
                detected_col = None
                for col in df.columns:
                    col_lower = str(col).lower()
                    if "raw" in col_lower or "transaction" in col_lower or "desc" in col_lower or "text" in col_lower or "description" in col_lower:
                        detected_col = col
                        break
                if detected_col is None:
                    detected_col = df.columns[0]
                
                processed_df = st.session_state.pipeline.process_csv(df, detected_col)
                
                # Convert processed_df back to results list
                new_results = []
                for _, row in processed_df.iterrows():
                    raw_val = row["Raw Transaction"]
                    merch_val = row["Clean Merchant"]
                    cat_val = row["Category"]
                    cat_short = cat_val.split(">")[0].strip()
                    conf_val = int(row["Confidence"])
                    meth_val = row["Method Used"]
                    time_val = f"{row['Processing Time (ms)']}ms"
                    reason_val = row["Reason"]
                    loc_val = get_location_for_txn(raw_val)
                    logs_val = generate_transaction_logs(raw_val, merch_val, cat_val, meth_val, conf_val, time_val, reason_val)
                    
                    new_results.append({
                        "raw": raw_val,
                        "merchant": merch_val,
                        "category": cat_val,
                        "category_short": cat_short,
                        "confidence": conf_val,
                        "method": meth_val,
                        "time": time_val,
                        "reason": reason_val,
                        "location": loc_val,
                        "logs": logs_val
                    })
                
                st.session_state.results = new_results
                st.session_state.selected_transaction_index = None
                st.session_state.current_page = 0
                
                # Clear standard parameters
                st.query_params.clear()
                st.query_params["tab"] = active_tab
                st.query_params["menu"] = active_menu
                
                st.toast(f"CSV file processed successfully! {len(new_results)} rows resolved.", icon="📊")
                st.rerun()
            except Exception as e:
                st.error(f"Error processing CSV file: {e}")
        else:
            st.error("Please drag or browse a CSV file first.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # KPI Grid (8 metrics showing the requested Stitch numbers, calculated dynamically)
    # ---------------------------------------------------------
    total_txns = len(st.session_state.results)
    
    # Parse times
    times = []
    for row in st.session_state.results:
        import re
        try:
            t = float(re.findall(r"[\d\.]+", str(row["time"]))[0])
            times.append(t)
        except:
            pass
    avg_time = sum(times) / len(times) if times else 0.0
    
    cache_hits = sum(1 for row in st.session_state.results if "Cached" in str(row["method"]))
    avg_conf = sum(row["confidence"] for row in st.session_state.results) / total_txns if total_txns > 0 else 0.0
    
    dict_matches = sum(1 for row in st.session_state.results if "Dictionary" in str(row["method"]))
    regex_matches = sum(1 for row in st.session_state.results if "Regex" in str(row["method"]))
    fuzzy_matches = sum(1 for row in st.session_state.results if "Fuzzy" in str(row["method"]))
    llm_matches = sum(1 for row in st.session_state.results if "LLM" in str(row["method"]))
    
    dict_pct = round((dict_matches / total_txns) * 100) if total_txns > 0 else 0
    regex_pct = round((regex_matches / total_txns) * 100) if total_txns > 0 else 0
    fuzzy_pct = round((fuzzy_matches / total_txns) * 100) if total_txns > 0 else 0
    llm_pct = round((llm_matches / total_txns) * 100) if total_txns > 0 else 0

    kpi_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Total Transactions</div>
            <div class="kpi-body">
                <span class="kpi-value">{total_txns:,}</span>
                <span class="kpi-badge kpi-badge-green">↑ 12%</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Average Processing Time</div>
            <div class="kpi-body">
                <span class="kpi-value">{avg_time:.1f}ms</span>
                <span class="kpi-badge kpi-badge-green">↓ 5ms</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Cache Hits</div>
            <div class="kpi-body">
                <span class="kpi-value">{cache_hits:,}</span>
                <span class="kpi-badge kpi-badge-grey">Stable</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Average Confidence</div>
            <div class="kpi-body">
                <span class="kpi-value">{avg_conf:.1f}%</span>
                <span class="kpi-badge kpi-badge-green">↑ 1%</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Dictionary Matches</div>
            <div class="kpi-body">
                <span class="kpi-value">{dict_matches:,}</span>
                <span class="kpi-badge kpi-badge-green">{dict_pct}%</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Regex Matches</div>
            <div class="kpi-body">
                <span class="kpi-value">{regex_matches:,}</span>
                <span class="kpi-badge kpi-badge-green">{regex_pct}%</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Fuzzy Matches</div>
            <div class="kpi-body">
                <span class="kpi-value">{fuzzy_matches:,}</span>
                <span class="kpi-badge kpi-badge-green">{fuzzy_pct}%</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">LLM Matches</div>
            <div class="kpi-body">
                <span class="kpi-value">{llm_matches:,}</span>
                <span class="kpi-badge kpi-badge-green">{llm_pct}%</span>
            </div>
        </div>
    </div>
    """
    render_html(kpi_html)

    # ---------------------------------------------------------
    # AI Pipeline Card (Highlighting Stage used)
    # ---------------------------------------------------------
    active_row = None
    if selected_idx is not None and selected_idx < len(st.session_state.results):
        active_row = st.session_state.results[selected_idx]
        
    method_name = active_row["method"] if active_row else None
    pipeline_html = f"""
    <div class="pipeline-card">
        <div class="label-input" style="margin-bottom: 8px;">Active AI Resolution Pipeline</div>
        {render_pipeline_flow(method_name)}
    </div>
    """
    render_html(pipeline_html)

    # ---------------------------------------------------------
    # Main Results and Side Details Drawer Layout Split
    # ---------------------------------------------------------
    has_drawer = selected_idx is not None
    
    if has_drawer:
        col_tbl_main, col_drawer_side = st.columns([3, 1.25])
    else:
        col_tbl_main = st.container()
        col_drawer_side = None

    with col_tbl_main:
        # Results table card container
        with st.container(border=True):
            col_r_title, col_r_search = st.columns([2.5, 1.5])
            with col_r_title:
                st.markdown('<h4 class="card-title">Analysis Results</h4>', unsafe_allow_html=True)
            with col_r_search:
                # Table Search input
                search_query_input = st.text_input(
                    "Search input",
                    value="",
                    placeholder="Search transactions...",
                    label_visibility="collapsed",
                    key="results_table_search_bar"
                )
                # Store in session state for filtering
                st.session_state.search_query_val = search_query_input
                
            st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
            
            # Filter rows by search box
            filtered_rows = []
            for idx, row in enumerate(st.session_state.results):
                if not search_query_input or (
                    search_query_input.lower() in row["raw"].lower() or
                    search_query_input.lower() in row["merchant"].lower() or
                    search_query_input.lower() in row["category"].lower() or
                    search_query_input.lower() in row["method"].lower()
                ):
                    filtered_rows.append((idx, row))
                    
            # Pagination calculations (5 rows per page matching Stitch)
            page_size = 5
            total_filtered = len(filtered_rows)
            max_pages = max(1, (total_filtered + page_size - 1) // page_size)
            
            st.session_state.current_page = min(st.session_state.current_page, max_pages - 1)
            st.session_state.current_page = max(0, st.session_state.current_page)
            
            start_idx = st.session_state.current_page * page_size
            end_idx = min(start_idx + page_size, total_filtered)
            
            paginated_rows = filtered_rows[start_idx:end_idx]
            
            # Build HTML table cells
            table_html = """
            <div class="stitch-table-wrapper">
                <table class="stitch-table">
                    <thead>
                        <tr>
                            <th>RAW TRANSACTION</th>
                            <th>MERCHANT</th>
                            <th>CATEGORY</th>
                            <th>CONFIDENCE</th>
                            <th>METHOD</th>
                            <th>REASON</th>
                            <th>PROCESSING TIME</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for orig_idx, row in paginated_rows:
                is_selected = (selected_idx == orig_idx)
                row_class = "clickable-row selected-row" if is_selected else "clickable-row"
                
                conf = row["confidence"]
                badge_cls = "badge-table-green" if conf >= 85 else ("badge-table-yellow" if conf >= 70 else "badge-table-red")
                
                m_val = row["merchant"]
                m_style = "cell-bold" if m_val != "Unknown Vendor" else "cell-italic-muted"
                
                def make_cell(content, is_bold=False, is_muted=False):
                    cls = "cell-link"
                    if is_bold: cls += " cell-bold"
                    if is_muted: cls += " cell-italic-muted"
                    return f'<td><a class="{cls}" href="?selected={orig_idx}&tab={active_tab}&menu={active_menu}&page={st.session_state.current_page}" target="_self">{content}</a></td>'
                
                method_cls = row['method'].replace(' (Cached)', '').lower()
                table_html += f"""
                    <tr class="{row_class}">
                        {make_cell(row['raw'])}
                        {make_cell(row['merchant'], is_bold=(m_val != "Unknown Vendor"), is_muted=(m_val == "Unknown Vendor"))}
                        {make_cell(row['category_short'])}
                        <td><a class="cell-link" href="?selected={orig_idx}&tab={active_tab}&menu={active_menu}&page={st.session_state.current_page}" target="_self"><span class="badge-table {badge_cls}">{row['confidence']}%</span></a></td>
                        <td><a class="cell-link" href="?selected={orig_idx}&tab={active_tab}&menu={active_menu}&page={st.session_state.current_page}" target="_self"><span class="chip-method chip-method-{method_cls}">{row['method']}</span></a></td>
                        {make_cell(row['reason'])}
                        {make_cell(row['time'])}
                    </tr>
                """
                
            table_html += """
                    </tbody>
                </table>
            </div>
            """
            
            # Render the custom clickable HTML table
            render_html(table_html)
            
            # Build pagination footer controls in HTML
            prev_page = max(0, st.session_state.current_page - 1)
            next_page = min(max_pages - 1, st.session_state.current_page + 1)
            prev_disabled = "disabled" if st.session_state.current_page == 0 else ""
            next_disabled = "disabled" if st.session_state.current_page == max_pages - 1 else ""
            
            prev_href = f'?page={prev_page}&selected={selected_param or ""}&tab={active_tab}&menu={active_menu}' if not prev_disabled else '#'
            next_href = f'?page={next_page}&selected={selected_param or ""}&tab={active_tab}&menu={active_menu}' if not next_disabled else '#'
            
            footer_html = f"""
            <div class="results-footer">
                <div>Showing {start_idx+1}-{end_idx} of {total_filtered:,} results</div>
                <div class="pagination-controls">
                    <a href="{prev_href}" target="_self" class="btn-pagination {prev_disabled}">◀</a>
                    <a href="{next_href}" target="_self" class="btn-pagination {next_disabled}">▶</a>
                </div>
            </div>
            """
            render_html(footer_html)

    # ---------------------------------------------------------
    # Right Drawer Column (Details & Trace logs)
    # ---------------------------------------------------------
    if col_drawer_side and active_row is not None:
        with col_drawer_side:
            # Inject sliding layout margin when drawer is open
            st.markdown("""
                <style>
                @media (min-width: 1200px) {
                    .block-container {
                        padding-right: 450px !important;
                    }
                }
                </style>
            """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown('<div id="drawer-marker"></div>', unsafe_allow_html=True)
                
                # Enrichment Output values
                merchant_name = active_row["merchant"]
                category_name = active_row["category"]
                conf_val = active_row["confidence"]
                method_val = active_row["method"]
                time_val = active_row["time"]
                location_val = active_row["location"]
                log_lines = "\n".join(active_row["logs"])
                
                # Re-process text variants for display (mock)
                norm_str = str(active_row["raw"]).upper().strip()
                import re
                clean_str = re.sub(r'\b\d+\b', '', norm_str)
                clean_str = clean_str.replace("SQ *", "").replace("TST*", "").replace("UBER *", "").replace("AMZN *", "").replace(" * ", " ").strip()
                
                conf_color = "#10B981" if conf_val >= 85 else ("#D97706" if conf_val >= 70 else "#EF4444")
                conf_bg = "#ECFDF5" if conf_val >= 85 else ("#FEF7E0" if conf_val >= 70 else "#FEF2F2")
                
                drawer_html = f"""
                <div class="drawer-header">
                    <div>
                        <h4 class="drawer-title">Transaction Details</h4>
                        <span class="drawer-ref">Ref: TXN-99{selected_idx}-B</span>
                    </div>
                    <a href="?selected=&page={st.session_state.current_page}&tab={active_tab}&menu={active_menu}" target="_self" class="drawer-close">&times;</a>
                </div>
                
                <div class="drawer-section-title">ENRICHMENT OUTPUT</div>
                <div class="enrichment-card">
                    <div class="enrichment-row">
                        <span class="enrichment-label">Original Text</span>
                        <span class="enrichment-value value-mono">{active_row['raw']}</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Normalized</span>
                        <span class="enrichment-value value-mono">{norm_str}</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Cleaned Text</span>
                        <span class="enrichment-value value-mono">{clean_str}</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Merchant</span>
                        <span class="enrichment-value value-bold">{merchant_name}</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Category</span>
                        <span class="enrichment-value">{category_name}</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Location</span>
                        <span class="enrichment-value">{location_val}</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Confidence</span>
                        <span class="enrichment-value"><span class="badge badge-green" style="color:{conf_color}; background-color:{conf_bg};">{conf_val}%</span></span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Method</span>
                        <span class="enrichment-value">{method_val} Match</span>
                    </div>
                    <div class="enrichment-row">
                        <span class="enrichment-label">Time</span>
                        <span class="enrichment-value">{time_val}</span>
                    </div>
                </div>
                
                <div class="drawer-section-title">PROCESSING PIPELINE LOG</div>
                <div class="terminal-log"><code>{log_lines}</code></div>
                """
                render_html(drawer_html)

    # ---------------------------------------------------------
    # Analytics Charts (Working mock charts at the bottom)
    # ---------------------------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_ch1, col_ch2, col_ch3 = st.columns(3)
    
    with col_ch1:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.05em;'>RESOLUTION METHOD</div>", unsafe_allow_html=True)
        # Mock pie chart matching Stitch
        pie_values = [dict_matches, regex_matches, fuzzy_matches, llm_matches]
        if sum(pie_values) == 0:
            pie_values = [1, 0, 0, 0]
        fig1 = px.pie(
            values=pie_values,
            names=["Dictionary", "Regex", "Fuzzy", "LLM"],
            hole=0.45,
            color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B", "#8B5CF6"]
        )
        fig1.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            height=200,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig1, use_container_width=True, key="dashboard_pie", config={"displayModeBar": False})
        
    with col_ch2:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.05em;'>TRANSACTIONS BY CATEGORY</div>", unsafe_allow_html=True)
        # Dynamic categories bar chart
        cat_counts = {}
        for row in st.session_state.results:
            c = row.get("category_short", "Other")
            cat_counts[c] = cat_counts.get(c, 0) + 1
        categories_list = ["Shopping", "Dining", "Travel", "Fuel", "Groceries", "Utilities", "Other"]
        bar_y = [cat_counts.get(c, 0) for c in categories_list]

        fig2 = px.bar(
            x=categories_list,
            y=bar_y,
            color_discrete_sequence=["#8B5CF6"]
        )
        fig2.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="",
            yaxis_title="",
            height=200,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig2, use_container_width=True, key="dashboard_bar", config={"displayModeBar": False})
        
    with col_ch3:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.05em;'>CONFIDENCE DISTRIBUTION</div>", unsafe_allow_html=True)
        # Dynamic confidence histogram
        confidences = [row["confidence"] for row in st.session_state.results]
        if not confidences:
            confidences = [100]
            
        fig3 = px.histogram(
            x=confidences,
            nbins=8,
            color_discrete_sequence=["#2563EB"]
        )
        fig3.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="",
            yaxis_title="",
            height=200,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, range=[0, 100]),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig3, use_container_width=True, key="dashboard_hist", config={"displayModeBar": False})

    # ---------------------------------------------------------
    # Dynamic Footer Section
    # ---------------------------------------------------------
    total_time_s = sum(times) / 1000.0
    llm_made = st.session_state.pipeline.stats.get("LLM_Calls_Made", 0)
    llm_saved = st.session_state.pipeline.stats.get("LLM_Calls_Saved", 0)
    
    # Generate Output CSV dynamically
    import urllib.parse
    out_rows = []
    for r in st.session_state.results:
        out_rows.append({
            "Raw Transaction": r["raw"],
            "Clean Merchant": r["merchant"],
            "Category": r["category"],
            "Confidence": r["confidence"],
            "Method Used": r["method"],
            "Processing Time": r["time"]
        })
    if out_rows:
        out_df = pd.DataFrame(out_rows)
        csv_string = out_df.to_csv(index=False)
        csv_data = urllib.parse.quote(csv_string)
    else:
        csv_data = "Raw%20Transaction%2CClean%20Merchant%2CCategory%2CConfidence%2CMethod%20Used%2CProcessing%20Time"
        
    footer_html = f"""
    <div class="stitch-footer">
        <div class="footer-left">
            Total Processing Time: <span class="footer-left-val">{total_time_s:.2f}s</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
            LLM Calls Made/Saved: <span class="footer-left-val">{llm_made:,} / {llm_saved:,}</span>
        </div>
        <div class="footer-center">
            © 2024 Transaction Intelligence Engine v2.4.0-prod
        </div>
        <div class="footer-right">
            <a href="data:text/csv;charset=utf-8,{csv_data}" download="transactions_output.csv" class="btn-output-csv">📥 Output CSV</a>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(footer_html), unsafe_allow_html=True)
