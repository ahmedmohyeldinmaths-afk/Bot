import streamlit as st
import google.generativeai as genai
from docx import Document
from fpdf import FPDF
import io

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Academic Report Bot", page_icon="🎓")

# --- 2. إعداد مفتاح جوجل ---
# يحاول جلب المفتاح من Secrets، وإذا لم يجده يطلبه من المستخدم
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

# --- 3. دوال النظام ---
def get_system_prompt(level, field):
    if level == "Undergraduate":
        return f"You are a tutor for an Undergraduate student in {field}. Write a report focusing on fundamental concepts. Structure: Intro, Core Concepts, Conclusion."
    elif level == "Masters":
        return f"You are a consultant for a Masters student in {field}. Write a report focusing on industry application and critical analysis."
    elif level == "Ph.D.":
        return f"You are a research associate for a Ph.D. candidate in {field}. Write a rigorous report focusing on novelty and theoretical contribution."
    return f"You are a technical writer in {field}."

def create_docx(text):
    doc = Document()
    doc.add_heading('Technical Report', 0)
    # تنظيف النص من النجوم الخاصة بـ Markdown
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
    # FPDF لا يدعم العربية أو الرموز المعقدة بشكل مباشر، لذا ننظف النص
    safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 4. واجهة التطبيق ---
st.title("🎓 Academic Report Generator (Free Version)")

level = st.sidebar.selectbox("Qualification Level", ["Undergraduate", "Masters", "Ph.D."])
field = st.sidebar.text_input("Field of Study", "Computer Science")

# بدء المحادثة
if prompt := st.chat_input("Enter report topic..."):
    if not api_key:
        st.error("⚠️ Please enter a Google API Key.")
    else:
        # عرض رسالة المستخدم
        st.chat_message("user").markdown(prompt)
        
        try:
            # إعداد جوجل Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') # موديل سريع ومجاني
            
            # تجميع التعليمات
            full_prompt = f"{get_system_prompt(level, field)}\n\nTopic: {prompt}"
            
            with st.chat_message("assistant"):
                with st.spinner("Writing report..."):
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
