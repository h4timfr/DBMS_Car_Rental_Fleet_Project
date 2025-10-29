import mysql.connector
conn = mysql.connector.connect(host='localhost',
                                password='Adithya3921*',
                                user='root')
if conn.is_connected():
    print("Connection is Established")

cur = conn.cursor()

def show_branches():
    cur.execute("SELECT * FROM branches")
    for row in cur.fetchall():
        print(row)
def insert_branch(ID,name, addr, phone):
    cur.execute("INSERT INTO branches (BranchID ,BranchName, address, PhoneNo) VALUES (%s, %s, %s, %s)", (ID,name, addr, phone))
    conn.commit()
    
def show_customers():
    cur.execute("SELECT * FROM customers")
    for row in cur.fetchall():
        print(row)
def insert_customer(ID,fname, lname, email, phone, addr, lic, dob):
    cur.execute("INSERT INTO customers (CustomerID,First_Name, Last_Name, Email, PhoneNo, Address, LicenseNumber, DateofBirth) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (ID ,fname, lname, email, phone, addr, lic, dob))
    conn.commit()
    
def show_employees():
    cur.execute("SELECT * FROM employees")
    for row in cur.fetchall():
        print(row)
        
def insert_employee(ID,fname, lname, role, branchid, email, phone):
    cur.execute("INSERT INTO employees (EmployeeID,FirstName, LastName, Role, BranchID, Email, PhoneNumber) VALUES (%s,%s,%s,%s,%s,%s,%s)", (ID,fname, lname, role, branchid, email, phone))
    conn.commit()

def show_cars():
    cur.execute("SELECT * FROM cars")
    for row in cur.fetchall():
        print(row)
        
def insert_car(ID,model, make, year, cartype, reg, status, branchid):
    cur.execute("INSERT INTO cars (CarID ,Model, Make, Year, CarType, RegistrationNumber, AvailabilityStatus, BranchID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (ID, model, make, year, cartype, reg, status, branchid))
    conn.commit()

def show_locations():
    cur.execute("SELECT * FROM locations")
    for row in cur.fetchall():
        print(row)
def insert_location(ID, branchid, address, pickup, dropoff):
    cur.execute("INSERT INTO locations (LocationID, BranchID, Address, IsPickupPoint, IsDropoffPoint) VALUES (%s,%s,%s,%s)", (ID, branchid, address, pickup, dropoff))
    conn.commit()

def show_reservations():
    cur.execute("SELECT * FROM reservations")
    for row in cur.fetchall():
        print(row)
        
def insert_reservation(ID, cid, carid, rdate, pickupid, dropoffid, status):
    cur.execute("INSERT INTO reservations (CustomerID, CarID, ReservationDate, PickupLocationID, DropoffLocationID, Status) VALUES (%s,%s,%s,%s,%s,%s,%s)", (ID, cid, carid, rdate, pickupid, dropoffid, status))
    conn.commit()

def show_rentals():
    cur.execute("SELECT * FROM rentals")
    for row in cur.fetchall():
        print(row)
        
def insert_rental(ID, resid, start, end, actual, totalcost):
    cur.execute("INSERT INTO rentals (RentalID,ReservationID, RentalStartDate, RentalEndDate, ActualReturnDate, TotalCost) VALUES (%s,%s,%s,%s,%s,%s)", (ID,resid, start, end, actual, totalcost))
    conn.commit()

def show_payments():
    cur.execute("SELECT * FROM payments")
    for row in cur.fetchall():
        print(row)
def insert_payment(ID,rentalid, paydate, method, amount, status):
    cur.execute("INSERT INTO payments (PaymentID,RentalID, PaymentDate, PaymentMethod, Amount, status) VALUES (%s,%s,%s,%s,%s,%s)", (ID,rentalid, paydate, method, amount, status))
    conn.commit()

def show_transactionhistory():
    cur.execute("SELECT * FROM transactionhistory")
    for row in cur.fetchall():
        print(row)
def insert_transaction(ID,rentalid, date, details, desc):
    cur.execute("INSERT INTO transactionhistory (RentalID, TransactionDate, TransactionDetails, Description) VALUES (%s,%s,%s,%s,%s)", (ID,rentalid, date, details, desc))
    conn.commit()

def show_accidenthistory():
    cur.execute("SELECT * FROM accidenthistory")
    for row in cur.fetchall():
        print(row)
def insert_accident(ID, carid, cid, adate, descr, dmgcost):
    cur.execute("INSERT INTO accidenthistory (AccidentID, CarID, CustomerID, AccidentDate, Description, DamageCost) VALUES (%s,%s,%s,%s,%s,%s)", (ID, carid, cid, adate, descr, dmgcost))
    conn.commit()

if __name__ == "__main__":
    cur.execute("USE Project")
    show_customers()
    pass

cur.close()
conn.close()
