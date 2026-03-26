"""
Health Insurance Charges - Automated BI Report Generator
=========================================================
Usage:
    python InsuranceReport.py
    python InsuranceReport.py --input insurance.csv --output report.pdf
"""

import argparse
import os
from datetime import datetime
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Image, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

# Brand colours
C_PRIMARY   = colors.HexColor("#1A3C5E")
C_ACCENT    = colors.HexColor("#2D7DD2")
C_SMOKER    = colors.HexColor("#E63946")
C_NONSMOKER = colors.HexColor("#2D7DD2")
C_SUCCESS   = colors.HexColor("#2A9D8F")
C_WARNING   = colors.HexColor("#E9C46A")
C_LIGHT     = colors.HexColor("#F0F4F8")
C_MID       = colors.HexColor("#D6E0EA")
C_TEXT      = colors.HexColor("#2C3E50")
C_SUBTEXT   = colors.HexColor("#7F8C8D")

MPL_PRIMARY   = "#1A3C5E"
MPL_ACCENT    = "#2D7DD2"
MPL_SMOKER    = "#E63946"
MPL_NONSMOKER = "#2D7DD2"
MPL_REGIONS   = ["#1A3C5E", "#2D7DD2", "#2A9D8F", "#E9C46A"]

CHART_RC = {
    "figure.facecolor": "white",
    "axes.facecolor":   "#F7F9FB",
    "axes.edgecolor":   "#D6E0EA",
    "axes.grid":        True,
    "grid.color":       "#E4EBF2",
    "grid.linewidth":   0.6,
    "font.family":      "sans-serif",
    "font.size":        8,
    "axes.titlesize":   10,
    "axes.titleweight": "bold",
    "axes.titlecolor":  "#1A3C5E",
    "axes.labelcolor":  "#2C3E50",
    "xtick.color":      "#2C3E50",
    "ytick.color":      "#2C3E50",
}

FIT_W  = 15.5
HALF_W = 7.5


