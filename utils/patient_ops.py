"""
Patient operations module.
Handles all CRUD operations for patient records.
Ward occupancy is kept in sync with the wards table.
"""

from utils.db_manager import HospitalDB


class PatientManager(HospitalDB):
    """
    Manages patient registration, viewing, searching, updating, and deletion.
    Inherits from HospitalDB for database connectivity.
    Ward occupancy is automatically tracked.
    """

    def add_patient(self, name, dob, phone, blood_type, ward):
        """
        Register a new patient and increment ward occupancy.

        Args:
            name (str): Patient full name.
            dob (str): Date of birth (YYYY-MM-DD).
            phone (str): Contact phone number.
            blood_type (str): Blood group (e.g., 'O+').
            ward (str): Assigned ward name.

        Returns:
            int: ID of newly created patient, or None if failed.
        """
        try:
            # Validate ward exists and has space
            ward_row = self.fetch_one(
                'SELECT * FROM wards WHERE name = ?', (ward,)
            )
            if not ward_row:
                print(f"  ✗ Ward '{ward}' not found.")
                return None
            if ward_row['occupied'] >= ward_row['capacity']:
                print(f"  ✗ Ward '{ward}' is full.")
                return None

            with self._conn() as conn:
                cursor = conn.execute(
                    'INSERT INTO patients (name, dob, phone, blood_type, ward) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (name, dob, phone, blood_type, ward)
                )
                patient_id = cursor.lastrowid

                # Increment ward occupancy
                conn.execute(
                    'UPDATE wards SET occupied = occupied + 1 WHERE name = ?',
                    (ward,)
                )

            print(f"  ✓ Patient '{name}' registered with ID {patient_id}.")
            return patient_id
        except Exception as e:
            print(f"  ✗ Error registering patient: {e}")
            return None

    def view_patients(self):
        """
        Display all patient records sorted by name.
        """
        try:
            rows = self.fetch_all(
                'SELECT * FROM patients ORDER BY name'
            )
            if not rows:
                print("  No patients found.")
                return

            print(f'\n  {"ID":>4}  {"Name":<22} {"DOB":<12} {"Blood":>6} {"Ward":<12} {"Phone"}')
            print('  ' + '-' * 72)
            for row in rows:
                print(f'  {row["id"]:>4}  {row["name"]:<22} '
                      f'{row["dob"]:<12} {row["blood_type"]:>6} '
                      f'{row["ward"]:<12} {row["phone"]}')
            print(f'\n  Total: {len(rows)} patient(s)')
        except Exception as e:
            print(f"  ✗ Error viewing patients: {e}")

    def search_patient(self, search_term):
        """
        Search patients by name or ID.

        Args:
            search_term (str): Name fragment or patient ID.
        """
        try:
            query = 'SELECT * FROM patients WHERE name LIKE ? OR id = ?'
            rows = self.fetch_all(query, (f'%{search_term}%', search_term))

            if not rows:
                print(f"  No patients found for '{search_term}'.")
                return

            print(f'\n  {"ID":>4}  {"Name":<22} {"Blood":>6} {"Ward":<12}')
            print('  ' + '-' * 50)
            for row in rows:
                print(f'  {row["id"]:>4}  {row["name"]:<22} '
                      f'{row["blood_type"]:>6} {row["ward"]:<12}')
        except Exception as e:
            print(f"  ✗ Error searching patients: {e}")

    def update_patient(self, patient_id, **kwargs):
        """
        Update patient fields. Handles ward changes.

        Args:
            patient_id (int): Patient ID to update.
            **kwargs: Fields to update (name, dob, phone, blood_type, ward).
        """
        try:
            allowed_fields = {'name', 'dob', 'phone', 'blood_type', 'ward'}
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

            if not updates:
                print("  No valid fields to update.")
                return

            # Handle ward change separately
            new_ward = updates.get('ward')
            if new_ward:
                # Get current ward
                current = self.fetch_one(
                    'SELECT ward FROM patients WHERE id = ?', (patient_id,)
                )
                if not current:
                    print(f"  ✗ Patient ID {patient_id} not found.")
                    return

                old_ward = current['ward']

                if old_ward != new_ward:
                    # Validate new ward
                    ward_row = self.fetch_one(
                        'SELECT * FROM wards WHERE name = ?', (new_ward,)
                    )
                    if not ward_row:
                        print(f"  ✗ Ward '{new_ward}' not found.")
                        return
                    if ward_row['occupied'] >= ward_row['capacity']:
                        print(f"  ✗ Ward '{new_ward}' is full.")
                        return

                    # Update both wards in single transaction
                    with self._conn() as conn:
                        set_clause = ', '.join(f'{k} = ?' for k in updates)
                        values = list(updates.values()) + [patient_id]
                        conn.execute(
                            f'UPDATE patients SET {set_clause} WHERE id = ?',
                            values
                        )
                        conn.execute(
                            'UPDATE wards SET occupied = occupied - 1 WHERE name = ?',
                            (old_ward,)
                        )
                        conn.execute(
                            'UPDATE wards SET occupied = occupied + 1 WHERE name = ?',
                            (new_ward,)
                        )

                    print(f"  ✓ Patient ID {patient_id} updated. "
                          f"Moved from '{old_ward}' to '{new_ward}'.")
                    return

            # No ward change — simple update
            set_clause = ', '.join(f'{k} = ?' for k in updates)
            values = list(updates.values()) + [patient_id]

            with self._conn() as conn:
                conn.execute(
                    f'UPDATE patients SET {set_clause} WHERE id = ?',
                    values
                )
            print(f"  ✓ Patient ID {patient_id} updated successfully.")
        except Exception as e:
            print(f"  ✗ Error updating patient: {e}")

    def delete_patient(self, patient_id):
        """
        Delete a patient record and decrement ward occupancy.

        Args:
            patient_id (int): Patient ID to delete.
        """
        try:
            with self._conn() as conn:
                # Get ward before deleting
                patient = conn.execute(
                    'SELECT ward FROM patients WHERE id = ?', (patient_id,)
                ).fetchone()

                if not patient:
                    print(f"  ✗ Patient ID {patient_id} not found.")
                    return

                ward = patient['ward']

                conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))

                # Decrement ward occupancy
                conn.execute(
                    'UPDATE wards SET occupied = occupied - 1 WHERE name = ?',
                    (ward,)
                )

            print(f"  ✓ Patient ID {patient_id} deleted from ward '{ward}'.")
        except Exception as e:
            print(f"  ✗ Error deleting patient: {e}")