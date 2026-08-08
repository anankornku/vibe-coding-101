import streamlit as st
import statistics

# ==========================================
# 1. DATA ACCESS LAYER (MODEL)
# จัดการข้อมูลจำลองและการทำความสะอาดข้อมูลเบื้องต้น
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
    def __init__(self):
        # ใช้ st.session_state เพื่อคงสภาพข้อมูลไว้ตลอดการใช้งานใน Session
        if "patients_data" not in st.session_state:
            raw_data = [
                {"id": 1, "name": "John Doe", "Glucose": 95, "BMI": 22.5, "Age": 30, "BloodPressure": 118},
                {"id": 2, "name": "Jane Smith", "Glucose": 115, "BMI": 0.0, "Age": 52, "BloodPressure": 135}, # BMI = 0 (ต้องทำความสะอาดข้อมูล)
                {"id": 3, "name": "Robert Lee", "Glucose": 140, "BMI": 33.2, "Age": 62, "BloodPressure": 145},
                {"id": 4, "name": "Maria Garcia", "Glucose": 88, "BMI": 24.0, "Age": 41, "BloodPressure": 112}
            ]
            
            # คำนวณ Median ของ BMI ที่ถูกต้องมาแทนที่ค่า 0
            valid_bmis = [p["BMI"] for p in raw_data if p["BMI"] > 0]
            median_bmi = statistics.median(valid_bmis) if valid_bmis else 22.0

            patients = []
            for item in raw_data:
                bmi = item["BMI"]
                if bmi == 0 or bmi == 0.0:
                    bmi = median_bmi
                patient = Patient(
                    pid=item["id"],
                    name=item["name"],
                    glucose=item["Glucose"],
                    bmi=bmi,
                    age=item["Age"],
                    bp=item["BloodPressure"]
                )
                patients.append(patient)
            st.session_state["patients_data"] = patients

    def get_all_patients(self):
        return st.session_state["patients_data"]

    def get_patient_by_id(self, pid):
        for p in st.session_state["patients_data"]:
            if p.id == pid:
                return p
        return None


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
# ควบคุมการแสดงผลผ่าน Streamlit และจัดการ Workflow
# ==========================================
def main():
    st.set_page_config(page_title="Diabetes Risk Scoring System", page_icon="🏥", layout="centered")
    
    st.title("🏥 Diabetes Risk Scoring System")
    st.markdown("ระบบประเมินความเสี่ยงโรคเบาหวาน (พัฒนาด้วย Streamlit บนโครงสร้าง 4-Tier Architecture)")
    st.markdown("---")

    # เริ่มต้นเชื่อมโยง Model และ Service
    repository = PatientRepository()
    service = RiskScoringService()

    patients = repository.get_all_patients()
    
    # ส่วนเลือกผู้ป่วย (Dropdown)
    patient_options = {f"ID: {p.id} - {p.name}": p.id for p in patients}
    selected_label = st.selectbox("📌 เลือกผู้ป่วยที่ต้องการประเมินความเสี่ยง:", list(patient_options.keys()))
    selected_id = patient_options[selected_label]
    
    patient = repository.get_patient_by_id(selected_id)

    if patient:
        st.subheader(f"📋 ข้อมูลทางคลินิกปัจจุบัน: {patient.name} (ID: {patient.id})")
        
        # ฟอร์มสำหรับปรับแต่งค่าตัวชี้วัดก่อนประเมิน (What-if Analysis)
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
            # อัปเดตค่าลงใน Object ผู้ป่วย
            patient.glucose = new_glucose
            patient.bmi = new_bmi
            patient.age = new_age
            patient.blood_pressure = new_bp

            # ประเมินคะแนนความเสี่ยงผ่าน Business Logic Layer
            evaluation = service.calculate_risk(patient)
            score = evaluation["total_score"]
            category = evaluation["category"]

            # กำหนดสีตามระดับความเสี่ยง
            if category == "Low Risk":
                color = "#2ecc71" # เขียว
            elif category == "Moderate Risk":
                color = "#f39c12" # ส้ม
            else:
                color = "#e74c3c" # แดง

            st.markdown("---")
            
            # แสดงผลรายงานในรูปแบบ Medical Diagnostic Report (ดีไซน์ใบเสร็จ/รายงานทางการแพทย์)
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