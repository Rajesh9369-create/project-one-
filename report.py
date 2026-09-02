from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def generate_farm_report(result: dict, farm_name: str, reporting_period: str, factor_registry: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("CoastalCarbon AI — Farm Carbon Assessment", styles["Title"]),
             Paragraph(f"{farm_name or 'Unnamed farm'} | Reporting period: {reporting_period or 'Not specified'}", styles["Normal"]), Spacer(1, 8)]

    story.append(Paragraph("Assessment status", styles["Heading2"]))
    story.append(Paragraph("This is a management assessment based on supplied and reviewed activity data. It is not an ASC certification finding, assurance statement, or carbon-credit claim.", styles["Normal"]))
    story.append(Spacer(1, 8))

    metrics = result["metrics"]
    metric_rows = [
        ["Metric", "Result"],
        ["Harvested shrimp", f"{result['production_kg']:,.1f} kg"],
        ["Total emissions", f"{result['total_kg_co2e']:,.1f} kg CO₂e"],
        ["Carbon intensity", f"{result['carbon_intensity_kg_co2e_per_kg']:.3f} kg CO₂e/kg shrimp"],
        ["FCR", f"{metrics['fcr']:.3f}" if metrics["fcr"] is not None else "Not calculated — initial biomass required"],
        ["Feed intensity", f"{metrics['feed_intensity_kg_per_kg']:.3f} kg feed/kg shrimp"],
        ["Energy intensity", f"{metrics['energy_intensity_kwh_per_kg']:.3f} kWh/kg shrimp"],
        ["Diesel intensity", f"{metrics['diesel_intensity_l_per_kg']:.4f} L/kg shrimp"],
    ]
    story.append(Table(metric_rows, colWidths=[65*mm, 105*mm], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EEF3")), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("VALIGN", (0,0), (-1,-1), "TOP")
    ])))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Emissions ledger", styles["Heading2"]))
    rows = [["Source", "Scope", "kg CO₂e", "Factor", "Unit", "Factor source"]]
    for a in result["activities"]:
        rows.append([a.name, a.scope, f"{a.kg_co2e:,.2f}", f"{a.factor:g}", a.factor_unit, a.source])
    story.append(Table(rows, repeatRows=1, colWidths=[30*mm, 20*mm, 25*mm, 20*mm, 30*mm, 45*mm], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EEF3")), ("GRID", (0,0), (-1,-1), 0.35, colors.grey), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 7), ("VALIGN", (0,0), (-1,-1), "TOP")
    ])))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Priority interventions", styles["Heading2"]))
    for item in result["interventions"]:
        story.append(Paragraph(f"P{item['priority']} — {item['area']} ({item['hotspot_share']*100:.1f}% footprint share)", styles["Heading3"]))
        story.append(Paragraph(f"Recommended action: {item['action']}", styles["Normal"]))
        story.append(Paragraph(f"Why: {item['why']}", styles["Normal"]))
        story.append(Paragraph(f"Standard basis: {item['standard_basis']}", styles["Normal"]))
        story.append(Spacer(1, 5))

    story.append(Paragraph("Emission factor register", styles["Heading2"]))
    elec = factor_registry["electricity"]["india_grid_weighted_average"]
    factor_rows = [["Factor", "Value", "Source", "Reporting year / version"], ["India grid electricity", f"{elec['value']} {elec['unit']}", elec["source"], f"{elec.get('reporting_year','')} / V{elec.get('version','')}"]]
    story.append(Table(factor_rows, colWidths=[35*mm, 35*mm, 70*mm, 30*mm], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EEF3")), ("GRID", (0,0), (-1,-1), 0.35, colors.grey), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 7), ("VALIGN", (0,0), (-1,-1), "TOP")
    ])))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Important: factor applicability, source-document accuracy, feed-factor boundaries, transport-factor boundaries and production-system boundaries must be verified before external disclosure.", styles["Italic"]))

    doc.build(story)
    return buffer.getvalue()
