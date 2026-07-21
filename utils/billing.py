"""
Billing operations module.
Handles invoice generation, payment tracking, and totals.
"""

from datetime import datetime
from utils.db_manager import HospitalDB


class BillingManager(HospitalDB):
    """
    Manages patient billing, invoices, and payment status.
    Inherits from HospitalDB.
    """

    def generate_bill(self, patient_id, amount, description):
        """
        Generate a new bill for a patient.

        Args:
            patient_id (int): Patient to bill.
            amount (float): Bill amount.
            description (str): Service description.
        """
        try:
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with self._conn() as conn:
                conn.execute(
                    'INSERT INTO bills (patient_id, amount, description, '
                    'status, created_at) VALUES (?, ?, ?, ?, ?)',
                    (patient_id, amount, description, 'Unpaid', created_at)
                )
            print(f"  ✓ Bill of ${amount:.2f} generated for patient {patient_id}.")
        except Exception as e:
            print(f"  ✗ Error generating bill: {e}")

    def view_bills(self, patient_id=None):
        """
        View bills. Optionally filter by patient.

        Args:
            patient_id (int, optional): Filter by specific patient.
        """
        try:
            if patient_id:
                rows = self.fetch_all(
                    'SELECT * FROM bills WHERE patient_id = ? ORDER BY created_at',
                    (patient_id,)
                )
            else:
                rows = self.fetch_all(
                    'SELECT b.*, p.name as patient_name FROM bills b '
                    'JOIN patients p ON b.patient_id = p.id '
                    'ORDER BY b.created_at'
                )

            if not rows:
                print("  No bills found.")
                return

            print(f'\n  {"ID":>4}  {"Patient":<18} {"Amount":>10} '
                  f'{"Status":<10} {"Date"}')
            print('  ' + '-' * 60)
            total = 0
            for row in rows:
                print(f'  {row["id"]:>4}  {row.get("patient_name", "N/A"):<18} '
                      f'${row["amount"]:>8.2f} {row["status"]:<10} '
                      f'{row["created_at"]}')
                if row['status'] == 'Unpaid':
                    total += row['amount']
            print(f'\n  Total Unpaid: ${total:.2f}')
        except Exception as e:
            print(f"  ✗ Error viewing bills: {e}")

    def mark_paid(self, bill_id):
        """
        Mark a bill as paid.

        Args:
            bill_id (int): Bill ID to update.
        """
        try:
            with self._conn() as conn:
                conn.execute(
                    "UPDATE bills SET status = 'Paid' WHERE id = ?",
                    (bill_id,)
                )
            print(f"  ✓ Bill {bill_id} marked as paid.")
        except Exception as e:
            print(f"  ✗ Error updating bill: {e}")

    def print_invoice(self, bill_id):
        """
        Print a formatted invoice.

        Args:
            bill_id (int): Bill to print.
        """
        try:
            row = self.fetch_one(
                'SELECT b.*, p.name, p.phone FROM bills b '
                'JOIN patients p ON b.patient_id = p.id WHERE b.id = ?',
                (bill_id,)
            )
            if not row:
                print(f"  Bill ID {bill_id} not found.")
                return

            print("\n" + "=" * 50)
            print("           HOSPITAL INVOICE")
            print("=" * 50)
            print(f"  Bill ID:     {row['id']}")
            print(f"  Patient:     {row['name']}")
            print(f"  Phone:       {row['phone']}")
            print(f"  Date:        {row['created_at']}")
            print(f"  Description: {row['description']}")
            print(f"  Amount:      ${row['amount']:.2f}")
            print(f"  Status:      {row['status']}")
            print("=" * 50)
        except Exception as e:
            print(f"  ✗ Error printing invoice: {e}")