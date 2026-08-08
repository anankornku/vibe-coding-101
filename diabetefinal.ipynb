import streamlit as st
import sqlite3
import statistics

# ==========================================
# 1. DATA ACCESS LAYER (MODEL)
# จัดการฐานข้อมูล SQLite3 และการทำความสะอาดข้อมูลเบื้องต้น
# ==========================================
class Patient:
    def __init__(self, pid, name, glucose, bmi, age, bp):
        self.id = pid
        self.name = name
        self.glucose = glucose
        self.bmi = bmi
        self.age = age
        self.blood_pressure = bp

class PatientRepository:
    def __init__(self, db_name="patients.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    glucose REAL,
                    bmi REAL,
                    age INTEGER,
                    blood_pressure REAL
                )
            """)
            conn.commit()
        if not self.get_all_patients():
            self._load_and_clean_mock_data()

    def _load_and_clean_mock_data(self):
        raw_data = [
            {"id": 1, "name": "John Doe", "Glucose": 95, "BMI": 22.5, "Age": 30, "BloodPressure": 118},
            {"id": 2, "name": "Jane Smith", "Glucose": 115, "BMI": 0.0, "Age": 52, "BloodPressure": 135},
            {"id": 3, "name": "Robert Lee", "Glucose": 140, "BMI": 33.2, "Age": 62, "BloodPressure": 145},
            {"id": 4, "name": "Maria Garcia", "Glucose": 88, "BMI": 24.0, "Age": 41, "BloodPressure": 112}
        ]

        valid_bmis = [p["BMI"] for p in raw_data if p["BMI"] > 0]
        median_bmi = statistics.median(valid_bmis) if valid_bmis else 22.0

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            for item in raw_data:
                bmi = item["BMI"]
                if bmi == 0 or bmi == 0.0:
                    bmi = median_bmi
                cursor.execute("""
                    INSERT OR REPLACE INTO patients (id, name, glucose, bmi, age, blood_pressure)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (item["id"], item["name"], item["Glucose"], bmi, item["Age"], item["BloodPressure"]))
            conn.commit()

    def get_all_patients(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, glucose, bmi, age, blood_pressure FROM patients")
            rows = cursor.fetchall()
            return [Patient(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]

    def get_patient_by_id(self, pid):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, glucose, bmi, age, blood_pressure FROM patients WHERE id = ?", (pid,))
            row = cursor.fetchone()
            if row:
                return Patient(row[0], row[1], row[2], row[3], row[4], row[5])
        return None

    def update_patient(self, patient):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patients SET glucose = ?, bmi = ?, age = ?, blood_pressure = ? WHERE id = ?
            """, (patient.glucose, patient.bmi, patient.age, patient.blood_pressure, patient.id))
            conn.commit()


# ==========================================
# 2. BUSINESS LOGIC LAYER (SERVICE)
# จัดการกฎเกณฑ์การตัดสินใจทางคลินิกและการให้คะแนน
# ==========================================
class RiskScoringService:
    @staticmethod
    def evaluate_metric(metric_name, value):
        if metric_name == "Glucose":
            if value < 100: return 0
            elif value <= 125: return 1
            else: return 2
        elif metric_name == "BMI":
            if value < 25.0: return 0
            elif value <= 29.9: return 1
            else: return 2
        elif metric_name == "Age":
            if value < 45: return 0
            elif value <= 59: return 1
            else: return 2
        elif metric_name == "BloodPressure":
            if value < 120: return 0
            elif value <= 139: return 1
            else: return 2
        return 0

    @classmethod
    def calculate_risk(cls, patient):
        scores = {
            "Glucose": cls.evaluate_metric("Glucose", patient.glucose),
            "BMI": cls.evaluate_metric("BMI", patient.bmi),
            "Age": cls.evaluate_metric("Age", patient.age),
            "BloodPressure": cls.evaluate_metric("BloodPressure", patient.blood_pressure)
        }
        total_score = sum(scores.values())
        
        if total_score <= 2:
            category = "Low Risk"
        elif total_score <= 5:
            category = "Moderate Risk"
        else:
            category = "High Risk"
            
        return {
            "breakdown": scores,
            "total_score": total_score,
            "category": category
        }


# ==========================================
# 3 & 4. PRESENTATION & ORCHESTRATION LAYER (UI & CONTROLLER)
# ควบคุมการแสดงผลผ่าน Streamlit และประสานการทำงานร่วมกับฐานข้อมูล
# ==========================================
def main():
    st.set_page_config(page_title="Diabetes Risk Scoring System", page_icon="🏥", layout="centered")
    
    st.title("🏥 Diabetes Risk Scoring System")
    st.markdown("ระบบประเมินความเสี่ยงโรคเบาหวาน (Streamlit + SQLite3 Persistence)")
    st.markdown("---")

    repository = PatientRepository()
    service = RiskScoringService()

    patients = repository.get_all_patients()
    
    patient_options = {f"ID: {p.id} - {p.name}": p.id for p in patients}
    selected_label = st.selectbox("📌 เลือกผู้ป่วยที่ต้องการประเมินความเสี่ยง:", list(patient_options.keys()))
    selected_id = patient_options[selected_label]
    
    patient = repository.get_patient_by_id(selected_id)

    if patient:
        st.subheader(f"📋 ข้อมูลทางคลินิกปัจจุบัน: {patient.name} (ID: {patient.id})")
        
        with st.form(key="patient_metric_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_glucose = st.number_input("Glucose (mg/dL)", value=int(patient.glucose), min_value=0, max_value=300)
                new_bmi = st.number_input("BMI", value=float(patient.bmi), min_value=0.0, max_value=60.0, format="%.1f")
            with col2:
                new_age = st.number_input("Age (ปี)", value=int(patient.age), min_value=0, max_value=120)
                new_bp = st.number_input("Blood Pressure (mmHg)", value=int(patient.blood_pressure), min_value=0, max_value=250)
            
            submit_button = st.form_submit_button(label="🔍 คำนวณคะแนนความเสี่ยง")

        if submit_button:
            patient.glucose = new_glucose
            patient.bmi = new_bmi
            patient.age = new_age
            patient.blood_pressure = new_bp
            
            # บันทึกข้อมูลที่แก้ไขลง SQLite3 Database ทันที
            repository.update_patient(patient)

            evaluation = service.calculate_risk(patient)
            score = evaluation["total_score"]
            category = evaluation["category"]

            if category == "Low Risk":
                color = "#2ecc71"
            elif category == "Moderate Risk":
                color = "#f39c12"
            else:
                color = "#e74c3c"

            st.markdown("---")
            
            report_html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; border-radius: 8px; background-color: #f9f9f9; border-left: 8px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #2c3e50; text-align: center;">MEDICAL DIAGNOSTIC REPORT</h3>
                <hr style="border: 0; border-top: 2px solid #ccc;">
                <p style="font-size: 16px;"><b>Patient ID:</b> {patient.id} ({patient.name})</p>
                <p style="font-size: 16px;"><b>Cumulative Score:</b> {score} pts</p>
                <p style="font-size: 16px;"><b>Risk Category:</b> <span style="color: {color}; font-weight: bold;">{category.upper()}</span></p>
                <hr style="border: 0; border-top: 2px solid #ccc;">
                <p style="font-size: 12px; color: #e74c3c; text-align: center; font-weight: bold; margin-bottom: 0;">[!] CONFIDENTIAL INFORMATION [!]</p>
            </div>
            """
            st.markdown(report_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()