import json
import streamlit as st
from calculator import calculate

st.set_page_config(page_title="CoastalCarbon AI", layout="wide")

with open("factors.json", "r", encoding="utf-8") as f:
    factors = json.load(f)

st.title("CoastalCarbon AI — Aqua Carbon Tracker")
st.caption("V1: transparent aquaculture carbon accounting. Calculation is deterministic; AI/document extraction is deliberately not used to alter the math.")

st.sidebar.header("Production")
production_kg = st.sidebar.number_input("Shrimp production (kg)", min_value=0.0, value=10000.0, step=100.0)

a, b = st.columns(2)
with a:
    st.subheader("Electricity")
    electricity_kwh = st.number_input("Electricity (kWh)", min_value=0.0, value=12000.0, step=100.0)
    electricity_factor = st.number_input("Grid factor (kg CO₂/kWh)", min_value=0.0,
                                         value=float(factors["electricity"]["india_grid_weighted_average"]["value"]), format="%.6f")
    electricity_source = st.text_input("Electricity factor source", value=factors["electricity"]["india_grid_weighted_average"]["source"])

with b:
    st.subheader("Diesel")
    diesel_litres = st.number_input("Diesel (L)", min_value=0.0, value=500.0, step=10.0)
    diesel_scope1 = st.number_input("Diesel Scope 1 factor (kg CO₂e/L)", min_value=0.0,
                                    value=float(factors["diesel"]["scope1"]["value"]), format="%.4f")
    diesel_upstream = st.number_input("Diesel upstream Scope 3 factor (kg CO₂e/L)", min_value=0.0,
                                      value=float(factors["diesel"]["scope3_upstream"]["value"]), format="%.4f")
    diesel_source = st.text_input("Diesel factor source", value="ASC Farm Standard v1.0.1A2")

st.subheader("Feed")
c, d = st.columns(2)
with c:
    feed_kg = st.number_input("Feed used (kg)", min_value=0.0, value=14000.0, step=100.0)
    feed_factor_raw = st.number_input("Feed factor (kg CO₂e/kg feed)", min_value=0.0, value=0.0, step=0.01,
                                      help="Enter a documented supplier-specific factor. Zero means 'not supplied', not zero emissions.")
with d:
    feed_source = st.text_input("Feed factor source", value="Enter supplier EPD/GHG profile or documented compatible factor")

st.subheader("Feed transport")
e, f = st.columns(2)
with e:
    distance_km = st.number_input("Feed mill → farm distance (km)", min_value=0.0, value=250.0, step=10.0)
with f:
    transport_factor_raw = st.number_input("Transport factor (kg CO₂e / tonne-km)", min_value=0.0, value=0.0, step=0.001,
                                            help="Enter a documented mode-specific factor. Zero means 'not supplied', not zero emissions.")
transport_source = st.text_input("Transport factor source", value="Enter documented transport factor source")

feed_factor = feed_factor_raw if feed_factor_raw > 0 else None
transport_factor = transport_factor_raw if transport_factor_raw > 0 else None

if st.button("Calculate carbon footprint", type="primary"):
    try:
        result = calculate(
            production_kg, electricity_kwh, electricity_factor,
            diesel_litres, diesel_scope1, diesel_upstream,
            feed_kg, feed_factor, feed_source,
            distance_km, transport_factor,
            electricity_source, diesel_source, transport_source,
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Total emissions", f"{result['total_kg_co2e']:,.1f} kg CO₂e")
        m2.metric("Carbon intensity", f"{result['carbon_intensity_kg_co2e_per_kg']:.3f} kg CO₂e/kg shrimp")
        m3.metric("Data completeness", "Complete" if result["complete"] else "Incomplete")

        rows = [{"Source": a.name, "Scope": a.scope, "kg CO₂e": round(a.kg_co2e, 3),
                 "Factor": a.factor, "Factor unit": a.factor_unit, "Source": a.source} for a in result["activities"]]
        st.subheader("Emissions ledger")
        st.dataframe(rows, use_container_width=True, hide_index=True)

        if not result["complete"]:
            st.warning("The result is incomplete because a feed factor and/or transport factor was not supplied. Do not use this number for certification, customer disclosure, or carbon-credit claims until all required factors are documented.")
        st.info("Aeration and refrigeration are not added as separate emissions here when their energy is already included in electricity; this avoids double counting.")
    except ValueError as exc:
        st.error(str(exc))

st.divider()
st.caption("Factor registry version: " + factors["version"])
st.caption("Always verify emission-factor version, geography, system boundary, and production boundary before external reporting.")
