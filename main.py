"""
Hospital Management System - Main Entry Point.

A console-based HMS with OOP design and SQLite persistence.
"""

import sys
from utils.patient_ops import PatientManager
from utils.doctor_ops import DoctorManager
from utils.appointment_ops import AppointmentManager
from utils.billing import BillingManager
from utils.ward_ops import WardManager


def get_input(prompt, required=True):
    """
    Get user input with validation.

    Args:
        prompt (str): Display prompt.
        required (bool): Whether empty input is allowed.

    Returns:
        str: User input.
    """
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("  This field is required.")


def patient_menu(pm):
    """Patient management submenu."""
    while True:
        print("\n  --- PATIENT MANAGEMENT ---")
        print("  1. Register Patient")
        print("  2. View All Patients")
        print("  3. Search Patient")
        print("  4. Update Patient")
        print("  5. Delete Patient")
        print("  6. Back to Main Menu")
        choice = input("  Select: ").strip()

        if choice == '1':
            pm.add_patient(
                get_input("  Name: "),
                get_input("  DOB (YYYY-MM-DD): "),
                get_input("  Phone: "),
                get_input("  Blood Type: "),
                get_input("  Ward: ")
            )
        elif choice == '2':
            pm.view_patients()
        elif choice == '3':
            pm.search_patient(get_input("  Search (name or ID): "))
        elif choice == '4':
            pid = get_input("  Patient ID: ")
            print("  Enter new values (press Enter to skip):")
            updates = {}
            for field in ['name', 'dob', 'phone', 'blood_type', 'ward']:
                val = input(f"  {field.title()}: ").strip()
                if val:
                    updates[field] = val
            pm.update_patient(int(pid), **updates)
        elif choice == '5':
            pm.delete_patient(int(get_input("  Patient ID to delete: ")))
        elif choice == '6':
            break


def doctor_menu(dm):
    """Doctor management submenu."""
    while True:
        print("\n  --- DOCTOR MANAGEMENT ---")
        print("  1. Add Doctor")
        print("  2. View All Doctors")
        print("  3. Search Doctor")
        print("  4. Back to Main Menu")
        choice = input("  Select: ").strip()

        if choice == '1':
            dm.add_doctor(
                get_input("  Name: "),
                get_input("  Specialisation: "),
                get_input("  Department: ")
            )
        elif choice == '2':
            dm.view_doctors()
        elif choice == '3':
            dm.search_doctor(get_input("  Search (name or dept): "))
        elif choice == '4':
            break


def appointment_menu(am):
    """Appointment management submenu."""
    while True:
        print("\n  --- APPOINTMENT SYSTEM ---")
        print("  1. Book Appointment")
        print("  2. View All Appointments")
        print("  3. View by Patient")
        print("  4. Cancel Appointment")
        print("  5. Back to Main Menu")
        choice = input("  Select: ").strip()

        if choice == '1':
            am.book_appointment(
                int(get_input("  Patient ID: ")),
                int(get_input("  Doctor ID: ")),
                get_input("  Date (YYYY-MM-DD): "),
                get_input("  Time (HH:MM): "),
                get_input("  Reason: ")
            )
        elif choice == '2':
            am.view_appointments()
        elif choice == '3':
            am.view_by_patient(int(get_input("  Patient ID: ")))
        elif choice == '4':
            am.cancel_appointment(int(get_input("  Appointment ID: ")))
        elif choice == '5':
            break


def billing_menu(bm):
    """Billing management submenu."""
    while True:
        print("\n  --- BILLING SYSTEM ---")
        print("  1. Generate Bill")
        print("  2. View Bills")
        print("  3. Mark as Paid")
        print("  4. Print Invoice")
        print("  5. Back to Main Menu")
        choice = input("  Select: ").strip()

        if choice == '1':
            bm.generate_bill(
                int(get_input("  Patient ID: ")),
                float(get_input("  Amount: $")),
                get_input("  Description: ")
            )
        elif choice == '2':
            pid = input("  Patient ID (or Enter for all): ").strip()
            bm.view_bills(int(pid) if pid else None)
        elif choice == '3':
            bm.mark_paid(int(get_input("  Bill ID: ")))
        elif choice == '4':
            bm.print_invoice(int(get_input("  Bill ID: ")))
        elif choice == '5':
            break


def ward_menu(wm):
    """Ward management submenu."""
    while True:
        print("\n  --- WARD MANAGEMENT ---")
        print("  1. Add Ward")
        print("  2. View All Wards")
        print("  3. Admit Patient")
        print("  4. Discharge Patient")
        print("  5. View Available Beds")
        print("  6. Back to Main Menu")
        choice = input("  Select: ").strip()

        if choice == '1':
            wm.add_ward(
                get_input("  Ward name: "),
                int(get_input("  Capacity: "))
            )
        elif choice == '2':
            wm.view_wards()
        elif choice == '3':
            wm.admit_patient(get_input("  Ward name: "))
        elif choice == '4':
            wm.discharge_patient(get_input("  Ward name: "))
        elif choice == '5':
            wm.view_available_beds()
        elif choice == '6':
            break


def main():
    """
    Main application entry point.
    Initializes managers and runs the main menu loop.
    """
    pm = PatientManager()
    dm = DoctorManager()
    am = AppointmentManager()
    bm = BillingManager()
    wm = WardManager()

    print("\n" + "=" * 50)
    print("   HOSPITAL MANAGEMENT SYSTEM")
    print("=" * 50)

    while True:
        try:
            print("\n--- MAIN MENU ---")
            print("1. Patient Management")
            print("2. Doctor Management")
            print("3. Appointment System")
            print("4. Billing System")
            print("5. Ward Management")
            print("6. Exit")
            choice = input("Select: ").strip()

            if choice == '1':
                patient_menu(pm)
            elif choice == '2':
                doctor_menu(dm)
            elif choice == '3':
                appointment_menu(am)
            elif choice == '4':
                billing_menu(bm)
            elif choice == '5':
                ward_menu(wm)
            elif choice == '6':
                print("\nThank you for using HMS. Goodbye!")
                sys.exit(0)
            else:
                print("  Invalid choice. Please try again.")

        except ValueError as ve:
            print(f"  Invalid input: {ve}")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"  Unexpected error: {e}")


if __name__ == '__main__':
    main()