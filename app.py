import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Country Launch Scoring", layout="wide")

with open("thresholds.json") as f:
    RUBRIC = json.load(f)["categories"]
    
DEFAULT_SELECT = ["Very weak","Weak","Moderate","Strong","Excellent"]

# Pre-populated country data extracted from your CSVs
COUNTRY_DATA = {
    "Singapore": {
        "GDP per capita": 72794.0,
        "Gini coefficient": 0.37,
        "Disposable income": 3500.0,
        "Retail investor penetration": 28.0,
        "Islamic robo competitors": "Moderate competition",
        "Conventional robo penetration": 2500.0,
        "Digital maturity": "Excellent",
        "Shariah-compliant instruments": "Strong range (21–50)",
        "Sukuk & mutual funds": "Strong",
        "Real estate crowdfunding": "Moderate",
        "Ethical commodities": "Excellent",
        "Clarity for Islamic Finance": "Weak",
        "Licensing process": "Weak",
        "Regulatory stability": "Excellent",
        "KYC providers": "Excellent",
        "Physical setup cost": "Low",
        "Brokers & custodians": "Weak",
        "Talent pool": 0.85,
        "Ethical investing culture": "Weak",
        "Shariah finance attitudes": "Excellent",
        "Attitude towards Muslims": "Mixed/neutral",
        "Digital adoption": "Mixed"
    },
    "India": {
        "GDP per capita": 2600.0,
        "Gini coefficient": 0.25,
        "Disposable income": 800.0,
        "Retail investor penetration": 6.0,
        "Islamic robo competitors": "None present",
        "Conventional robo penetration": 16.0,
        "Digital maturity": "Excellent",
        "Shariah-compliant instruments": "None available",
        "Sukuk & mutual funds": "Very weak",
        "Real estate crowdfunding": "Moderate",
        "Ethical commodities": "Moderate",
        "Clarity for Islamic Finance": "Very weak",
        "Licensing process": "Strong",
        "Regulatory stability": "Moderate",
        "KYC providers": "Strong",
        "Physical setup cost": "Low",
        "Brokers & custodians": "Excellent",
        "Talent pool": 1.0,
        "Ethical investing culture": "Very weak",
        "Shariah finance attitudes": "Very weak",
        "Attitude towards Muslims": "Very negative",
        "Digital adoption": "Mixed"
    },
    "France": {
        "GDP per capita": 39117.0,
        "Gini coefficient": 0.3,
        "Disposable income": 3000.0,
        "Retail investor penetration": 24.0,
        "Islamic robo competitors": "None present",
        "Conventional robo penetration": 4200.0,
        "Digital maturity": "Excellent",
        "Shariah-compliant instruments": "Extensive opportunities (50+)",
        "Sukuk & mutual funds": "Excellent",
        "Real estate crowdfunding": "Excellent",
        "Ethical commodities": "Excellent",
        "Clarity for Islamic Finance": "Moderate",
        "Licensing process": "Strong",
        "Regulatory stability": "Excellent",
        "KYC providers": "Excellent",
        "Physical setup cost": "Very high",
        "Brokers & custodians": "Weak",
        "Talent pool": 0.5,
        "Ethical investing culture": "Strong",
        "Shariah finance attitudes": "Weak",
        "Attitude towards Muslims": "Negative",
        "Digital adoption": "Digital-leaning"
    },
    "Netherlands": {
        "GDP per capita": 52000.0,
        "Gini coefficient": 0.29,
        "Disposable income": 3000.0,
        "Retail investor penetration": 82.0,
        "Islamic robo competitors": "Sparse presence",
        "Conventional robo penetration": 277.0,
        "Digital maturity": "Excellent",
        "Shariah-compliant instruments": "Strong range (21–50)",
        "Sukuk & mutual funds": "Moderate",
        "Real estate crowdfunding": "Moderate",
        "Ethical commodities": "Moderate",
        "Clarity for Islamic Finance": "Strong",
        "Licensing process": "Excellent",
        "Regulatory stability": "Excellent",
        "KYC providers": "Excellent",
        "Physical setup cost": "Very low",
        "Brokers & custodians": "Excellent",
        "Talent pool": 1.0,
        "Ethical investing culture": "Excellent",
        "Shariah finance attitudes": "Weak",
        "Attitude towards Muslims": "Negative",
        "Digital adoption": "Digital-first"
    },
    "Canada": {
        "GDP per capita": 54283.0,
        "Gini coefficient": 0.31,
        "Disposable income": 2400.0,
        "Retail investor penetration": 25.0,
        "Islamic robo competitors": "Sparse presence",
        "Conventional robo penetration": 450.0,
        "Digital maturity": "Excellent",
        "Shariah-compliant instruments": "Moderate range (6–20)",
        "Sukuk & mutual funds": "Moderate",
        "Real estate crowdfunding": "Weak",
        "Ethical commodities": "Excellent",
        "Clarity for Islamic Finance": "Strong",
        "Licensing process": "Weak",
        "Regulatory stability": "Excellent",
        "KYC providers": "Excellent",
        "Physical setup cost": "Moderate",
        "Brokers & custodians": "Moderate",
        "Talent pool": 1.0,
        "Ethical investing culture": "Excellent",
        "Shariah finance attitudes": "Excellent",
        "Attitude towards Muslims": "Negative",
        "Digital adoption": "Digital-leaning"
    },
    "Brunei": {
        "GDP per capita": 29600.0,
        "Gini coefficient": 0.63,
        "Disposable income": 1200.0,
        "Retail investor penetration": 2.0,
        "Islamic robo competitors": "None present",
        "Conventional robo penetration": 10.0,
        "Digital maturity": "Moderate",
        "Shariah-compliant instruments": "Extensive opportunities (50+)",
        "Sukuk & mutual funds": "Moderate",
        "Real estate crowdfunding": "Weak",
        "Ethical commodities": "Weak",
        "Clarity for Islamic Finance": "Excellent",
        "Licensing process": "Strong",
        "Regulatory stability": "Excellent",
        "KYC providers": "Moderate",
        "Physical setup cost": "Very low",
        "Brokers & custodians": "Moderate",
        "Talent pool": 0.5,
        "Ethical investing culture": "Weak",
        "Shariah finance attitudes": "Excellent",
        "Attitude towards Muslims": "Very positive",
        "Digital adoption": "Branch-leaning"
    },
    "Custom (Manual Entry)": {}
}

