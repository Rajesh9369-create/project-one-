import json
import streamlit as st
from calculator import calculate
from extractor import extract_text, suggest_fields

st.set_page_config(page_title="CoastalCarbon AI", page_icon="🌊", layout="wide")

with open("factors.json", "r", encoding="utf-8") as f:
    factors = json.load(f)

st.title("🌊 CoastalCarbon AI")
st.caption("Aqua MSME carbon tracker — documents → reviewed activity data → deterministic carbon calculation")

st.header("1. Upload records")
st.write("Upload bills/invoices/records. Extraction is only a suggestion: review every value before calculation.")

doc_types = ["Electricity bill", "Diesel invoice", "Feed invoice", "Production record"]
files = {}
cols = st.columns(4)
for col, dtype in zip(cols, doc_types):
    with col:
        files[dtype] = st.file_uploader(dtype, type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "csv"], key=dtype)

if "extracted" not in st.session_state:
    st.session_state.extracted = {}

if st.button("Extract values from uploaded records"):
    for dtype, uploaded in files.items():
        if uploaded:
            text = extract_text(uploaded)
            st.session_state.extracted[dtype] = {"text": text, "fields": suggest_fields(text, dtype)}

st.header("2. Review extracted data")
ex = st.session_state.extracted
if ex:
    for dtype, payload in ex.items():
        with st.expander(dtype, expanded=True):
            st.text_area("Extracted text", payload["text"][:6000], height=120, key=f"txt_{dtype}")
            for field, value in payload["fields"].items():
                st.session_state[f"review_{field}"] = st.number_input(
                    field.replace("_", " ").title(), min_value=0.0,
                    value=float(value) if value is not None else 0.0,
                    key=f"input_{field}",
                    help="Verify this value against the original document. 0 is accepted only when the source actually says zero."
                )
else:
    st.info("Upload records above and click Extract. You can also enter values manually below.")

st.header("3. Complete / verify calculation inputs")
left, right = st.columns(2)
with left:
    production_kg = st.number_input("Shrimp production (kg)", min_value=0.0, value=float(st.session_state.get("review_production_kg", 10000.0)), step=100.0)
    electricity_kwh = st.number_input("Electricity (kWh)", min_value=0.0, value=float(st.session_state.get("review_electricity_kwh", 12000.0)), step=100.0)
    diesel_litres = st.number_input("Diesel (L)", min_value=0.0, value=float(st.session_state.get("review_diesel_litres", 500.0)), step=10.0)
    feed_kg = st.number_input("Feed used (kg)", min_value=0.0, value=float(st.session_state.get("review_feed_kg", 14000.0)), step=100.0)
with right:
    electricity_factor = st.number_input("Grid factor (kg CO₂/kWh)", min_value=0.0, value=float(factors["electricity"]["india_grid_weighted_average"]["value"]), format="%.6f")
    diesel_scope1 = st.number_input("Diesel Scope 1 factor (kg CO₂e/L)", min_value=0.0, value=float(factors["diesel"]["scope1"]["value"]), format="%.4f")
    diesel_upstream = st.number_input("Diesel upstream Scope 3 factor (kg CO₂e/L)", min_value=0.0, value=float(factors["diesel"]["scope3_upstream"]["value"]), format="%.4f")
    feed_factor_raw = st.number_input("Feed factor (kg CO₂e/kg feed)", min_value=0.0, value=0.0, step=0.01)

st.subheader("Feed transport")
t1, t2 = st.columns(2)
with t1:
    distance_km = st.number_input("Feed mill → farm distance (km)", min_value=0.0, value=250.0, step=10.0)
with t2:
    transport_factor_raw = st.number_input("Transport factor (kg CO₂e / tonne-km)", min_value=0.0, value=0.0, step=0.001)

feed_factor = feed_factor_raw if feed_factor_raw > 0 else None
transport_factor = transport_factor_raw if transport_factor_raw > 0 else None

if st.button("Calculate carbon footprint", type="primary"):
    try:
        result = calculate(
            production_kg, electricity_kwh, electricity_factor,
            diesel_litres, diesel_scope1, diesel_upstream,
            feed_kg, feed_factor, "User-supplied documented feed factor",
            distance_km, transport_factor,
            factors["electricity"]["india_grid_weighted_average"]["source"],
            "ASC Farm Standard v1.0.1A2", "User-supplied documented transport factor",
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Total emissions", f"{result['total_kg_co2e']:,.1f} kg CO₂e")
        m2.metric("Carbon intensity", f"{result['carbon_intensity_kg_co2e_per_kg']:.3f} kg CO₂e/kg shrimp")
        m3.metric("Data status", "Complete" if result["complete"] else "INCOMPLETE")

        rows = [{"Source": a.name, "Scope": a.scope, "kg CO₂e": round(a.kg_co2e, 3), "Factor": a.factor, "Unit": a.factor_unit, "Factor source": a.source} for a in result["activities"]]
        st.subheader("Auditable emissions ledger")
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.subheader("4. Priority interventions")
        st.caption("Recommendations are standards-aligned management actions based on measured hotspots. They are not certification findings and do not guarantee a specific CO₂e reduction.")
        for item in result["interventions"]:
            share = item["hotspot_share"] * 100
            title = f"P{item['priority']} — {item['area']}"
            with st.expander(title, expanded=item["priority"] <= 2):
                if item["area"] != "GHG management plan & verification":
                    st.metric("Measured footprint share", f"{share:.1f}%")
                st.write("**Recommended action:** " + item["action"])
                st.write("**Why:** " + item["why"])
                st.caption("Standard basis: " + item["standard_basis"])

        if not result["complete"]:
            st.error("INCOMPLETE ACCOUNTING: a documented feed and/or transport emission factor is missing. Do not use this result for certification, customer disclosure or carbon-credit claims.")
        else:
            st.info("Calculation complete means the required factors were supplied; source documents and factor boundaries still require verification before external reporting.")
        st.info("Aeration and refrigeration are treated as energy-consuming activities under electricity when their consumption is already included in the electricity total. This prevents double counting.")
    except ValueError as exc:
        st.error(str(exc))

st.divider()
st.caption("Factor registry: " + factors["version"])
st.caption("Always verify factor geography, year/version, system boundary and production boundary before external reporting.")
