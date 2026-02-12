import streamlit as st
import sqlite3
import random
import os
from datetime import date
from google import genai

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Hospital appointment", page_icon="🏥", layout="centered")

# ---------------- CUSTOM UI ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
html, body, [class*="css"] {font-family:'Poppins',sans-serif;}

.stApp {background: linear-gradient(135deg,#e0f2fe,#f8fafc);}

.card {
    background:white;
    padding:25px;
    border-radius:18px;
    box-shadow:0 10px 25px rgba(0,0,0,0.12);
    margin-bottom:20px;
}

.stButton>button {
    width:100%;
    border-radius:12px;
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    color:white;
    font-weight:600;
    padding:12px;
    border:none;
}

.successBox {background:#dcfce7;padding:15px;border-radius:12px;color:#166534;}
.warnBox {background:#fee2e2;padding:15px;border-radius:12px;color:#991b1b;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;color:#0f172a;'>🏥 Smart Hospital Appointment Assistant</h1>
<p style='text-align:center;color:gray;'>Book appointment & get instant AI temporary relief guidance</p>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments(
ap_no INTEGER PRIMARY KEY,
name TEXT,
age INTEGER,
doctor TEXT,
date TEXT,
problem TEXT
)

""")


conn.commit()

# ---------------- GEMINI ----------------
client = genai.Client(api_key="AIzaSyBjm3gte_0prYSlIpMLbLtRJiegFj7V3ao")

def get_ai_relief(problem):
    prompt = f"""
role:you are a ai appointment booker and your are also temporary relief advisor,
Suggest ONLY home remedies for temporary relief.act like a friend who can also speak personal advices.
and also tell what to do and what not to do 
No medicines.
Add warning this is not medical treatment.
give in some short ans and minimal so that the patient cannot feel bore to read.

Problem: {problem}
age :{age}
name:{name}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ---------------- SESSION ----------------
if "verified" not in st.session_state:
    st.session_state.verified = False
if "otp" not in st.session_state:
    st.session_state.otp = None

# ---------------- OTP ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📱 Mobile Verification")

mobile = st.text_input("Mobile Number", placeholder="Enter 10 digit number")
    
if st.button("Send OTP"):
    if len(mobile) == 10:
        st.session_state.otp = random.randint(1000,9999)
        st.success(f"Demo OTP: {st.session_state.otp}")
    else:
        st.warning("Enter valid mobile number")

otp = st.text_input("Enter OTP", placeholder="4 digit code")

if st.button("Verify"):
    if otp == str(st.session_state.get("otp")):
        st.session_state.verified = True
        st.success("Verified Successfully")
    else:
        st.error("Invalid OTP")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BOOK APPOINTMENT ----------------
if st.session_state.verified:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Book Appointment")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Patient Name", placeholder="Full name")
        age = st.number_input("Age", 1, 120)

    with col2:
        doctor = st.selectbox("Select Doctor", ["Dr. Sharma","Dr. Khan","Dr. Patil","Dr. Mehta"])
        ap_date = st.date_input("Appointment Date", min_value=date.today())

    problem = st.text_area("Describe Problem",
                           placeholder="Example: headache since morning, eye strain...")

    if st.button("Confirm Appointment"):
        ap_no = random.randint(1000,9999)

        cursor.execute("INSERT INTO appointments VALUES(?,?,?,?,?,?)",
                       (ap_no,name,age,doctor,str(ap_date),problem))
        conn.commit()

        st.success(f"Appointment Booked! Your ID: {ap_no}")

        with st.spinner("🔍Analyzing your problem using AI ..."):
            advice = get_ai_relief(problem)

        st.markdown(f'<div class="successBox">{advice}</div>', unsafe_allow_html=True)
        st.markdown('<div class="warnBox">Temporary relief only. Visit doctor.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SEARCH ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔍 Search Appointment")

search_id = st.text_input("Appointment Number", placeholder="Enter ID")

if st.button("Search"):
    data = cursor.execute("SELECT * FROM appointments WHERE ap_no=?",(search_id,)).fetchone()
    if data:
        st.success("Appointment Found")
        st.write("Name:",data[1])
        st.write("Doctor:",data[3])
        st.write("Date:",data[4])
        st.write("Problem:",data[5])
    else:
        st.error("No record found")

st.markdown('</div>', unsafe_allow_html=True)

st.caption("- Made by Saikiran Jinde")