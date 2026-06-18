from fpdf import FPDF
import pandas as pd

import numpy as np


def get_summary_statistics(df):
    """

    Computes mathematical summary statistics (mean, min, max, quartiles)

    and converts them directly into an automatically styled Bootstrap HTML table string.

    """

    # .describe(include='all') captures numerical and categorical columns automatically

    summary_df = df.describe(include='all')

    # Replace empty NaN tracking values with a clean hyphen for cleaner UI display

    summary_df = summary_df.fillna("-")

    # Convert dataframe into styled bootstrap table structures

    return summary_df.to_html(classes="table table-bordered table-striped table-hover table-sm text-center small")


def detect_missing_values(df):
    """

    Finds which columns have empty or missing fields and calculates their percentage.

    """

    missing_report = []

    # Calculate sum of null values across all features

    null_counts = df.isnull().sum()

    for column, count in null_counts.items():

        if count > 0:

            percentage = (count / len(df)) * 100

            missing_report.append({

                "column": column,

                "count": int(count),

                "percentage": f"{percentage:.1f}%"

            })

    return missing_report


def identify_outliers(df):
    """

    Uses the Interquartile Range (IQR) rule to scan all numerical features

    and mathematically flag data rows containing extreme outlier points.

    """

    outlier_report = []

    # Filter to look strictly at numerical columns

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:

        # Drop missing records temporarily from the column calculation to prevent mathematical skewing

        col_data = df[col].dropna()

        if len(col_data) < 4:

            continue

        # Extract the 25th percentile (Q1) and 75th percentile (Q3)

        Q1 = col_data.quantile(0.25)

        Q3 = col_data.quantile(0.75)

        IQR = Q3 - Q1

        # Formulate boundary lines

        lower_bound = Q1 - 1.5 * IQR

        upper_bound = Q3 + 1.5 * IQR

        # Filter rows that bleed past the upper or lower fences

        outliers = col_data[(col_data < lower_bound) |
                            (col_data > upper_bound)]

        if len(outliers) > 0:

            outlier_report.append({

                "column": col,

                "count": len(outliers),

                "min_outlier": float(outliers.min()),

                "max_outlier": float(outliers.max())

            })

    return outlier_report


def generate_auto_insights(df):
    """

    Scans the numerical correlations of a DataFrame and auto-generates

    plain-English insights about strong positive or inverse trends.

    """

    insights = []

    # Isolate strictly numerical columns

    numeric_df = df.select_dtypes(include=[np.number])

    # We need at least two numeric columns to analyze relationships

    if numeric_df.shape[1] < 2:

        return ["Not enough numerical data columns present to compute relational trends."]

    # Calculate the Pearson correlation matrix coefficients (-1.0 to 1.0)

    corr_matrix = numeric_df.corr()

    # Scan relationships across the matrix grid

    for i in range(len(corr_matrix.columns)):

        for j in range(i):

            score = corr_matrix.iloc[i, j]

            col1 = corr_matrix.columns[i]

            col2 = corr_matrix.columns[j]

            # Identify high positive correlation

            if score > 0.70 and score < 1.0:

                insights.append(

                    f"📈 <strong>Strong positive trend:</strong> '{col1}' and '{col2}' move closely together ({score:.2f}). As one increases, the other typically rises."

                )

            # Identify high negative (inverse) correlation

            elif score < -0.70 and score > -1.0:

                insights.append(

                    f"📉 <strong>Strong inverse trend:</strong> '{col1}' and '{col2}' have an opposite relationship ({score:.2f}). When one goes up, the other tends to fall."

                )

    # Fallback if no columns are heavily correlated

    if not insights:

        insights.append(
            "✓ <strong>Uniform variance:</strong> No strong linear correlations or anomalies detected among the numerical features.")

    return insights


from fpdf import FPDF

from fpdf import FPDF

def create_pdf_report(filename, total_rows, total_cols, insights_list, missing_list, outlier_list):
    """
    Assembles data metrics into a compiled FPDF class structure.
    """
    pdf = FPDF()
    pdf.add_page()

    # --- Header Style Configuration ---
    pdf.set_font("Helvetica", style="B", size=22)
    pdf.set_text_color(21, 128, 61) # Calming Emerald Green Accent
    pdf.cell(0, 15, text="Data Analytics Executive Summary", ln=True, align="C")

    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, text=f"Document Target Asset: {str(filename)}", ln=True, align="C")
    pdf.ln(10)

    # --- Section 1: Dimensions Profile ---
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, text="1. Dataset Dimensions Profile", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, text=f"- Total Record Rows Captured: {str(total_rows)}", ln=True)
    pdf.cell(0, 8, text=f"- Total Feature Columns Discovered: {str(total_cols)}", ln=True)
    pdf.ln(6)

    # --- Section 2: Calculated Analytics ---
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, text="2. System Generated Analytical Insights", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", size=11)
    if insights_list:
        for insight in insights_list:
            clean_insight = str(insight).replace("<strong>", "").replace("</strong>", "").replace("📈", "").replace("📉", "").replace("✓", "")
            pdf.multi_cell(0, 7, text=f"- {clean_insight}")
    else:
        pdf.cell(0, 8, text="- No baseline linear trends computed.", ln=True)
    pdf.ln(6)

    # --- Section 3: System Logging ---
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, text="3. Data Integrity & Anomaly Logs", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", size=11)

    if isinstance(missing_list, list) and len(missing_list) > 0:
        pdf.cell(0, 8, text="Empty or Null Variables Discovered:", ln=True)
        for item in missing_list:
            if isinstance(item, dict) and "column" in item:
                pdf.cell(0, 7, text=f"  * Column '{item['column']}': {item.get('count', 0)} instances missing ({item.get('percentage', '0%')})", ln=True)
    else:
        pdf.cell(0, 8, text="* Zero missing structural fields flagged across the record grid.", ln=True)

    pdf.ln(2)

    if isinstance(outlier_list, list) and len(outlier_list) > 0:
        pdf.cell(0, 8, text="Statistical Extreme Variance Points (IQR Rule):", ln=True)
        for item in outlier_list:
            if isinstance(item, dict) and "column" in item:
                pdf.cell(0, 7, text=f"  * Column '{item['column']}': {item.get('count', 0)} outlier records detected.", ln=True)
    else:
        pdf.cell(0, 8, text="* Zero extreme value anomalies flagged outside boundary limits.", ln=True)

    # Return the clean instance back to the calling controller route
    return pdf
