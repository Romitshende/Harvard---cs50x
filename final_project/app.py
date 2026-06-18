import os
from flask import Flask, render_template, request, redirect, flash, Response
import pandas as pd
import json

# Import calculation engine parameters
from analytics import get_summary_statistics, detect_missing_values, identify_outliers, generate_auto_insights

app = Flask(__name__)
app.secret_key = "cs50_analytics_secret_key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("System error: Missing file field payload.")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("Please choose a file before clicking process.")
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            try:
                # 1. Stream the CSV file straight into a Pandas DataFrame
                df = pd.read_csv(file)

                # 2. Run calculations engines
                stats_html = get_summary_statistics(df)
                missing_report = detect_missing_values(df)
                outlier_report = identify_outliers(df)
                auto_insights = generate_auto_insights(df)

                # 3. Restructure numeric data arrays safely to handle high-fidelity cross-filtering directly in client memory
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                chart_data_dict = {}

                if len(numeric_cols) > 0:
                    for col in numeric_cols:
                        # Drop NaN metrics from array lists to prevent runtime rendering faults in Plotly
                        chart_data_dict[col] = df[col].dropna().tolist()

                # 4. Render the optimized light layout dashboard view template
                return render_template(
                    "dashboard.html",
                    filename=file.filename,
                    rows=df.shape[0],
                    cols=df.shape[1],
                    stats_table=stats_html,
                    missing_data=missing_report,
                    outliers=outlier_report,
                    insights=auto_insights,
                    chart_json=json.dumps(chart_data_dict),
                    has_numeric=len(numeric_cols) > 0
                )

            except Exception as e:
                flash(f"Error parsing database contents: {str(e)}")
                return redirect(request.url)

        flash("File validation rejected. Please supply a correctly structured .csv file asset.")
        return redirect("/")
    else:
        return render_template("index.html")


from analytics import create_pdf_report

import json
import io  # <-- Make sure to import io at the top of your app.py file
from flask import Flask, request, flash, redirect, make_response

import json
from flask import Flask, request, flash, redirect, make_response

import json
import io  # <-- Ensure you have 'import io' at the top of your app.py file
from flask import Flask, request, flash, redirect, send_file

@app.route("/export", methods=["POST"])
def export():
    try:
        # 1. Pull core layout values safely
        filename = request.form.get("filename", "dataset")
        rows = request.form.get("rows", "0")
        cols = request.form.get("cols", "0")

        # 2. Extract client list inputs
        insights = request.form.getlist("insights")
        if not insights:
            insights = [request.form.get("insights", "No trends computed.")]

        # 3. Defensive raw string parsing
        try:
            missing_raw = request.form.get("missing_data", "[]")
            missing_data = json.loads(missing_raw) if missing_raw else []
        except Exception:
            missing_data = []

        try:
            outliers_raw = request.form.get("outliers", "[]")
            outliers = json.loads(outliers_raw) if outliers_raw else []
        except Exception:
            outliers = []

        # 4. Generate data array natively from analytics.py
        pdf_data = create_pdf_report(filename, rows, cols, insights, missing_data, outliers)

        # 5. Type checking cast to ensure raw byte matching patterns
        if isinstance(pdf_data, (bytes, bytearray)):
            final_bytes = bytes(pdf_data)
        elif isinstance(pdf_data, str):
            final_bytes = pdf_data.encode('latin1')
        else:
            final_bytes = bytes(pdf_data.output())

        # 6. FIXED FORMAT SYSTEM: Wrap bytes safely inside an in-memory stream buffer
        mem_stream = io.BytesIO(final_bytes)
        mem_stream.seek(0) # Reset tracking pointer cleanly back to the beginning of the file

        # 7. Hand over stream directly to Flask's native download security controller
        return send_file(
            mem_stream,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{filename}_summary_report.pdf"
        )

    except Exception as e:
        print(f"CRITICAL API ERROR: {str(e)}")
        flash(f"Failed to generate report document file layout: {str(e)}")
        return redirect("/")