@st.cache_data
def load_thresholds():
    with open("thresholds.json", "r") as f:
        return json.load(f)

def score_numeric(value, breaks, scores, direction):
    if value is None:
        return 3, "N/A → neutral 3"
    
    if direction == "higher_better":
        for b, s in zip(reversed(breaks), reversed(scores)):
            if value >= b:
                return s, f"{value} ≥ {b} → {s}"
        return scores[0], f"{value} < {breaks[0]} → {scores[0]}"
    elif direction == "lower_better":
        for b, s in zip(breaks, scores):
            if value <= b:
                return s, f"{value} ≤ {b} → {s}"
        return scores[-1], f"{value} > {breaks[-1]} → {scores[-1]}"

def score_select(val, custom_options, reverse=False):
    options = custom_options or DEFAULT_SELECT
    try:
        idx = options.index(val)
    except ValueError:
        idx = 2
    score = (5 - idx) if reverse else (idx + 1)
    return score, f"{val} → {score}"

def readiness_label(score):
    if score >= 4.5: return "Launch-ready (Excellent)", "#10b981"
    elif score >= 3.8: return "Strong candidate (Good)", "#3b82f6"
    elif score >= 3.0: return "Conditional (Needs fixes)", "#f59e0b"
    else: return "High risk (Major issues)", "#ef4444"

def narrative(country, category_scores, overall):
    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    top3, bot3 = sorted_cats[:3], sorted_cats[-3:]
    label, _ = readiness_label(overall)
    lines = [f"**Market Assessment: {country}**", "", f"Launch Readiness: {overall:.2f}/5 → **{label}**", ""]
    lines.append("**Top-scoring categories:**")
    lines += [f"- {c}: {v:.2f}" for c, v in top3]
    lines.append("")
    lines.append("**Lowest-scoring categories:**")
    lines += [f"- {c}: {v:.2f}" for c, v in bot3]
    return "\n".join(lines)

