"""
Doctor operations module.
Manages doctor records, specializations, and department assignments.
"""

from utils.db_manager import HospitalDB


class DoctorManager(HospitalDB):
    """
    Handles doctor CRUD operations and department-based queries.
    Inherits from HospitalDB.
    """

    def add_doctor(self, name, specialisation, department):
        """
        Add a new doctor to the system.

        Args:
            name (str): Doctor's full name.
            specialisation (str): Medical specialization.
            department (str): Hospital department.
        """
        try:
            with self._conn() as conn:
                conn.execute(
                    'INSERT INTO doctors (name, specialisation, department) '
                    'VALUES (?, ?, ?)',
                    (name, specialisation, department)
                )
            print(f"  ✓ Dr. {name} added to {department}.")
        except Exception as e:
            print(f"  ✗ Error adding doctor: {e}")

    def view_doctors(self):
        """
        Display all doctors.
        """
        try:
            rows = self.fetch_all('SELECT * FROM doctors ORDER BY name')
            if not rows:
                print("  No doctors found.")
                return

            print(f'\n  {"ID":>4}  {"Name":<22} {"Specialisation":<20} {"Department"}')
            print('  ' + '-' * 65)
            for row in rows:
                print(f'  {row["id"]:>4}  {row["name"]:<22} '
                      f'{row["specialisation"]:<20} {row["department"]}')
        except Exception as e:
            print(f"  ✗ Error viewing doctors: {e}")

    def search_doctor(self, search_term):
        """
        Search doctors by name or department.

        Args:
            search_term (str): Name or department to search.
        """
        try:
            rows = self.fetch_all(
                'SELECT * FROM doctors WHERE name LIKE ? OR department LIKE ?',
                (f'%{search_term}%', f'%{search_term}%')
            )
            if not rows:
                print(f"  No doctors found for '{search_term}'.")
                return

            for row in rows:
                print(f"  ID {row['id']}: Dr. {row['name']} — "
                      f"{row['specialisation']} ({row['department']})")
        except Exception as e:
            print(f"  ✗ Error searching doctors: {e}")