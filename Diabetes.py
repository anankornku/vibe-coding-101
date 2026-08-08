import sys
import time
import statistics
import unittest
from unittest.mock import patch

# ==========================================
# CONFIGURATION SWITCH
# ==========================================
# Set to True to run the 3-Tier Testing Suite, or False to launch the application.
RUN_TEST_SUITE = False


# ==========================================
# 1. DATA ACCESS LAYER (MODEL)
# Manages raw data loading, structures, and initial data cleanup.
# ==========================================
class Patient:
    def __init__(self, pid, name, glucose, bmi, age, bp):
        self.id = pid
        self.name = name
        self.glucose = glucose
        self.bmi = bmi
        self.age = age
        self.blood_pressure = bp

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Glucose": self.glucose,
            "BMI": self.bmi,
            "Age": self.age,
            "BloodPressure": self.blood_pressure
        }


class PatientRepository:
    def __init__(self):
        self.patients = []
        self._load_and_clean_mock_data()

    def _load_and_clean_mock_data(self):
        """Loads 4 sample patients and cleans invalid data (e.g., BMI == 0)."""
        raw_data = [
            {"id": 1, "name": "John Doe", "Glucose": 95, "BMI": 22.5, "Age": 30, "BloodPressure": 118},
            {"id": 2, "name": "Jane Smith", "Glucose": 115, "BMI": 0.0, "Age": 52, "BloodPressure": 135}, # BMI = 0 (Requires cleaning)
            {"id": 3, "name": "Robert Lee", "Glucose": 140, "BMI": 33.2, "Age": 62, "BloodPressure": 145},
            {"id": 4, "name": "Maria Garcia", "Glucose": 88, "BMI": 24.0, "Age": 41, "BloodPressure": 112}
        ]

        # Calculate median of valid BMIs to replace 0-value entries
        valid_bmis = [p["BMI"] for p in raw_data if p["BMI"] > 0]
        median_bmi = statistics.median(valid_bmis) if valid_bmis else 22.0

        for item in raw_data:
            bmi = item["BMI"]
            if bmi == 0 or bmi == 0.0:
                bmi = median_bmi  # Automated data cleanup rule
            
            patient = Patient(
                pid=item["id"],
                name=item["name"],
                glucose=item["Glucose"],
                bmi=bmi,
                age=item["Age"],
                bp=item["BloodPressure"]
            )
            self.patients.append(patient)

    def get_all_patients(self):
        return self.patients

    def get_patient_by_id(self, pid):
        for p in self.patients:
            if p.id == pid:
                return p
        return None


# ==========================================
# 2. BUSINESS LOGIC LAYER (SERVICE)
# Handles pure clinical decision rules and scoring logic.
# ==========================================
class RiskScoringService:
    @staticmethod
    def evaluate_metric(metric_name, value):
        """Evaluates a metric against clinical thresholds and returns a sub-score (0, 1, or 2)."""
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
        """Computes total risk score and classifies the risk category."""
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
# 3. PRESENTATION LAYER (VIEW)
# Handles user interface layout, menus, and input captures.
# ==========================================
class ConsoleView:
    @staticmethod
    def display_main_menu():
        print("\n========================================")
        print("   DIABETES RISK SCORING SYSTEM")
        print("========================================")
        print("1. Assess Patient Risk")
        print("2. Exit")
        print("========================================")

    @staticmethod
    def display_patient_list(patients):
        print("\n--- Valid Patient IDs ---")
        for p in patients:
            print(f"ID: {p.id} | Name: {p.name}")

    @staticmethod
    def get_user_input(prompt):
        return input(prompt)

    @staticmethod
    def display_patient_profile(patient):
        print(f"\n--- Current Clinical Profile: {patient.name} (ID: {patient.id}) ---")
        print(f"  - Glucose: {patient.glucose} mg/dL")
        print(f"  - BMI: {patient.bmi:.1f}")
        print(f"  - Age: {patient.age} years")
        print(f"  - Blood Pressure: {patient.blood_pressure} mmHg")

    @staticmethod
    def display_diagnostic_report(patient_id: int, score: int, category: str) -> None:
        print("\n" + "="*52)
        print("                 MEDICAL DIAGNOSTIC REPORT")
        print("="*52)
        print("-" * 52)
        print(f" Patient ID:       {patient_id}")
        print(f" Cumulative Score: {score} pts")
        print(f" Risk Category:    {category.upper()}")
        print("-" * 52)
        print("              [!] CONFIDENTIAL INFORMATION [!]              ")
        print("="*52)

    @staticmethod
    def display_message(msg):
        print(msg)


