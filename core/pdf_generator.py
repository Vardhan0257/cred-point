from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from datetime import datetime
from io import BytesIO


def generate_cpe_report(holder_name, certification, member_id, activity):
    """
    Generates a CPE report in official certification-body style and returns a BytesIO buffer.
    """
    buffer = BytesIO()
    width, height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    # Holder Info (title removed)
    y = height - 1.5*inch
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, y, f"Certification Holder Name: {holder_name}")
    y -= 0.4*inch
    c.drawString(1*inch, y, f"Certification ID / Member ID: {member_id}")
    y -= 0.4*inch
    c.drawString(1*inch, y, f"Certification: {certification}")

    # Section Line
    y -= 0.6*inch
    c.setStrokeColor(colors.black)
    c.line(1*inch, y, width-1*inch, y)

    # Normalize to list
    activities = activity if isinstance(activity, list) else [activity]

    for act in activities:
        # Activity Section
        y -= 0.8*inch
        c.setFont("Helvetica-Bold", 13)
        c.drawString(1*inch, y, "CPE Activity Details")

        c.setFont("Helvetica", 11)
        y -= 0.4*inch
        c.drawString(1*inch, y, f"Activity Title / Name: {act.get('title','')}")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"Organizer / Institution: {act.get('provider','')}")

        # --- Date(s) Attended (use activity_date if present; fallback to start/end) ---
        y -= 0.3*inch
        date_text = ""
        act_date = act.get('activity_date')
        if act_date:
            try:
                dt = datetime.fromisoformat(str(act_date)).date()
                date_text = dt.strftime('%d/%m/%Y')
            except Exception:
                try:
                    date_text = act_date.strftime('%d/%m/%Y')
                except Exception:
                    date_text = str(act_date)
        else:
            s = str(act.get('start_date', '') or '')
            e = str(act.get('end_date', '') or '')
            date_text = f"{s} - {e}".strip(" -")

        c.drawString(1*inch, y, f"Date(s) Attended: {date_text}")

        # --- Removed Duration (Hours) line ---

        y -= 0.3*inch
        c.drawString(1*inch, y, f"Type of Activity: {act.get('activity_type','')}")
        y -= 0.3*inch
        c.drawString(1*inch, y, "Description / Summary:")
        y -= 0.3*inch

        text_obj = c.beginText(1.2*inch, y)
        text_obj.setFont("Helvetica", 10)
        text_obj.textLines(act.get("description", ""))
        c.drawText(text_obj)

        # Move below description
        y = text_obj.getY() - 0.3*inch
        c.setFont("Helvetica", 11)

        # Supporting docs + QR (file name removed)
        proof_name = act.get('proof_file') or act.get('proof') or ''
        proof_url = ''
        if proof_name:
            try:
                from flask import url_for
                proof_url = url_for('static', filename=f'uploads/{proof_name}', _external=True)
            except Exception:
                proof_url = f"/static/uploads/{proof_name}"

        c.drawString(1*inch, y, "Supporting Documents Attached:")

        if proof_url:
            qr_size = 0.9 * inch
            qr_widget = qr.QrCodeWidget(proof_url)
            bounds = qr_widget.getBounds()
            bw = bounds[2] - bounds[0]
            bh = bounds[3] - bounds[1]
            qr_drawing = Drawing(qr_size, qr_size, transform=[qr_size/bw, 0, 0, qr_size/bh, 0, 0])
            qr_drawing.add(qr_widget)

            qr_x = 1 * inch
            qr_y = y - qr_size - 0.1*inch
            renderPDF.draw(qr_drawing, c, qr_x, qr_y)
            y = qr_y - 0.3*inch
        else:
            y -= 0.5*inch

        # Total CPE (use cpe_points)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, f"Total CPEs Earned: {act.get('cpe_points','')}")
        y -= 0.2*inch

        # Declaration
        y -= 0.8*inch
        c.setFont("Helvetica", 11)
        c.drawString(1*inch, y, "Declaration:")
        y -= 0.4*inch
        c.setFont("Helvetica", 10)
        c.drawString(1.2*inch, y, "I hereby declare that the above information is true and accurate to the best")
        y -= 0.3*inch
        c.drawString(1.2*inch, y, "of my knowledge. I understand that providing false information may affect")
        y -= 0.3*inch
        c.drawString(1.2*inch, y, "my certification status.")

        # Signature + Date (today)
        y -= 1*inch
        c.setFont("Helvetica", 11)
        c.drawString(1*inch, y, "Signature: ______________________________")
        c.drawString(width/2 + 0.5*inch, y, f"Date: {datetime.now().strftime('%d/%m/%Y')}")

        if act != activities[-1]:
            c.showPage()
            y = height - 1.5*inch

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