def build_styles():
    return {
        "cover_tag": ParagraphStyle(
            "cover_tag", fontSize=10, textColor=colors.HexColor("#7FB3D3"),
            fontName="Helvetica", spaceAfter=8),
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=26, textColor=colors.white,
            fontName="Helvetica-Bold", spaceAfter=12, leading=32),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=10, textColor=colors.HexColor("#BDC3C7"),
            fontName="Helvetica", spaceAfter=5),
        "cover_divider": ParagraphStyle(
            "cover_divider", fontSize=9, textColor=colors.HexColor("#4A7BA7"),
            fontName="Helvetica", spaceAfter=4),
        "section": ParagraphStyle(
            "section", fontSize=13, textColor=C_PRIMARY,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=5),
        "subsection": ParagraphStyle(
            "subsection", fontSize=10, textColor=C_PRIMARY,
            fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle(
            "body", fontSize=9, textColor=C_TEXT,
            fontName="Helvetica", leading=13, spaceAfter=3),
        "finding": ParagraphStyle(
            "finding", fontSize=9, textColor=C_TEXT,
            fontName="Helvetica", leading=14, spaceAfter=5,
            leftIndent=8),
        "kpi_label": ParagraphStyle(
            "kpi_label", fontSize=7, textColor=C_SUBTEXT,
            fontName="Helvetica", alignment=TA_CENTER),
        "kpi_value": ParagraphStyle(
            "kpi_value", fontSize=17, textColor=C_PRIMARY,
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "kpi_sub": ParagraphStyle(
            "kpi_sub", fontSize=7.5, textColor=C_ACCENT,
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "th": ParagraphStyle(
            "th", fontSize=8, textColor=colors.white,
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "td": ParagraphStyle(
            "td", fontSize=8.5, textColor=C_TEXT, fontName="Helvetica"),
        "td_r": ParagraphStyle(
            "td_r", fontSize=8.5, textColor=C_TEXT,
            fontName="Helvetica", alignment=TA_RIGHT),
        "footer": ParagraphStyle(
            "footer", fontSize=7, textColor=C_SUBTEXT,
            fontName="Helvetica", alignment=TA_CENTER),
    }


def analyse(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    bins   = [0, 24, 34, 44, 54, 100]
    labels = ["Under 25", "25-34", "35-44", "45-54", "55+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels)

    bmi_bins   = [0, 18.5, 25, 30, 100]
    bmi_labels = ["Underweight", "Normal", "Overweight", "Obese"]
    df["bmi_cat"] = pd.cut(df["bmi"], bins=bmi_bins, labels=bmi_labels)

    total         = len(df)
    avg_charge    = df["charges"].mean()
    smoker_avg    = df[df["smoker"] == "yes"]["charges"].mean()
    nonsmoker_avg = df[df["smoker"] == "no"]["charges"].mean()
    smoker_ratio  = smoker_avg / nonsmoker_avg

    smoker_grp = df.groupby("smoker")["charges"].agg(["mean", "median", "count"]).reset_index()
    age_grp    = (df.groupby("age_group", observed=True)["charges"]
                  .agg(["mean", "median", "count"]).reset_index())
    region_grp = (df.groupby("region")["charges"]
                  .agg(["mean", "median", "count"]).reset_index()
                  .sort_values("mean", ascending=False))
    sex_grp    = df.groupby("sex")["charges"].agg(["mean", "sum", "count"]).reset_index()

    male_pct   = sex_grp[sex_grp["sex"] == "male"]["count"].values[0] / total * 100
    female_pct = 100 - male_pct
    male_avg   = sex_grp[sex_grp["sex"] == "male"]["mean"].values[0]
    female_avg = sex_grp[sex_grp["sex"] == "female"]["mean"].values[0]

    smokers    = df[df["smoker"] == "yes"]
    nonsmokers = df[df["smoker"] == "no"]
    top10      = df.nlargest(10, "charges")[["age", "sex", "bmi", "children", "smoker", "region", "charges"]]

    return dict(
        df=df, total=total, avg_charge=avg_charge,
        smoker_avg=smoker_avg, nonsmoker_avg=nonsmoker_avg, smoker_ratio=smoker_ratio,
        smoker_grp=smoker_grp, age_grp=age_grp, region_grp=region_grp,
        sex_grp=sex_grp, male_pct=male_pct, female_pct=female_pct,
        male_avg=male_avg, female_avg=female_avg,
        smokers=smokers, nonsmokers=nonsmokers, top10=top10,
        n_smokers=len(smokers), n_nonsmokers=len(nonsmokers),
    )


def to_img(fig, width_cm=FIT_W):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return Image(buf, width=width_cm * cm)


def fmt_k(v, _=None):
    return f"${v/1000:.0f}k"


def chart_smoker_avg(d):
    with plt.rc_context(CHART_RC):
        fig, ax = plt.subplots(figsize=(3.2, 1.8))
        labels = ["Non-Smoker", "Smoker"]
        vals   = [d["nonsmoker_avg"], d["smoker_avg"]]
        cols   = [MPL_NONSMOKER, MPL_SMOKER]
        bars   = ax.barh(labels, vals, color=cols, height=0.35, alpha=0.9)
        for bar, val in zip(bars, vals):
            ax.text(val + 200, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}", va="center", fontsize=7.5, fontweight="bold",
                    color=bar.get_facecolor())
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
        ax.set_title("Avg Charges: Smoker vs Non-Smoker", fontsize=8)
        ax.set_xlim(0, d["smoker_avg"] * 1.22)
        ax.invert_yaxis()
        fig.tight_layout(pad=0.4)
    return to_img(fig, 8.5)


def chart_smoker_count(d):
    with plt.rc_context(CHART_RC):
        fig, ax = plt.subplots(figsize=(2.2, 1.8))
        cats = ["Non-Smoker", "Smoker"]
        vals = [d["n_nonsmokers"], d["n_smokers"]]
        cols = [MPL_NONSMOKER, MPL_SMOKER]
        bars = ax.bar(cats, vals, color=cols, width=0.35, alpha=0.9)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                    str(val), ha="center", fontsize=7.5, fontweight="bold")
        ax.set_title("No. of Policy Holders", fontsize=8)
        ax.set_ylabel("Count", fontsize=7)
        fig.tight_layout(pad=0.4)
    return to_img(fig, 6.5)


def chart_age(d):
    with plt.rc_context(CHART_RC):
        ag   = d["age_grp"]
        fig, ax = plt.subplots(figsize=(7, 3.2))
        x    = range(len(ag))
        cols = ["#2D7DD2", "#1E6DB5", "#185E9E", "#124F87", "#0C4070"]
        bars = ax.bar(x, ag["mean"], color=cols, width=0.5, alpha=0.9)
        ax.set_xticks(list(x))
        ax.set_xticklabels(ag["age_group"].astype(str))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
        ax.set_title("Average Insurance Charges by Age Group")
        for bar, val in zip(bars, ag["mean"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                    f"${val/1000:.1f}k", ha="center", va="bottom",
                    fontsize=8, fontweight="bold", color=MPL_PRIMARY)
        fig.tight_layout()
    return to_img(fig, FIT_W)


def chart_region(d):
    with plt.rc_context(CHART_RC):
        rg   = d["region_grp"]
        fig, ax = plt.subplots(figsize=(7, 2.8))
        bars = ax.barh(rg["region"].str.title(), rg["mean"],
                       color=MPL_REGIONS, height=0.38, alpha=0.9)
        for bar, val in zip(bars, rg["mean"]):
            ax.text(val + 80, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}", va="center", fontsize=8,
                    fontweight="bold", color=MPL_PRIMARY)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
        ax.set_title("Average Insurance Charges by Region")
        ax.set_xlim(0, rg["mean"].max() * 1.18)
        ax.invert_yaxis()
        fig.tight_layout()
    return to_img(fig, FIT_W)


def chart_bmi_scatter(d):
    with plt.rc_context(CHART_RC):
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.scatter(d["nonsmokers"]["bmi"], d["nonsmokers"]["charges"],
                   color=MPL_NONSMOKER, alpha=0.3, s=12, label="Non-Smoker")
        ax.scatter(d["smokers"]["bmi"], d["smokers"]["charges"],
                   color=MPL_SMOKER, alpha=0.5, s=16, label="Smoker")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
        ax.set_xlabel("BMI")
        ax.set_ylabel("Annual Charges ($)")
        ax.set_title("BMI vs Insurance Charges  (by Smoking Status)")
        ax.axvline(30, color="#E9C46A", linewidth=1.2, linestyle="--", alpha=0.85)
        ax.text(30.3, ax.get_ylim()[1] * 0.93, "Obese threshold\n(BMI 30)",
                fontsize=7, color="#B8860B")
        ax.legend(framealpha=0.9, fontsize=8)
        fig.tight_layout()
    return to_img(fig, FIT_W)


def chart_gender(d):
    with plt.rc_context(CHART_RC):
        fig, ax = plt.subplots(figsize=(3.2, 3.2))
        ax.set_aspect("equal")
        sizes  = [d["male_pct"], d["female_pct"]]
        labels = [f"Male\n{d['male_pct']:.1f}%", f"Female\n{d['female_pct']:.1f}%"]
        ax.pie(sizes, labels=labels, colors=[MPL_PRIMARY, MPL_ACCENT],
               autopct=None, startangle=90,
               wedgeprops={"edgecolor": "white", "linewidth": 2},
               textprops={"fontsize": 8.5},
               radius=0.85)
        ax.set_title("Policy Holders by Gender", fontsize=9, pad=8)
        fig.subplots_adjust(left=0.1, right=0.9, top=0.88, bottom=0.05)
    return to_img(fig, 6.5)


def kpi_card(label, value, sub, styles, accent_color=None):
    ac = accent_color or C_ACCENT
    inner = Table([
        [Paragraph(label, styles["kpi_label"])],
        [Paragraph(value, styles["kpi_value"])],
        [Paragraph(sub,   styles["kpi_sub"])],
    ], colWidths=[4.0 * cm])
    inner.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    wrapper = Table([[inner]], colWidths=[4.3 * cm])
    wrapper.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.white),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_MID),
        ("LINEBELOW",     (0, 0), (-1,  0), 3,   ac),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return wrapper


def on_page(canvas, doc, styles):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(C_PRIMARY)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.5 * cm, h - 0.76 * cm, "Health Insurance Charges Analysis")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(w - 1.5 * cm, h - 0.76 * cm, "BI Report  |  1,338 Customers")
    canvas.setFillColor(colors.HexColor("#7F8C8D"))
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(1.5 * cm, 0.5 * cm,
                      f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
    canvas.drawCentredString(w / 2, 0.5 * cm, "CONFIDENTIAL - Internal use only")
    canvas.drawRightString(w - 1.5 * cm, 0.5 * cm, f"Page {doc.page}")
    canvas.restoreState()


def base_tbl_style():
    return TableStyle([
        ("BACKGROUND",     (0, 0), (-1,  0), C_PRIMARY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT]),
        ("GRID",           (0, 0), (-1, -1), 0.4, C_MID),
        ("LEFTPADDING",    (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 7),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])


def build_report(csv_path, output_path):
    print(f"  Reading  : {csv_path}")
    d      = analyse(csv_path)
    styles = build_styles()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.8 * cm,  bottomMargin=1.5 * cm,
        title="Health Insurance Charges Analysis",
        author="BI Report Generator",
    )
    cb    = lambda cv, dc: on_page(cv, dc, styles)
    story = []

    # COVER PAGE
    cover_content = [
        [Paragraph("BUSINESS INTELLIGENCE REPORT", styles["cover_tag"])],
        [Spacer(1, 10)],
        [Paragraph("Health Insurance", styles["cover_title"])],
        [Paragraph("Charges Analysis", styles["cover_title"])],
        [Spacer(1, 16)],
        [Paragraph(f"Dataset: {d['total']:,} individual policy records", styles["cover_sub"])],
        [Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles["cover_sub"])],
        [Spacer(1, 20)],
        [Paragraph("Analysis covers:", styles["cover_divider"])],
        [Paragraph("Smoking Status   |   Age Groups   |   Regional Breakdown   |   BMI Impact   |   Gender", styles["cover_sub"])],
    ]
    cover_tbl = Table(cover_content, colWidths=[doc.width])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_PRIMARY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 30),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 30),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (0,  0),  50),
        ("BOTTOMPADDING", (0, -1),(-1, -1), 50),
    ]))
    story += [Spacer(1, 3.5 * cm), cover_tbl, PageBreak()]

    # EXECUTIVE SUMMARY
    story.append(Paragraph("Executive Summary", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=10))

    kpi_row = Table([[
        kpi_card("Total Customers",    f"{d['total']:,}",           "policy holders",        styles),
        kpi_card("Avg. Annual Charge", f"${d['avg_charge']:,.0f}",  "across all customers",  styles, C_ACCENT),
        kpi_card("Smoker Avg. Charge", f"${d['smoker_avg']:,.0f}",  "vs $8K non-smoker avg", styles, C_SMOKER),
        kpi_card("Smoker Cost Ratio",  f"{d['smoker_ratio']:.1f}x", "more than non-smokers", styles, C_SMOKER),
    ]], colWidths=[4.3 * cm] * 4, hAlign="CENTER")
    kpi_row.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    story += [kpi_row, Spacer(1, 12)]

    findings = [
        f"<b>Smoking is the #1 cost driver.</b> Smokers average ${d['smoker_avg']:,.0f} vs "
        f"${d['nonsmoker_avg']:,.0f} for non-smokers - a {d['smoker_ratio']:.1f}x difference. "
        f"With only {d['n_smokers']} smokers ({d['n_smokers']/d['total']*100:.0f}% of customers), "
        f"this group disproportionately drives claim costs.",

        "<b>Age has a clear positive relationship with charges.</b> Seniors (55+) average ~$18.5K, "
        "nearly double the charges of customers under 25 at ~$9.0K.",

        "<b>Regional variation is moderate.</b> The Southeast has the highest average charges (~$14.7K), "
        "while the Southwest averages around $12.3K.",

        "<b>BMI alone does not predict high charges.</b> Non-smokers maintain low charges across all BMI "
        "ranges. The high-cost cluster is almost entirely smokers, regardless of BMI.",

        f"<b>Gender plays a minor role.</b> Males account for {d['male_pct']:.1f}% of policies and "
        "average slightly higher charges than females, but the gap is small compared to smoking or age.",
    ]
    for txt in findings:
        story.append(Paragraph(f"•    {txt}", styles["finding"]))
    story.append(PageBreak())

    # SECTION 1: SMOKER
    story.append(Paragraph("1. Smoker vs Non-Smoker Analysis", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=8))

    side = Table(
        [[chart_smoker_avg(d), chart_smoker_count(d)]],
        colWidths=[10.0 * cm, 8.0 * cm]
    )
    side.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0,  -1), 6),
    ]))
    story += [side, Spacer(1, 10)]

    sg = d["smoker_grp"]
    smoke_rows = [[Paragraph(h, styles["th"]) for h in
                   ["Status", "Customers", "% of Total", "Avg Charge", "Median Charge"]]]
    for _, row in sg.iterrows():
        label = "Smoker" if row["smoker"] == "yes" else "Non-Smoker"
        pct   = row["count"] / d["total"] * 100
        smoke_rows.append([
            Paragraph(label,                    styles["td"]),
            Paragraph(f"{int(row['count']):,}", styles["td_r"]),
            Paragraph(f"{pct:.1f}%",            styles["td_r"]),
            Paragraph(f"${row['mean']:,.0f}",   styles["td_r"]),
            Paragraph(f"${row['median']:,.0f}", styles["td_r"]),
        ])
    st = Table(smoke_rows, colWidths=[3.5*cm, 3*cm, 3*cm, 3.5*cm, 4*cm])
    st.setStyle(base_tbl_style())
    story += [st, PageBreak()]

    # SECTION 2: AGE GROUP
    story.append(Paragraph("2. Charges by Age Group", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=8))
    story += [chart_age(d), Spacer(1, 10)]

    ag = d["age_grp"]
    age_rows = [[Paragraph(h, styles["th"]) for h in
                 ["Age Group", "Customers", "Avg Charge", "Median Charge", "Index vs Overall"]]]
    for _, row in ag.iterrows():
        idx     = row["mean"] / d["avg_charge"] * 100
        idx_col = "#E63946" if idx > 110 else ("#2A9D8F" if idx < 90 else "#2C3E50")
        age_rows.append([
            Paragraph(str(row["age_group"]),    styles["td"]),
            Paragraph(f"{int(row['count']):,}", styles["td_r"]),
            Paragraph(f"${row['mean']:,.0f}",   styles["td_r"]),
            Paragraph(f"${row['median']:,.0f}", styles["td_r"]),
            Paragraph(f'<font color="{idx_col}">{idx:.0f}</font>', styles["td_r"]),
        ])
    at = Table(age_rows, colWidths=[3.2*cm, 3*cm, 3.5*cm, 3.5*cm, 4.3*cm])
    at.setStyle(base_tbl_style())
    story += [at, PageBreak()]

    # SECTION 3: REGIONAL
    story.append(Paragraph("3. Regional Analysis", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=8))
    story += [chart_region(d), Spacer(1, 10)]

    rg = d["region_grp"]
    reg_rows = [[Paragraph(h, styles["th"]) for h in
                 ["Region", "Customers", "Avg Charge", "Median Charge", "vs Overall Avg"]]]
    for _, row in rg.iterrows():
        diff = row["mean"] - d["avg_charge"]
        dc   = "#E63946" if diff > 0 else "#2A9D8F"
        reg_rows.append([
            Paragraph(row["region"].title(),    styles["td"]),
            Paragraph(f"{int(row['count']):,}", styles["td_r"]),
            Paragraph(f"${row['mean']:,.0f}",   styles["td_r"]),
            Paragraph(f"${row['median']:,.0f}", styles["td_r"]),
            Paragraph(f'<font color="{dc}">${diff:+,.0f}</font>', styles["td_r"]),
        ])
    rt = Table(reg_rows, colWidths=[3.5*cm, 3*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    rt.setStyle(base_tbl_style())
    story += [rt, PageBreak()]

    # SECTION 4: BMI
    story.append(Paragraph("4. BMI Impact on Insurance Charges", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=8))
    story += [chart_bmi_scatter(d), Spacer(1, 8)]
    story.append(Paragraph(
        "The scatter plot reveals two distinct populations. Non-smokers (blue) maintain relatively "
        "low charges across the full BMI range. Smokers (red) cluster at much higher charge levels "
        "regardless of BMI, demonstrating that smoking status dominates BMI as a cost predictor. "
        "The obese threshold (BMI 30) is shown as a dashed line for reference.",
        styles["body"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Average Charges by BMI Category and Smoking Status", styles["subsection"]))
    bmi_rows = [[Paragraph(h, styles["th"]) for h in
                 ["BMI Category", "Smoker Avg", "Non-Smoker Avg", "Overall Avg", "Count"]]]
    for cat in ["Underweight", "Normal", "Overweight", "Obese"]:
        sub     = d["df"][d["df"]["bmi_cat"] == cat]
        s_avg   = sub[sub["smoker"] == "yes"]["charges"].mean()
        ns_avg  = sub[sub["smoker"] == "no"]["charges"].mean()
        all_avg = sub["charges"].mean()
        bmi_rows.append([
            Paragraph(cat,                                                    styles["td"]),
            Paragraph(f"${s_avg:,.0f}"  if not np.isnan(s_avg)  else "N/A", styles["td_r"]),
            Paragraph(f"${ns_avg:,.0f}" if not np.isnan(ns_avg) else "N/A", styles["td_r"]),
            Paragraph(f"${all_avg:,.0f}",                                    styles["td_r"]),
            Paragraph(f"{len(sub):,}",                                       styles["td_r"]),
        ])
    bmi_t = Table(bmi_rows, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    bmi_t.setStyle(base_tbl_style())
    story += [bmi_t, PageBreak()]

    # SECTION 5: GENDER
    story.append(Paragraph("5. Gender Breakdown", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=8))

    n_male   = d["df"][d["df"]["sex"] == "male"].shape[0]
    n_female = d["df"][d["df"]["sex"] == "female"].shape[0]
    diff_amt = abs(d["male_avg"] - d["female_avg"])
    diff_pct = diff_amt / d["avg_charge"] * 100

    gender_text = Table([[
        Paragraph("Gender plays a minor role in insurance charges compared to smoking "
                  "status, age, and region.", styles["body"]),
        Spacer(1, 8),
        Paragraph(f"- Males: <b>{d['male_pct']:.1f}%</b> of holders ({n_male:,} customers) "
                  f"| Avg charge: <b>${d['male_avg']:,.0f}</b>", styles["body"]),
        Paragraph(f"- Females: <b>{d['female_pct']:.1f}%</b> of holders ({n_female:,} customers) "
                  f"| Avg charge: <b>${d['female_avg']:,.0f}</b>", styles["body"]),
        Spacer(1, 8),
        Paragraph(
            f"The charge difference between genders is ${diff_amt:,.0f} ({diff_pct:.1f}% of the "
            "overall average) - small relative to the 4x smoking multiplier.",
            styles["body"]),
    ]], colWidths=[9 * cm])

    gender_side = Table([[chart_gender(d), gender_text]], colWidths=[8.5 * cm, 9 * cm])
    gender_side.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0,  -1), 10),
    ]))
    story += [gender_side, PageBreak()]

    # SECTION 6: TOP 10
    story.append(Paragraph("6. Top 10 Highest-Cost Policy Holders", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID, spaceAfter=8))
    story.append(Paragraph(
        "All top 10 highest individual charges share a common profile: smokers, typically older age, "
        "often with higher BMI. This confirms smoking status as the primary risk indicator for extreme charges.",
        styles["body"]))
    story.append(Spacer(1, 8))

    top_rows = [[Paragraph(h, styles["th"]) for h in
                 ["#", "Age", "Sex", "BMI", "Children", "Smoker", "Region", "Annual Charge"]]]
    for i, (_, row) in enumerate(d["top10"].iterrows(), 1):
        s_col = "#E63946" if row["smoker"] == "yes" else "#2D7DD2"
        top_rows.append([
            Paragraph(str(i),                                                          styles["td"]),
            Paragraph(str(row["age"]),                                                 styles["td"]),
            Paragraph(row["sex"].title(),                                              styles["td"]),
            Paragraph(f"{row['bmi']:.1f}",                                            styles["td_r"]),
            Paragraph(str(row["children"]),                                            styles["td"]),
            Paragraph(f'<font color="{s_col}"><b>{row["smoker"].title()}</b></font>', styles["td"]),
            Paragraph(row["region"].title(),                                           styles["td"]),
            Paragraph(f"${row['charges']:,.0f}",                                       styles["td_r"]),
        ])
    tt = Table(top_rows, colWidths=[1*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 2.2*cm, 3*cm, 4.3*cm])
    tt.setStyle(base_tbl_style())
    story.append(tt)

    doc.build(story, onFirstPage=cb, onLaterPages=cb)
    print(f"  Saved to : {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health Insurance Charges BI Report")
    parser.add_argument("--input",  default="insurance.csv")
    parser.add_argument("--output", default="insurance_report.pdf")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: '{args.input}' not found.")
    else:
        print("\n=== Health Insurance BI Report Generator ===")
        build_report(args.input, args.output)
        print("=== Done! ===\n")