# ==========================================
# 4. ORCHESTRATION LAYER (CONTROLLER)
# Manages workflow execution and coordinates all layers.
# ==========================================
class RiskController:
    def __init__(self):
        self.repository = PatientRepository()
        self.service = RiskScoringService()
        self.view = ConsoleView()

    def run(self):
        while True:
            self.view.display_main_menu()
            choice = self.view.get_user_input("Select an option (1-2): ").strip()

            if choice == "1":
                self._handle_assessment()
            elif choice == "2":
                self.view.display_message("\nExiting program. Stay healthy!")
                break
            else:
                self.view.display_message("\n[Error] Invalid choice. Please enter 1 or 2.")

    def _handle_assessment(self):
        patients = self.repository.get_all_patients()
        self.view.display_patient_list(patients)

        id_input = self.view.get_user_input("\nEnter Patient ID to assess: ").strip()
        if not id_input.isdigit():
            self.view.display_message("\n[Error] Invalid input. ID must be a number.")
            return

        pid = int(id_input)
        patient = self.repository.get_patient_by_id(pid)
        if not patient:
            self.view.display_message(f"\n[Error] Patient with ID {pid} does not exist.")
            return

        self.view.display_patient_profile(patient)

        modify = self.view.get_user_input("\nDo you want to modify any metrics before scoring? (y/n): ").strip().lower()
        if modify == 'y':
            self._modify_patient_metrics(patient)

        evaluation = self.service.calculate_risk(patient)
        self.view.display_diagnostic_report(patient, evaluation)

    def _modify_patient_metrics(self, patient):
        self.view.display_message("\nEnter new values or press Enter to keep current value:")
        
        # Glucose
        g_in = self.view.get_user_input(f"  Glucose [{patient.glucose}]: ").strip()
        if g_in.isdigit():
            patient.glucose = int(g_in)

        # BMI
        bmi_in = self.view.get_user_input(f"  BMI [{patient.bmi:.1f}]: ").strip()
        if bmi_in:
            try:
                patient.bmi = float(bmi_in)
            except ValueError:
                self.view.display_message("  [Warning] Invalid BMI format, keeping previous value.")

        # Age
        age_in = self.view.get_user_input(f"  Age [{patient.age}]: ").strip()
        if age_in.isdigit():
            patient.age = int(age_in)

        # Blood Pressure
        bp_in = self.view.get_user_input(f"  Blood Pressure [{patient.blood_pressure}]: ").strip()
        if bp_in.isdigit():
            patient.blood_pressure = int(bp_in)


# ==========================================
# 3-TIER TESTING SUITE
# ==========================================
class TestDiabetesSystem(unittest.TestCase):
    
    # --- Unit Tests ---
    def test_bmi_zero_correction(self):
        """Verify that a patient with BMI=0 is automatically cleaned using the median of valid peers."""
        repo = PatientRepository()
        jane = repo.get_patient_by_id(2)  # Jane Smith had BMI = 0 in mock data
        self.assertGreater(jane.bmi, 0.0)

    def test_scoring_service_low_risk(self):
        """Verify business logic bounds for Low Risk classification."""
        p = Patient(99, "Test Low", 90, 22.0, 30, 110)
        res = RiskScoringService.calculate_risk(p)
        self.assertEqual(res["total_score"], 0)
        self.assertEqual(res["category"], "Low Risk")

    def test_scoring_service_high_risk(self):
        """Verify business logic bounds for High Risk classification."""
        p = Patient(99, "Test High", 150, 35.0, 65, 150)
        res = RiskScoringService.calculate_risk(p)
        self.assertEqual(res["total_score"], 8)
        self.assertEqual(res["category"], "High Risk")

    # --- End-to-End (E2E) Tests ---
    def test_e2e_workflow(self):
        """Simulate a complete user journey loop across all 4 architectural layers."""
        # Flow: Select '1' (Assess), choose ID '1', skip modification ('n'), exit ('2')
        simulated_inputs = ['1', '1', 'n', '2']
        with patch('builtins.input', side_effect=simulated_inputs):
            controller = RiskController()
            controller.run()

    # --- Performance Tests ---
    def test_performance_benchmark(self):
        """Benchmark processing speed over thousands of iterations."""
        p = Patient(99, "Benchmark", 110, 27.5, 50, 130)
        iterations = 10000
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            RiskScoringService.calculate_risk(p)
            
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        print(f"\n[PERFORMANCE BENCHMARK] Evaluated risk scoring {iterations} times in {elapsed:.4f} seconds.")
        self.assertLess(elapsed, 1.0, "Performance test failed: Processing took too long.")


# ==========================================
# APPLICATION ENTRYPOINT
# ==========================================
if __name__ == "__main__":
    if RUN_TEST_SUITE:
        print(">>> Running 3-Tier Testing Suite...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        app = RiskController()
        app.run()