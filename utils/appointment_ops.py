"""
Appointment operations module.
Handles booking, viewing, and managing appointments.
"""

from utils.db_manager import HospitalDB


class AppointmentManager(HospitalDB):
    """
    Manages appointment scheduling and queries.
    Inherits from HospitalDB.
    """

    def book_appointment(self, patient_id, doctor_id, date, time, reason):
        """
        Book a new appointment.

        Args:
            patient_id (int): Existing patient ID.
            doctor_id (int): Existing doctor ID.
            date (str): Appointment date (YYYY-MM-DD).
            time (str): Appointment time (HH:MM).
            reason (str): Reason for visit.
        """
        try:
            # Validate patient exists
            patient = self.fetch_one(
                'SELECT id FROM patients WHERE id = ?', (patient_id,)
            )
            if not patient:
                print(f"  ✗ Patient ID {patient_id} not found.")
                return

            # Validate doctor exists
            doctor = self.fetch_one(
                'SELECT id FROM doctors WHERE id = ?', (doctor_id,)
            )
            if not doctor:
                print(f"  ✗ Doctor ID {doctor_id} not found.")
                return

            with self._conn() as conn:
                conn.execute(
                    'INSERT INTO appointments '
                    '(patient_id, doctor_id, date, time, reason, status) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (patient_id, doctor_id, date, time, reason, 'Scheduled')
                )
            print(f"  ✓ Appointment booked for {date} at {time}.")
        except Exception as e:
            print(f"  ✗ Error booking appointment: {e}")

    def view_appointments(self):
        """
        Display all appointments with patient and doctor names.
        """
        try:
            rows = self.fetch_all("""
                SELECT a.*, p.name as patient_name, d.name as doctor_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                ORDER BY a.date, a.time
            """)
            if not rows:
                print("  No appointments found.")
                return

            print(f'\n  {"ID":>4}  {"Date":<12} {"Time":<8} {"Patient":<18} '
                  f'{"Doctor":<18} {"Status":<12}')
            print('  ' + '-' * 80)
            for row in rows:
                print(f'  {row["id"]:>4}  {row["date"]:<12} {row["time"]:<8} '
                      f'{row["patient_name"]:<18} {row["doctor_name"]:<18} '
                      f'{row["status"]:<12}')
        except Exception as e:
            print(f"  ✗ Error viewing appointments: {e}")

    def view_by_patient(self, patient_id):
        """
        View appointments for a specific patient.

        Args:
            patient_id (int): Patient ID to filter by.
        """
        try:
            rows = self.fetch_all(
                'SELECT * FROM appointments WHERE patient_id = ? ORDER BY date',
                (patient_id,)
            )
            if not rows:
                print(f"  No appointments for patient ID {patient_id}.")
                return

            for row in rows:
                print(f"  {row['date']} {row['time']}: {row['reason']} "
                      f"({row['status']})")
        except Exception as e:
            print(f"  ✗ Error fetching appointments: {e}")

    def cancel_appointment(self, appointment_id):
        """
        Cancel an appointment by ID.

        Args:
            appointment_id (int): Appointment to cancel.
        """
        try:
            with self._conn() as conn:
                conn.execute(
                    "UPDATE appointments SET status = 'Cancelled' WHERE id = ?",
                    (appointment_id,)
                )
            print(f"  ✓ Appointment {appointment_id} cancelled.")
        except Exception as e:
            print(f"  ✗ Error cancelling appointment: {e}")