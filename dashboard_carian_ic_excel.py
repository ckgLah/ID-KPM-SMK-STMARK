import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from datetime import datetime
import os

# ==========================
# TEMA & CSS
# ==========================
st.set_page_config(page_title="Dashboard Delima SMK ST MARK 2025", layout="centered")

st.markdown("""
<style>
.header {display:flex; align-items:center;}
.header img {width:80px; margin-right:20px;}
.header h1 {color:darkgoldenrod;}
.info-box {
    background-color: rgba(240,240,240,0.6);
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #009944;
    margin-top: 10px;
    margin-bottom: 10px;
    color: darkgoldenrod;
}
.highlight {background-color: #00994433; padding:3px; border-radius:5px;}
.fade-item {animation: fadeIn 0.6s ease-in-out; margin:2px 0;}
@keyframes fadeIn {from {opacity:0;} to {opacity:1;}}
</style>
""", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================
st.markdown("""
<style>
.header {display:flex; align-items:center; margin-bottom:20px;}
.header img {width:80px; margin-right:20px;}
.header h1 {color: darkgoldenrod !important; margin:0;}  /* Tukar tajuk hijau keemasan */
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo_stmark.png", width=80)
st.markdown("<h1>Dashboard Delima SMK ST MARK 2025</h1>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ==========================
# LOAD DATA
# ==========================
excel_path = "senarai_pelajar.xlsx"
if not os.path.exists(excel_path):
    st.error(f"❌ Fail Excel tidak dijumpai: {excel_path}")
else:
    # Pastikan NoKadPengenalan dibaca sebagai string
    df = pd.read_excel(excel_path, dtype={"NoKadPengenalan": str}).fillna("")

# ==========================
# FUNGSI PADAM INPUT
# ==========================
def reset_ic():
    st.session_state["ic_input_field"] = ""

# ==========================
# INPUT DAN CARIAN
# ==========================
ic_input = st.text_input("Masukkan No Kad Pengenalan:", key="ic_input_field")

if st.button("Cari"):
    if ic_input.strip() == "":
        st.warning("⚠️ Sila masukkan No Kad Pengenalan terlebih dahulu.")
    else:
        ic_input_str = ic_input.strip().zfill(12)
        result = df[df["NoKadPengenalan"].str.strip() == ic_input_str]

        if not result.empty:
            maklumat = result.iloc[0]

            # PAPAR MAKLUMAT DALAM SATU KOTAK
            info_html = f"""
            <div class="info-box">
                <p class="fade-item"><b>Nama:</b> {maklumat['Nama']}</p>
                <p class="fade-item"><b>Emel:</b> <span class='highlight'>{maklumat['Emel']}</span></p>
                <p class="fade-item"><b>No Kad Pengenalan:</b> {maklumat['NoKadPengenalan']}</p>
                <p class="fade-item"><b>Kata Laluan:</b> <span class='highlight'>{maklumat['Katalaluan']}</span></p>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)

            # ==========================
            # JANA PDF DENGAN WATERMARK TRANSPARENT
            # ==========================
            def generate_pdf(data):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                # LOGO WATERMARK TRANSPARENT
                try:
                    logo = ImageReader("logo_stmark.png")
                    c.saveState()
                    c.translate(width / 2, height / 2)
                    c.rotate(30)
                    c.setFillAlpha(0.1)  # transparent
                    c.drawImage(logo, -200, -200, width=400, height=400, mask='auto', preserveAspectRatio=True)
                    c.restoreState()
                    c.setFillAlpha(1)  # reset alpha
                except:
                    pass

                # TAJUK
                c.setFont("Helvetica-Bold", 18)
                c.setFillColor(colors.darkgreen)
                c.drawCentredString(width / 2, height - 80, "SLIP MAKLUMAT ID DELIMA PELAJAR")

                # BINGKAI MAKLUMAT
                box_x, box_y = 70, height - 200
                box_width, box_height = width - 140, 130
                c.setStrokeColor(colors.darkgreen)
                c.setLineWidth(2)
                c.roundRect(box_x, box_y - box_height + 20, box_width, box_height, 10, stroke=1, fill=0)

                # Tuliskan maklumat
                c.setFont("Helvetica", 12)
                y = box_y
                c.drawString(80, y, f"Nama: {data['Nama']}"); y -= 25
                c.drawString(80, y, f"No Kad Pengenalan: {data['NoKadPengenalan']}"); y -= 25
                c.drawString(80, y, f"Emel: {data['Emel']}"); y -= 25
                c.drawString(80, y, f"Kata Laluan: {data['Katalaluan']}"); y -= 25
                c.drawString(80, y, f"Tarikh & Masa Jana: {now}")

                # CATATAN
                c.setFillColor(colors.darkgoldenrod)
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(80, 80, "Slip ini dijana secara automatik oleh Dashboard Delima SMK ST MARK 2025.")
                c.save()
                buffer.seek(0)
                return buffer

            pdf_buffer = generate_pdf(maklumat)
            st.download_button(
                label="📄 Muat Turun Slip Maklumat ID Delima Pelajar",
                data=pdf_buffer,
                file_name=f"Slip_Maklumat_{maklumat['Nama'].replace(' ','_')}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("❌ No Kad Pengenalan tidak dijumpai dalam senarai.")

# ==========================
# BUTANG PADAM INPUT
# ==========================
st.button("Padam Input", on_click=reset_ic)