# Clean, professional styling with proper contrast
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 300 !important;
    }
    
    /* Main content area */
    .main {
        background-color: #ffffff;
        padding: 2rem;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Headings - light weight, minimalist */
    h1 {
        font-weight: 300 !important;
        color: #1a1a1a !important;
        font-size: 2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    h2, h3 {
        font-weight: 300 !important;
        color: #1a1a1a !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }
    
    /* Labels - light weight */
    .stSelectbox label, .stNumberInput label {
        font-weight: 400 !important;
        color: #1a1a1a !important;
        font-size: 0.9rem !important;
    }
    
    /* Input fields */
    div[data-baseweb="select"] > div {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="select"] > div:hover {
        border-color: #9ca3af;
    }
    
    /* Fix dropdown menu background and text */
    div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[role="option"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    div[role="option"]:hover {
        background-color: #f3f4f6 !important;
        color: #1a1a1a !important;
    }
    
    /* Selected option text in the dropdown */
    div[data-baseweb="select"] span {
        color: #1a1a1a !important;
    }
    
    /* Dropdown arrow */
    div[data-baseweb="select"] svg {
        color: #6b7280 !important;
    }
    
    .stNumberInput input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-weight: 300 !important;
    }
    
    .stNumberInput input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Buttons - keep medium weight for readability */
    .stButton > button {
        border-radius: 8px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 400 !important;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    /* Caption text - light weight for minimalism */
    .stMarkdown p, p[data-testid="stMarkdownContainer"] {
        color: #6b7280 !important;
        font-size: 0.875rem;
        line-height: 1.5;
        font-weight: 300 !important;
    }
    
    /* Bold text in markdown - medium weight */
    .stMarkdown strong {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        font-weight: 300 !important;
    }
    
    /* Data tables */
    .stDataFrame {
        border-radius: 8px;
    }
    
    .stDataFrame td, .stDataFrame th {
        font-weight: 300 !important;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 8px;
        background-color: #ffffff;
        color: #1a1a1a !important;
        border: 1px solid #d1d5db;
        padding: 0.5rem 1.2rem;
        font-weight: 400 !important;
        font-size: 0.9rem;
    }
    
    .stDownloadButton > button:hover {
        border-color: #9ca3af;
        background-color: #f9fafb;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1rem;
        font-weight: 400 !important;
        color: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] p {
        color: #4b5563 !important;
        font-weight: 300 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #4b5563 !important;
        font-weight: 300 !important;
    }
    
    /* Metric widget */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-weight: 300 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6b7280 !important;
        font-weight: 300 !important;
    }
</style>
''', unsafe_allow_html=True)

st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        font-weight: 400 !important;
    }
    div[data-baseweb="select"] div {
        color: black !important;
    }
    div[data-baseweb="select"] span {
        color: black !important;
    }
    ul[role="listbox"] {
        background-color: white !important;
        color: black !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }
    section[data-testid="stSidebar"] * {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

thresholds = load_thresholds()

st.title("Country Launch Scoring")
st.markdown("<p style='color: #6b7280; font-size: 1rem; margin-top: -0.5rem;'>Assess market readiness for Shariah/Ethical robo-advisory services</p>", unsafe_allow_html=True)
st.markdown("")

# Initialize session state for country if not exists
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = "Singapore"

# Country selection dropdown
col1, col2 = st.columns([2, 3])
with col1:
    country = st.selectbox(
        "Select Jurisdiction",
        options=list(COUNTRY_DATA.keys()) + ["Custom (Manual Entry)"],
        key='country_selector',
        help="Select a pre-populated country or choose 'Custom (Manual Entry)' to enter manually"
    )

# If user chooses Custom, show text input box
if country == "Custom (Manual Entry)":
    manual_name = st.text_input("Enter Country Name Manually")
    if manual_name.strip():
        st.session_state.selected_country = manual_name.strip()
    else:
        st.session_state.selected_country = "Custom (Manual Entry)"
else:
    st.session_state.selected_country = country

# Get pre-populated data
if st.session_state.selected_country in COUNTRY_DATA:
    selected_data = COUNTRY_DATA[st.session_state.selected_country]
else:
    selected_data = {}

# You can use this everywhere below
current_country = st.session_state.selected_country
st.write(f"Current country: {current_country}")


st.sidebar.header("Category Weights")
st.sidebar.markdown("*Total should equal 1.00*")
total_cat_weight = sum(cat_cfg["weight"] for cat_cfg in thresholds["categories"].values())
st.sidebar.metric("Total Weight", f"{total_cat_weight:.2f}")
st.sidebar.markdown("---")
for cat_name, cat_cfg in thresholds["categories"].items():
    st.sidebar.markdown(f"**{cat_name}**: {cat_cfg['weight']:.2f}")

if selected_data and country != "Custom (Manual Entry)":
    st.info(f"✓ Pre-populated data loaded for **{country}**. You can modify any field below.")

st.markdown("---")

cat_scores, cat_breakdown = {}, {}

for cat, cdef in RUBRIC.items():
    st.subheader(cat)
    total, metrics = 0.0, {}
    
    for mkey, mdef in cdef["metrics"].items():
        label = mdef.get("label", mkey)
        weight = mdef["weight"]
        
        if mdef.get("custom"):
            options = mdef.get("options", DEFAULT_SELECT)
            reverse = mdef.get("reverse_options", False)
            
            # Get pre-populated value or default to middle option
            default_val = selected_data.get(mkey, options[2])
            if default_val not in options:
                default_val = options[2]
            default_idx = options.index(default_val)
            
            val = st.selectbox(label, options, index=default_idx, key=f"sel_{country}_{cat}_{mkey}")
            score, why = score_select(val, options, reverse)
            raw = val
        else:
            # Get pre-populated numeric value or default to 0
            default_num = selected_data.get(mkey, 0.0)
            val = st.number_input(label, value=float(default_num), key=f"num_{country}_{cat}_{mkey}")
            score, why = score_numeric(val, mdef["breaks"], mdef["scores"], mdef["direction"])
            raw = val
            
        st.caption(f"_{mdef['reason']}_ → Score: **{score}** ({why}) • Weight: {weight:.2f}")
        total += score * weight
        metrics[mkey] = {"label": label, "input": raw, "score": score, "weight": weight, "reason": mdef["reason"]}
    
    cat_scores[cat] = round(total, 3)
    cat_breakdown[cat] = {"weight": cdef["weight"], "score": round(total, 3), "metrics": metrics}
    st.markdown("")

st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    compute_readiness = st.button("📊 Compute Launch Readiness", use_container_width=True)
with col2:
    compute_csv = st.button("📥 Generate CSV Reports", use_container_width=True)

if compute_readiness:
    overall = sum([cat_scores[c] * RUBRIC[c]["weight"] for c in RUBRIC.keys()])
    label, color = readiness_label(overall)
    
    st.session_state['launch_readiness'] = {
        'overall': overall,
        'label': label,
        'color': color,
        'narrative': narrative(country, cat_scores, overall)
    }

if 'launch_readiness' in st.session_state:
    lr = st.session_state['launch_readiness']
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {lr['color']}15 0%, {lr['color']}05 100%); 
                padding: 1.5rem; border-radius: 12px; border-left: 4px solid {lr['color']};
                margin: 1.5rem 0;'>
        <h2 style='color: {lr['color']}; margin: 0 0 0.5rem 0; font-size: 1.5rem;'>
            Launch Readiness: {lr['overall']:.2f}/5
        </h2>
        <p style='color: #4a4a4a; margin: 0; font-size: 1.1rem; font-weight: 500;'>
            {lr['label']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(lr['narrative'])

if compute_csv:
    rows = []
    category_rows = []
    overall = 0.0

    for cat_name, cat_cfg in thresholds["categories"].items():
        cat_weight = cat_cfg["weight"]
        cat_score_weighted_sum = 0.0
        cat_weight_sum = 0.0
        
        for mkey, mdef in cat_cfg["metrics"].items():
            label = mdef.get("label", mkey)
            weight = mdef["weight"]
            
            if mdef.get("custom"):
                val = st.session_state.get(f"sel_{country}_{cat_name}_{mkey}")
                options = mdef.get("options", DEFAULT_SELECT)
                reverse = mdef.get("reverse_options", False)
                score, rationale = score_select(val, options, reverse)
            else:
                val = st.session_state.get(f"num_{country}_{cat_name}_{mkey}")
                score, rationale = score_numeric(val, mdef["breaks"], mdef["scores"], mdef["direction"])
            
            rows.append({
                "Category": cat_name,
                "Metric": label,
                "Input": val if val is not None else "N/A",
                "Score": score,
                "Sub-weight": weight,
                "Weighted (metric)": round(score * weight, 3),
                "Rationale": rationale
            })
            cat_score_weighted_sum += score * weight
            cat_weight_sum += weight

        cat_avg_weighted = cat_score_weighted_sum / cat_weight_sum if cat_weight_sum > 0 else 0
        category_rows.append({
            "Category": cat_name,
            "Category weight": cat_weight,
            "Category score (weighted sub-metrics)": round(cat_avg_weighted, 3),
            "Contribution to overall": round(cat_avg_weighted * cat_weight, 3)
        })
        overall += cat_avg_weighted * cat_weight

    st.session_state['csv_results'] = {
        'rows': rows,
        'category_rows': category_rows,
        'overall': overall
    }

if 'csv_results' in st.session_state:
    csv = st.session_state['csv_results']
    
    st.markdown("### Metric-level Results")
    st.dataframe(pd.DataFrame(csv['rows']), use_container_width=True)

    st.markdown("### Category-level Results")
    st.dataframe(pd.DataFrame(csv['category_rows']), use_container_width=True)

    st.markdown("### Overall Score")
    st.metric("Final Score", f"{csv['overall']:.3f} / 5", f"{csv['overall']/5*100:.1f}%")

    safe_country_name = country.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download Metric Results (CSV)",
            pd.DataFrame(csv['rows']).to_csv(index=False).encode("utf-8"),
            file_name=f"{safe_country_name}_metrics.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "⬇️ Download Category Results (CSV)",
            pd.DataFrame(csv['category_rows']).to_csv(index=False).encode("utf-8"),
            file_name=f"{safe_country_name}_categories.csv",
            mime="text/csv",
            use_container_width=True
        )
