import mysql.connector
from mysql.connector import errorcode
from colorama import init, Fore, Style
from tabulate import tabulate
from datetime import datetime

init(autoreset=True)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Adithya3921*',
    'database': 'project'
}

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print(Fore.RED + "Access denied: Invalid username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(Fore.RED + "Database does not exist.")
        else:
            print(Fore.RED + f"Error: {err}")
        exit(1)

def input_date(prompt):
    while True:
        date_str = input(prompt + " (YYYY-MM-DD HH:MM:SS): ")
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(Fore.YELLOW + "Invalid datetime format. Please try again.")

def print_table(data, headers):
    if data:
        print(tabulate(data, headers=headers, tablefmt='psql'))
    else:
        print(Fore.YELLOW + "No records found.")

def yes_no_prompt(prompt):
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ('y', 'n'):
            return ans == 'y'
        print(Fore.YELLOW + "Please enter 'y' or 'n'.")

def branch_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Branch Management ---")
        print("1. Add Branch\n2. View Branches\n3. Update Branch\n4. Delete Branch\n5. Back to Main Menu")
        choice = input("Choice: ")
        if choice == '1':
            try:
                branchid = int(input("Branch ID: "))
                name = input("Branch Name: ")
                addr = input("Address: ")
                phone = input("Phone No: ")
                cur.execute("INSERT INTO branches (BranchID, BranchName, address, PhoneNo) VALUES (%s,%s,%s,%s)", (branchid, name, addr, phone))
                conn.commit()
                print(Fore.GREEN + "Branch added.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT BranchID, BranchName, address, PhoneNo FROM branches ORDER BY BranchID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            try:
                branchid = int(input("Branch ID to update: "))
                cur.execute("SELECT * FROM branches WHERE BranchID=%s", (branchid,))
                if not cur.fetchone():
                    print(Fore.YELLOW + "Not found.")
                    continue
                name = input("New Name (blank to keep): ").strip()
                addr = input("New Address (blank to keep): ").strip()
                phone = input("New Phone No (blank to keep): ").strip()
                updates, params = [], []
                if name:
                    updates.append("BranchName=%s"); params.append(name)
                if addr:
                    updates.append("address=%s"); params.append(addr)
                if phone:
                    updates.append("PhoneNo=%s"); params.append(phone)
                if not updates:
                    print(Fore.YELLOW + "No changes.")
                    continue
                params.append(branchid)
                cur.execute(f"UPDATE branches SET {', '.join(updates)} WHERE BranchID=%s", params)
                conn.commit()
                print(Fore.GREEN + "Updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            try:
                branchid = int(input("Branch ID to delete: "))
                cur.execute("DELETE FROM branches WHERE BranchID=%s", (branchid,))
                conn.commit()
                print(Fore.GREEN + "Deleted.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '5':
            break
        else:
            print(Fore.YELLOW + "Invalid option.")

def customer_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Customer Management ---")
        print("1. Add Customer\n2. View Customers\n3. Update Customer\n4. Delete Customer\n5. Back")
        c = input("Choice: ")
        if c == '1':
            try:
                cid = int(input("Customer ID: "))
                fname = input("First Name: ")
                lname = input("Last Name: ")
                email = input("Email: ")
                phone = input("Phone No: ")
                addr = input("Address: ")
                lic = input("License Number: ")
                dob = input_date("DOB")
                cur.execute(
                    "INSERT INTO customers (CustomerID, First_Name, Last_Name, Email, PhoneNo, Address, LicenseNumber, DateofBirth) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (cid, fname, lname, email, phone, addr, lic, dob))
                conn.commit()
                print(Fore.GREEN + "Customer added.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif c == '2':
            cur.execute("SELECT * FROM customers ORDER BY CustomerID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif c == '3':
            try:
                cid = int(input("Customer ID to update: "))
                cur.execute("SELECT * FROM customers WHERE CustomerID=%s", (cid,))
                cdata = cur.fetchone()
                if not cdata:
                    print(Fore.YELLOW + "Not found.")
                    continue
                fname = input(f"First Name ({cdata['First_Name']}): ") or cdata['First_Name']
                lname = input(f"Last Name ({cdata['Last_Name']}): ") or cdata['Last_Name']
                email = input(f"Email ({cdata['Email']}): ") or cdata['Email']
                phone = input(f"Phone ({cdata['PhoneNo']}): ") or cdata['PhoneNo']
                addr = input(f"Address ({cdata['Address']}): ") or cdata['Address']
                lic = input(f"License Number ({cdata['LicenseNumber']}): ") or cdata['LicenseNumber']
                dob = input(f"DOB ({cdata['DateofBirth']}): ") or cdata['DateofBirth']
                cur.execute(
                    "UPDATE customers SET First_Name=%s, Last_Name=%s, Email=%s, PhoneNo=%s, Address=%s, LicenseNumber=%s, DateofBirth=%s WHERE CustomerID=%s",
                    (fname,lname,email,phone,addr,lic,dob,cid))
                conn.commit()
                print(Fore.GREEN + "Updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif c == '4':
            try:
                cid = int(input("Customer ID to delete: "))
                cur.execute("DELETE FROM customers WHERE CustomerID=%s", (cid,))
                conn.commit()
                print(Fore.GREEN + "Deleted.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif c == '5':
            break
        else:
            print(Fore.YELLOW + "Invalid option.")

def employee_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Employee Management ---")
        print("1. Add Employee\n2. View Employees\n3. Update Employee\n4. Delete Employee\n5. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                eid = int(input("Employee ID: "))
                fname = input("First Name: ")
                lname = input("Last Name: ")
                role = input("Role: ")
                branchid = int(input("Branch ID: "))
                email = input("Email: ")
                phone = input("Phone No: ")
                cur.execute(
                    "INSERT INTO employees (EmployeeID, FirstName, LastName, Role, BranchID, Email, PhoneNumber) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (eid, fname, lname, role, branchid, email, phone))
                conn.commit()
                print(Fore.GREEN + "Employee added.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT * FROM employees ORDER BY EmployeeID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            try:
                eid = int(input("Employee ID to update: "))
                cur.execute("SELECT * FROM employees WHERE EmployeeID=%s", (eid,))
                edata = cur.fetchone()
                if not edata:
                    print(Fore.YELLOW + "Not found.")
                    continue
                fname = input(f"First Name ({edata['FirstName']}): ") or edata['FirstName']
                lname = input(f"Last Name ({edata['LastName']}): ") or edata['LastName']
                role = input(f"Role ({edata['Role']}): ") or edata['Role']
                branchid = input(f"Branch ID ({edata['BranchID']}): ") or edata['BranchID']
                email = input(f"Email ({edata['Email']}): ") or edata['Email']
                phone = input(f"Phone ({edata['PhoneNumber']}): ") or edata['PhoneNumber']
                cur.execute(
                    "UPDATE employees SET FirstName=%s, LastName=%s, Role=%s, BranchID=%s, Email=%s, PhoneNumber=%s WHERE EmployeeID=%s",
                    (fname, lname, role, int(branchid), email, phone, eid))
                conn.commit()
                print(Fore.GREEN + "Updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            try:
                eid = int(input("Employee ID to delete: "))
                cur.execute("DELETE FROM employees WHERE EmployeeID=%s", (eid,))
                conn.commit()
                print(Fore.GREEN + "Deleted.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '5':
            break
        else:
            print(Fore.YELLOW + "Invalid option.")

def car_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Car Management ---")
        print("1. Add Car\n2. View Cars\n3. Update Car\n4. Delete Car\n5. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                cid = int(input("Car ID: "))
                model = input("Model: ")
                make = input("Make: ")
                year = int(input("Year: "))
                cartype = input("Car Type: ")
                reg = input("Registration Number: ")
                status = input("Availability Status: ")
                branchid = int(input("Branch ID: "))
                cur.execute(
                    "INSERT INTO cars (CarID, Model, Make, Year, CarType, RegistrationNumber, AvailabilityStatus, BranchID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (cid, model, make, year, cartype, reg, status, branchid))
                conn.commit()
                print(Fore.GREEN + "Car added.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT * FROM cars ORDER BY CarID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            try:
                cid = int(input("Car ID to update: "))
                cur.execute("SELECT * FROM cars WHERE CarID=%s", (cid,))
                cdata = cur.fetchone()
                if not cdata:
                    print(Fore.YELLOW + "Not found.")
                    continue
                model = input(f"Model ({cdata['Model']}): ") or cdata['Model']
                make = input(f"Make ({cdata['Make']}): ") or cdata['Make']
                year = input(f"Year ({cdata['Year']}): ") or str(cdata['Year'])
                cartype = input(f"CarType ({cdata['CarType']}): ") or cdata['CarType']
                reg = input(f"RegistrationNumber ({cdata['RegistrationNumber']}): ") or cdata['RegistrationNumber']
                status = input(f"AvailabilityStatus ({cdata['AvailabilityStatus']}): ") or cdata['AvailabilityStatus']
                branchid = input(f"BranchID ({cdata['BranchID']}): ") or str(cdata['BranchID'])
                cur.execute(
                    "UPDATE cars SET Model=%s, Make=%s, Year=%s, CarType=%s, RegistrationNumber=%s, AvailabilityStatus=%s, BranchID=%s WHERE CarID=%s",
                    (model, make, int(year), cartype, reg, status, int(branchid), cid))
                conn.commit()
                print(Fore.GREEN + "Updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            try:
                cid = int(input("Car ID to delete: "))
                cur.execute("DELETE FROM cars WHERE CarID=%s", (cid,))
                conn.commit()
                print(Fore.GREEN + "Deleted.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '5':
            break
        else:
            print(Fore.YELLOW + "Invalid option.")

def location_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Location Management ---")
        print("1. Add Location\n2. View Locations\n3. Update Location\n4. Delete Location\n5. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                locid = int(input("Location ID: "))
                branchid = int(input("Branch ID: "))
                addr = input("Address: ")
                pickup = yes_no_prompt("Is Pickup Point?")
                dropoff = yes_no_prompt("Is Dropoff Point?")
                cur.execute("INSERT INTO locations (LocationID, BranchID, Address, IsPickupPoint, IsDropoffPoint) VALUES (%s,%s,%s,%s,%s)",
                            (locid, branchid, addr, pickup, dropoff))
                conn.commit()
                print(Fore.GREEN + "Location added.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT * FROM locations ORDER BY LocationID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            try:
                locid = int(input("Location ID to update: "))
                cur.execute("SELECT * FROM locations WHERE LocationID=%s", (locid,))
                ldata = cur.fetchone()
                if not ldata:
                    print(Fore.YELLOW + "Not found.")
                    continue
                addr = input(f"Address ({ldata['Address']}): ") or ldata['Address']
                pickup = input(f"Is Pickup Point ({ldata['IsPickupPoint']}): ").lower()
                dropoff = input(f"Is Dropoff Point ({ldata['IsDropoffPoint']}): ").lower()
                pick_val = ldata['IsPickupPoint']
                drop_val = ldata['IsDropoffPoint']
                if pickup in ('y','n'):
                    pick_val = (pickup == 'y')
                if dropoff in ('y','n'):
                    drop_val = (dropoff == 'y')
                cur.execute("UPDATE locations SET Address=%s, IsPickupPoint=%s, IsDropoffPoint=%s WHERE LocationID=%s",
                            (addr, pick_val, drop_val, locid))
                conn.commit()
                print(Fore.GREEN + "Location updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            try:
                locid = int(input("Location ID to delete: "))
                cur.execute("DELETE FROM locations WHERE LocationID=%s", (locid,))
                conn.commit()
                print(Fore.GREEN + "Location deleted.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '5':
            break
        else:
            print(Fore.YELLOW + "Invalid choice.")

def reservation_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Reservation Management ---")
        print("1. Add Reservation\n2. View Reservations\n3. Update Reservation\n4. Cancel Reservation\n5. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                resid = int(input("Reservation ID: "))
                cid = int(input("Customer ID: "))
                carid = int(input("Car ID: "))
                rdate = input_date("Reservation Date")
                pickupid = int(input("Pickup Location ID: "))
                dropoffid = int(input("Dropoff Location ID: "))
                status = "Confirmed"
                cur.execute("SELECT AvailabilityStatus FROM cars WHERE CarID=%s", (carid,))
                avail = cur.fetchone()
                if not avail:
                    print(Fore.YELLOW + "Car not found.")
                    continue
                if avail['AvailabilityStatus'].lower() != 'available':
                    print(Fore.RED + f"Car not available. Status: {avail['AvailabilityStatus']}")
                    continue
                cur.execute("INSERT INTO reservations (ReservationID, CustomerID, CarID, ReservationDate, PickupLocationID, DropoffLocationID, Status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                            (resid, cid, carid, rdate, pickupid, dropoffid, status))
                cur.execute("UPDATE cars SET AvailabilityStatus='Reserved' WHERE CarID=%s", (carid,))
                conn.commit()
                print(Fore.GREEN + "Reservation added and car marked reserved.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT * FROM reservations ORDER BY ReservationID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            try:
                resid = int(input("Reservation ID to update: "))
                cur.execute("SELECT * FROM reservations WHERE ReservationID=%s", (resid,))
                rdata = cur.fetchone()
                if not rdata:
                    print(Fore.YELLOW + "Not found.")
                    continue
                cid = input(f"Customer ID ({rdata['CustomerID']}): ") or rdata['CustomerID']
                carid = input(f"Car ID ({rdata['CarID']}): ") or rdata['CarID']
                rdate = input(f"Reservation Date ({rdata['ReservationDate']}): ") or rdata['ReservationDate']
                pickupid = input(f"Pickup Location ID ({rdata['PickupLocationID']}): ") or rdata['PickupLocationID']
                dropoffid = input(f"Dropoff Location ID ({rdata['DropoffLocationID']}): ") or rdata['DropoffLocationID']
                status = input(f"Status ({rdata['Status']}): ") or rdata['Status']
                cur.execute("UPDATE reservations SET CustomerID=%s, CarID=%s, ReservationDate=%s, PickupLocationID=%s, DropoffLocationID=%s, Status=%s WHERE ReservationID=%s",
                            (int(cid), int(carid), rdate, int(pickupid), int(dropoffid), status, resid))
                conn.commit()
                print(Fore.GREEN + "Reservation updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            try:
                resid = int(input("Reservation ID to cancel: "))
                cur.execute("SELECT CarID FROM reservations WHERE ReservationID=%s", (resid,))
                car = cur.fetchone()
                if not car:
                    print(Fore.YELLOW + "Reservation not found.")
                    continue
                cur.execute("DELETE FROM reservations WHERE ReservationID=%s", (resid,))
                cur.execute("UPDATE cars SET AvailabilityStatus='Available' WHERE CarID=%s", (car['CarID'],))
                conn.commit()
                print(Fore.GREEN + "Reservation cancelled and car set to available.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '5':
            break
        else:
            print(Fore.YELLOW + "Invalid choice.")

def rental_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Rental Management ---")
        print("1. Start Rental\n2. End Rental\n3. View Rentals\n4. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                rid = int(input("Rental ID: "))
                resid = int(input("Reservation ID: "))
                startd = input_date("Rental Start Date")
                endd = input_date("Rental End Date")
                cur.execute("INSERT INTO rentals (RentalID, ReservationID, RentalStartDate, RentalEndDate) VALUES (%s,%s,%s,%s)", (rid, resid, startd, endd))
                cur.execute("SELECT CarID FROM reservations WHERE ReservationID=%s", (resid,))
                carid = cur.fetchone()['CarID']
                cur.execute("UPDATE cars SET AvailabilityStatus='Rented' WHERE CarID=%s", (carid,))
                conn.commit()
                print(Fore.GREEN + "Rental started.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            try:
                rid = int(input("Rental ID to end: "))
                actual = input_date("Actual Return Date")
                total = float(input("Total Cost: "))
                cur.execute("UPDATE rentals SET ActualReturnDate=%s, TotalCost=%s WHERE RentalID=%s", (actual, total, rid))
                cur.execute("SELECT ReservationID FROM rentals WHERE RentalID=%s", (rid,))
                resid = cur.fetchone()['ReservationID']
                cur.execute("SELECT CarID FROM reservations WHERE ReservationID=%s", (resid,))
                carid = cur.fetchone()['CarID']
                cur.execute("UPDATE cars SET AvailabilityStatus='Available' WHERE CarID=%s", (carid,))
                conn.commit()
                print(Fore.GREEN + "Rental ended, car marked available.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '3':
            cur.execute("SELECT * FROM rentals ORDER BY RentalID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '4':
            break
        else:
            print(Fore.YELLOW + "Invalid choice.")
def payment_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Payment Processing ---")
        print("1. Record Payment\n2. View Payments\n3. Update Payment Status\n4. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                pid = int(input("Payment ID: "))
                rid = int(input("Rental ID: "))
                paydate = input_date("Payment Date")
                method = input("Payment Method (Cash, CreditCard, DebitCard, Online): ")
                if method not in ('Cash', 'CreditCard', 'DebitCard', 'Online'):
                    print(Fore.YELLOW + "Invalid method.")
                    continue
                amount = float(input("Amount: "))
                status = input("Status (Paid, Pending, etc.): ")
                cur.execute("INSERT INTO payments (PaymentID, RentalID, PaymentDate, PaymentMethod, Amount, status) VALUES (%s,%s,%s,%s,%s,%s)", (pid, rid, paydate, method, amount, status))
                conn.commit()
                print(Fore.GREEN + "Payment recorded.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT PaymentID, RentalID, PaymentDate, PaymentMethod, Amount, status FROM payments ORDER BY PaymentID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            try:
                pid = int(input("Payment ID to update: "))
                status = input("New Status: ")
                cur.execute("UPDATE payments SET status=%s WHERE PaymentID=%s", (status, pid))
                conn.commit()
                print(Fore.GREEN + "Payment status updated.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            break
        else:
            print(Fore.YELLOW + "Invalid choice.")
def accident_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Accident History ---")
        print("1. Report Accident\n2. View Accidents\n3. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                aid = int(input("Accident ID: "))
                carid = int(input("Car ID: "))
                cid = int(input("Customer ID: "))
                adate = input_date("Accident Date")
                descr = input("Description: ")
                dmgcost_raw = input("Damage Cost (optional): ").strip()
                dmgcost = float(dmgcost_raw) if dmgcost_raw else None
                cur.execute("INSERT INTO accidenthistory (AccidentID, CarID, CustomerID, AccidentDate, Description, DamageCost) VALUES (%s,%s,%s,%s,%s,%s)",
                            (aid, carid, cid, adate, descr, dmgcost))
                conn.commit()
                print(Fore.GREEN + "Accident reported.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            cur.execute("SELECT * FROM accidenthistory ORDER BY AccidentID")
            rows = cur.fetchall()
            print_table(rows, headers="keys")
        elif choice == '3':
            break
        else:
            print(Fore.YELLOW + "Invalid choice.")
def transaction_menu(cur, conn):
    while True:
        print(Fore.CYAN + "\n--- Transaction History ---")
        print("1. View by RentalID\n2. View by CustomerID\n3. View by Date Range\n4. Back")
        choice = input("Choice: ")
        if choice == '1':
            try:
                rid = int(input("Rental ID: "))
                cur.execute("SELECT * FROM transactionhistory WHERE RentalID=%s ORDER BY TransactionDate", (rid,))
                rows = cur.fetchall()
                print_table(rows, ['TransactionID', 'RentalID', 'TransactionDate', 'TransactionDetails', 'Description'])
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '2':
            try:
                cid = int(input("Customer ID: "))
                cur.execute("""
                    SELECT th.*
                    FROM transactionhistory th
                    JOIN rentals r ON th.RentalID = r.RentalID
                    JOIN reservations res ON r.ReservationID = res.ReservationID
                    WHERE res.CustomerID = %s ORDER BY th.TransactionDate
                """, (cid,))
                rows = cur.fetchall()
                print_table(rows, ['TransactionID', 'RentalID', 'TransactionDate', 'TransactionDetails', 'Description'])
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '3':
            try:
                start = input_date("Start Date")
                end = input_date("End Date")
                cur.execute("SELECT * FROM transactionhistory WHERE TransactionDate BETWEEN %s AND %s ORDER BY TransactionDate", (start, end))
                rows = cur.fetchall()
                print_table(rows, headers="keys")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
        elif choice == '4':
            break
        else:
            print(Fore.YELLOW + "Invalid choice.")
def main_menu():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    try:
        while True:
            print(Fore.BLUE + "\n=== Car Rental Management System ===")
            print("1. Branch Management")
            print("2. Customer Management")
            print("3. Employee Management")
            print("4. Car Management")
            print("5. Location Management")
            print("6. Reservation Management")
            print("7. Rental Management")
            print("8. Payment Processing")
            print("9. Accident History")
            print("10. Transaction History")
            print("11. Exit")
            choice = input("Choice: ")
            if choice == '1':
                branch_menu(cur, conn)
            elif choice == '2':
                customer_menu(cur, conn)
            elif choice == '3':
                employee_menu(cur, conn)
            elif choice == '4':
                car_menu(cur, conn)
            elif choice == '5':
                location_menu(cur, conn)
            elif choice == '6':
                reservation_menu(cur, conn)
            elif choice == '7':
                rental_menu(cur, conn)
            elif choice == '8':
                payment_menu(cur, conn)
            elif choice == '9':
                accident_menu(cur, conn)
            elif choice == '10':
                transaction_menu(cur, conn)
            elif choice == '11':
                print(Fore.GREEN + "Goodbye!")
                break
            else:
                print(Fore.YELLOW + "Invalid choice.")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main_menu()
