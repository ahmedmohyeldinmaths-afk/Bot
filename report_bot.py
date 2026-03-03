import streamlit as st
import google.generativeai as genai
from docx import Document
from fpdf import FPDF
import io

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Academic Report Bot", page_icon="🎓")

# --- 2. إعداد مفتاح جوجل ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

# --- 3. دوال النظام ---
def get_system_prompt(level, field):
    prompt = f"You are an expert academic writer in {field}. "
    if level == "Undergraduate":
        prompt += "Write for an Undergraduate level. Focus on definitions and core concepts. Structure: Introduction, Body, Conclusion."
    elif level == "Masters":
        prompt += "Write for a Masters level. Focus on analysis, methodology, and industry application."
    elif level == "Ph.D.":
        prompt += "Write for a Ph.D. level. Focus on novelty, theoretical contribution, and rigorous academic tone."
    return prompt

def create_docx(text):
    doc = Document()
    doc.add_heading('Technical Report', 0)
    # تنظيف بسيط للنص
    clean_text = text.replace('**', '').replace('##', '')
    for line in clean_text.split('\n'):
        if line.strip():
            doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    return bio

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Technical Report", ln=True, align='C')
    pdf.ln(10)
    # ترميز لاتيني بسيط لتجنب الأخطاء
    safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 4. واجهة التطبيق ---
st.title("🎓 Academic Report Generator (Gemini Pro)")

level = st.sidebar.selectbox("Qualification Level", ["Undergraduate", "Masters", "Ph.D."])
field = st.sidebar.text_input("Field of Study", "Computer Science")

if prompt := st.chat_input("Enter report topic..."):
    if not api_key:
        st.error("⚠️ Please enter a Google API Key.")
    else:
        st.chat_message("user").markdown(prompt)
        
        try:
            # إعداد جوجل Gemini
            genai.configure(api_key=api_key)
            
            # --- التغيير هنا: استخدام الموديل المستقر ---
            model = genai.GenerativeModel('gemini-pro')
            
            full_prompt = f"{get_system_prompt(level, field)}\n\nTopic: {prompt}"
            
            with st.chat_message("assistant"):
                with st.spinner("Generating report..."):
                    response = model.generate_content(full_prompt)
                    report_text = response.text
                    st.markdown(report_text)
            
            # أزرار التحميل
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📄 Word Doc", create_docx(report_text).getvalue(), "report.docx")
            with col2:
                st.download_button("📕 PDF File", create_pdf(report_text), "report.pdf")

        except Exception as e:
            st.error(f"Error: {e}")
