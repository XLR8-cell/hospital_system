"""
Ward operations module.
Handles ward occupancy, patient admission, discharge, and bed availability.
"""

from utils.db_manager import HospitalDB


class WardManager(HospitalDB):
    """
    Manages ward occupancy, patient admission, and discharge.
    Inherits from HospitalDB.
    """

    def add_ward(self, name, capacity):
        """
        Add a new ward to the system.

        Args:
            name (str): Ward name.
            capacity (int): Total bed capacity.
        """
        try:
            with self._conn() as conn:
                conn.execute(
                    'INSERT INTO wards (name, capacity, occupied) '
                    'VALUES (?, ?, ?)',
                    (name, capacity, 0)
                )
            print(f"  ✓ Ward '{name}' added with capacity {capacity}.")
        except Exception as e:
            print(f"  ✗ Error adding ward: {e}")

    def view_wards(self):
        """
        Display all wards with occupancy status.
        """
        try:
            rows = self.fetch_all('SELECT * FROM wards ORDER BY name')
            if not rows:
                print("  No wards found.")
                return

            print(f'\n  {"ID":>4}  {"Name":<18} {"Capacity":>10} {"Occupied":>10} '
                  f'{"Available":>10}')
            print('  ' + '-' * 58)
            for row in rows:
                available = row['capacity'] - row['occupied']
                print(f'  {row["id"]:>4}  {row["name"]:<18} '
                      f'{row["capacity"]:>10} {row["occupied"]:>10} '
                      f'{available:>10}')
            print(f'\n  Total: {len(rows)} ward(s)')
        except Exception as e:
            print(f"  ✗ Error viewing wards: {e}")

    def admit_patient(self, ward_name):
        """
        Admit a patient to a ward (increment occupied).

        Args:
            ward_name (str): Name of the ward.
        """
        try:
            ward = self.fetch_one(
                'SELECT * FROM wards WHERE name = ?', (ward_name,)
            )
            if not ward:
                print(f"  ✗ Ward '{ward_name}' not found.")
                return

            if ward['occupied'] >= ward['capacity']:
                print(f"  ✗ Ward '{ward_name}' is FULL.")
                return

            with self._conn() as conn:
                conn.execute(
                    'UPDATE wards SET occupied = occupied + 1 WHERE name = ?',
                    (ward_name,)
                )

            available = ward['capacity'] - ward['occupied'] - 1
            print(f"  ✓ Patient admitted to '{ward_name}'. Beds available: {available}")
        except Exception as e:
            print(f"  ✗ Error admitting patient: {e}")

    def discharge_patient(self, ward_name):
        """
        Discharge a patient from a ward (decrement occupied).

        Args:
            ward_name (str): Name of the ward.
        """
        try:
            ward = self.fetch_one(
                'SELECT * FROM wards WHERE name = ?', (ward_name,)
            )
            if not ward:
                print(f"  ✗ Ward '{ward_name}' not found.")
                return

            if ward['occupied'] <= 0:
                print(f"  ✗ Ward '{ward_name}' has no patients to discharge.")
                return

            with self._conn() as conn:
                conn.execute(
                    'UPDATE wards SET occupied = occupied - 1 WHERE name = ?',
                    (ward_name,)
                )

            available = ward['capacity'] - ward['occupied'] + 1
            print(f"  ✓ Patient discharged from '{ward_name}'. Beds available: {available}")
        except Exception as e:
            print(f"  ✗ Error discharging patient: {e}")

    def view_available_beds(self):
        """
        Show only wards with available beds.
        """
        try:
            rows = self.fetch_all(
                'SELECT * FROM wards WHERE occupied < capacity ORDER BY name'
            )
            if not rows:
                print("  No wards with available beds.")
                return

            print(f'\n  {"Name":<18} {"Capacity":>10} {"Occupied":>10} {"Available":>10}')
            print('  ' + '-' * 52)
            for row in rows:
                available = row['capacity'] - row['occupied']
                print(f'  {row["name"]:<18} {row["capacity"]:>10} '
                      f'{row["occupied"]:>10} {available:>10}')
        except Exception as e:
            print(f"  ✗ Error viewing available beds: {e}")