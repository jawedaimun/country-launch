import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Country Launch Scoring", layout="wide")

with open("thresholds.json") as f:
    RUBRIC = json.load(f)["categories"]
    
DEFAULT_SELECT = ["Very weak","Weak","Moderate","Strong","Excellent"]

# Pre-populated country data extracted from your CSVs
COUNTRY_DATA = {
    "India": {
        "GDP per capita": 2600.0,
        "Gini coefficient": 0.25,
        "Disposable income": 800.0,
        "Retail investor penetration": 6.0,
        "Islamic robo competitors": "None present",
        "Conventional robo penetration": 16.0,
        "Digital maturity": "Excellent",
        "Shariah-compliant instruments": "Extensive opportunities (50+)",
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
        "Conventional robo penetration": 0.0,
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
    "Custom (Manual Entry)": {}  # Empty for manual entry
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
    else:  # higher_worse
        for b, s in zip(breaks, scores):
            if value <= b:
                return s, f"{value} ≤ {b} → {s}"
        return scores[-1], f"{value} > {breaks[-1]} → {scores[-1]}"

def score_select(val, custom_options, reverse=False):
    options = custom_options or DEFAULT_SELECT
    try:
        idx = options.index(val)
    except ValueError:
        idx = 2  # Moderate/Neutral default
    score = (5 - idx) if reverse else (idx + 1)
    return score, f"{val} → {score}"

def readiness_label(score):
    if score >= 4.5: return "Launch-ready (Excellent)", "green"
    elif score >= 3.8: return "Strong candidate (Good)", "blue"
    elif score >= 3.0: return "Conditional (Needs fixes)", "orange"
    else: return "High risk (Major issues)", "red"

def narrative(country, category_scores, overall):
    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    top3, bot3 = sorted_cats[:3], sorted_cats[-3:]
    label, _ = readiness_label(overall)
    lines = [f"**Market Assessment: {country}**", "", f"Launch Readiness: {overall:.2f}/5 → **{label}**", ""]
    lines.append("Top-scoring categories:")
    lines += [f"- {c}: {v:.2f}" for c, v in top3]
    lines.append("")
    lines.append("Lowest-scoring categories:")
    lines += [f"- {c}: {v:.2f}" for c, v in bot3]
    return "\n".join(lines)

# Styling
st.markdown('''
<style>
body { background: white; color: #333; }
div[data-baseweb="input"] input, .stNumberInput input { max-width: 280px; border-radius: 10px; }
div[role="combobox"] { max-width: 320px; }
.stButton>button { border-radius: 10px; }
</style>
''', unsafe_allow_html=True)

thresholds = load_thresholds()
st.title("Shariah/Ethical Robo Advisory Country Launch Scoring")

# Country selection dropdown
country = st.selectbox(
    "Select Jurisdiction",
    options=list(COUNTRY_DATA.keys()),
    index=0,
    help="Select a pre-populated country or choose 'Custom' to enter manually"
)

# Get pre-populated data or empty dict
selected_data = COUNTRY_DATA.get(country, {})

st.sidebar.header("Weights overview")
total_cat_weight = sum(cat_cfg["weight"] for cat_cfg in thresholds["categories"].values())
st.sidebar.write(f"Total category weights = {total_cat_weight:.2f} (should be 1.00)")

if selected_data and country != "Custom (Manual Entry)":
    st.info(f"✅ Pre-populated data loaded for {country}. You can modify any field below.")

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
            
            # Get pre-populated value or default to first option
            default_val = selected_data.get(mkey, options[2])  # Default to middle option
            if default_val not in options:
                default_val = options[2]
            default_idx = options.index(default_val)
            
            val = st.selectbox(label, options, index=default_idx, key=f"sel_{cat}_{mkey}")
            score, why = score_select(val, options, reverse)
            raw = val
        else:
            # Get pre-populated numeric value or default to 0
            default_num = selected_data.get(mkey, 0.0)
            val = st.number_input(label, value=float(default_num), key=f"num_{cat}_{mkey}")
            score, why = score_numeric(val, mdef["breaks"], mdef["scores"], mdef["direction"])
            raw = val
            
        st.caption(f"{mdef['reason']} → Score {score} ({why}); weight {weight:.2f}")
        total += score * weight
        metrics[mkey] = {"label": label, "input": raw, "score": score, "weight": weight, "reason": mdef["reason"]}
    
    cat_scores[cat] = round(total, 3)
    cat_breakdown[cat] = {"weight": cdef["weight"], "score": round(total, 3), "metrics": metrics}

if st.button("Compute Launch Readiness"):
    overall = sum([cat_scores[c] * RUBRIC[c]["weight"] for c in RUBRIC.keys()])
    label, color = readiness_label(overall)
    
    # Store in session state
    st.session_state['launch_readiness'] = {
        'overall': overall,
        'label': label,
        'color': color,
        'narrative': narrative(country, cat_scores, overall)
    }

# Display if exists in session state
if 'launch_readiness' in st.session_state:
    lr = st.session_state['launch_readiness']
    st.markdown(f"<p style='color:{lr['color']};font-size:20px'><b>Launch Readiness: {lr['overall']:.2f}/5 → {lr['label']}</b></p>", unsafe_allow_html=True)
    st.markdown(lr['narrative'])

st.markdown("---")

if st.button("Compute score & Export CSVs"):
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
                val = st.session_state.get(f"sel_{cat_name}_{mkey}")
                options = mdef.get("options", DEFAULT_SELECT)
                reverse = mdef.get("reverse_options", False)
                score, rationale = score_select(val, options, reverse)
            else:
                val = st.session_state.get(f"num_{cat_name}_{mkey}")
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

    # Store in session state
    st.session_state['csv_results'] = {
        'rows': rows,
        'category_rows': category_rows,
        'overall': overall
    }

# Display if exists in session state
if 'csv_results' in st.session_state:
    csv = st.session_state['csv_results']
    
    st.subheader("Metric-level results")
    st.dataframe(pd.DataFrame(csv['rows']))

    st.subheader("Category-level results")
    st.dataframe(pd.DataFrame(csv['category_rows']))

    st.subheader("Overall score")
    st.write(f"**{csv['overall']:.3f} / 5**  (equivalently **{csv['overall']/5*100:.1f}%**)")

    # Clean up country name for filename
    safe_country_name = country.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    
    st.download_button(
        "Download metric results (CSV)",
        pd.DataFrame(csv['rows']).to_csv(index=False).encode("utf-8"),
        file_name=f"{safe_country_name}_metrics.csv",
        mime="text/csv"
    )
    st.download_button(
        "Download category results (CSV)",
        pd.DataFrame(csv['category_rows']).to_csv(index=False).encode("utf-8"),
        file_name=f"{safe_country_name}_categories.csv",
        mime="text/csv"
    )
