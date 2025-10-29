from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Adithya3921*',  # Your password
        database='Project'        # Your database name
    )
    return conn
from datetime import datetime, timedelta
from decimal import Decimal

def calculate_dynamic_price(car_type, start_date, end_date, booking_date=None):
    """
    Calculate dynamic rental price based on multiple factors
    Returns: dict with price breakdown
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Parse dates
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
    if booking_date is None:
        booking_date = datetime.now()
    
    # Calculate rental duration
    duration = (end_date - start_date).days
    duration = max(duration, 1)  # Minimum 1 day
    
    # 1. Get base price from YOUR existing vehicle_pricing table
    cursor.execute("SELECT PricePerDay FROM vehicle_pricing WHERE CarType = %s", (car_type,))
    price_row = cursor.fetchone()
    base_price = float(price_row['PricePerDay']) if price_row else 1000.00
    
    # 2. Get seasonal multiplier
    start_month = start_date.month
    cursor.execute("""
        SELECT PriceMultiplier, SeasonName 
        FROM seasonal_pricing 
        WHERE (StartMonth <= EndMonth AND %s BETWEEN StartMonth AND EndMonth)
           OR (StartMonth > EndMonth AND (%s >= StartMonth OR %s <= EndMonth))
    """, (start_month, start_month, start_month))
    season = cursor.fetchone()
    season_multiplier = float(season['PriceMultiplier']) if season else 1.00
    season_name = season['SeasonName'] if season else 'Regular Season'
    
    # 3. Get availability factor (count available cars of this type)
    cursor.execute("""
        SELECT COUNT(*) as available_count 
        FROM cars 
        WHERE CarType = %s AND AvailabilityStatus = 'Available'
    """, (car_type,))
    availability = cursor.fetchone()
    available_count = availability['available_count'] if availability else 0
    
    # Availability multiplier: fewer cars = higher price
    if available_count <= 2:
        availability_multiplier = 1.30  # High demand (30% increase)
        availability_status = "High Demand"
    elif available_count <= 5:
        availability_multiplier = 1.15  # Moderate demand (15% increase)
        availability_status = "Moderate Demand"
    else:
        availability_multiplier = 1.00  # Normal
        availability_status = "Good Availability"
    
    # 4. Get duration discount
    cursor.execute("""
        SELECT DiscountPercent, DiscountName 
        FROM duration_discounts 
        WHERE MinDays <= %s AND (MaxDays IS NULL OR MaxDays >= %s)
        ORDER BY MinDays DESC LIMIT 1
    """, (duration, duration))
    discount_row = cursor.fetchone()
    duration_discount_percent = float(discount_row['DiscountPercent']) if discount_row else 0.00
    discount_name = discount_row['DiscountName'] if discount_row else 'No Discount'
    
    # 5. Early booking discount (book 7+ days in advance)
    days_in_advance = (start_date - booking_date).days
    early_booking_discount = 0.00
    if days_in_advance >= 30:
        early_booking_discount = 10.00  # 10% off
        early_booking_name = "🎁 Early Bird (30+ days)"
    elif days_in_advance >= 14:
        early_booking_discount = 5.00  # 5% off
        early_booking_name = "🎁 Advance Booking (14+ days)"
    else:
        early_booking_name = "No Early Booking Discount"
    
    # 6. Weekend/Holiday surcharge
    weekend_surcharge = 0.00
    if start_date.weekday() >= 5:  # Saturday or Sunday
        weekend_surcharge = 10.00  # 10% surcharge
        weekend_name = "⚠️ Weekend Surcharge"
    else:
        weekend_name = "No Weekend Surcharge"
    
    cursor.close()
    conn.close()
    
    # === CALCULATE FINAL PRICE ===
    # Base calculation (convert everything to float)
    subtotal = base_price * duration
    
    # Apply seasonal and availability multipliers
    subtotal_with_multipliers = subtotal * season_multiplier * availability_multiplier
    
    # Calculate discount amounts
    duration_discount_amount = (subtotal_with_multipliers * duration_discount_percent / 100.0)
    early_booking_discount_amount = (subtotal_with_multipliers * early_booking_discount / 100.0)
    
    # Calculate surcharge
    weekend_surcharge_amount = (subtotal_with_multipliers * weekend_surcharge / 100.0)
    
    # Final total
    total_price = subtotal_with_multipliers - duration_discount_amount - early_booking_discount_amount + weekend_surcharge_amount
    
    # Apply minimum pricing rule (never below 50% of original base price)
    minimum_price = base_price * duration * 0.5
    total_price = max(total_price, minimum_price)
    
    # Calculate total savings
    total_savings = duration_discount_amount + early_booking_discount_amount
    
    # Return detailed breakdown (all as float)
    return {
        'base_price': float(base_price),
        'duration': int(duration),
        'base_subtotal': float(subtotal),
        'season_name': season_name,
        'season_multiplier': float(season_multiplier),
        'available_cars': int(available_count),
        'availability_status': availability_status,
        'availability_multiplier': float(availability_multiplier),
        'subtotal_after_multipliers': float(subtotal_with_multipliers),
        'duration_discount_percent': float(duration_discount_percent),
        'duration_discount_name': discount_name,
        'duration_discount_amount': float(duration_discount_amount),
        'early_booking_discount': float(early_booking_discount),
        'early_booking_name': early_booking_name,
        'early_booking_amount': float(early_booking_discount_amount),
        'weekend_surcharge_percent': float(weekend_surcharge),
        'weekend_name': weekend_name,
        'weekend_surcharge_amount': float(weekend_surcharge_amount),
        'total_price': round(float(total_price), 2),
        'savings': round(float(total_savings), 2)
    }

# ==================== MAIN PAGES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get key metrics
        cursor.execute("SELECT COUNT(*) as total_cars FROM cars")
        result = cursor.fetchone()
        total_cars = result['total_cars'] if result else 0
        
        cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
        result = cursor.fetchone()
        total_customers = result['total_customers'] if result else 0
        
        cursor.execute("SELECT COUNT(*) as active_rentals FROM rentals WHERE ActualReturnDate IS NULL")
        result = cursor.fetchone()
        active_rentals = result['active_rentals'] if result else 0
        
        cursor.execute("SELECT COALESCE(SUM(TotalCost), 0) as total_revenue FROM rentals")
        result = cursor.fetchone()
        total_revenue = result['total_revenue'] if result else 0
        
        # Get recent activities (last 10 activities)
        recent_activities = []
        
        # Recent Reservations
        cursor.execute("""
            SELECT 'Reservation' as activity_type, 
                   CONCAT('New reservation by ', c.First_Name, ' ', c.Last_Name) as description,
                   r.ReservationDate as activity_date,
                   'success' as status,
                   r.ReservationID as item_id
            FROM reservations r
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            ORDER BY r.ReservationDate DESC
            LIMIT 3
        """)
        recent_activities.extend(cursor.fetchall())
        
        # Recent Rentals
        cursor.execute("""
            SELECT 'Rental' as activity_type,
                   CONCAT('Car rented by ', c.First_Name, ' ', c.Last_Name) as description,
                   rt.RentalStartDate as activity_date,
                   CASE WHEN rt.ActualReturnDate IS NULL THEN 'warning' ELSE 'info' END as status,
                   rt.RentalID as item_id
            FROM rentals rt
            LEFT JOIN reservations r ON rt.ReservationID = r.ReservationID
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            ORDER BY rt.RentalStartDate DESC
            LIMIT 3
        """)
        recent_activities.extend(cursor.fetchall())
        
        # Recent Payments
        cursor.execute("""
            SELECT 'Payment' as activity_type,
                   CONCAT('Payment received ₹', FORMAT(p.Amount, 0)) as description,
                   p.PaymentDate as activity_date,
                   'success' as status,
                   p.PaymentID as item_id
            FROM payments p
            ORDER BY p.PaymentDate DESC
            LIMIT 4
        """)
        recent_activities.extend(cursor.fetchall())
        
        # Sort all activities by date and limit to 10
        recent_activities = sorted(recent_activities, key=lambda x: x['activity_date'] or datetime.min, reverse=True)[:10]
        
    except Exception as e:
        print(f"Database error: {e}")
        total_cars = 0
        total_customers = 0
        active_rentals = 0
        total_revenue = 0
        recent_activities = []
        
    finally:
        cursor.close()
        conn.close()
    
    return render_template('dashboard.html', 
                         total_cars=total_cars,
                         total_customers=total_customers,
                         active_rentals=active_rentals,
                         total_revenue=total_revenue,
                         recent_activities=recent_activities)

# ==================== BRANCH MANAGEMENT ====================
@app.route('/branches')
def branches():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT BranchId, BranchName, address, PhoneNo FROM branches ORDER BY BranchId")
        branches_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching branches: {e}")
        branches_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('branches.html', branches=branches_data)

@app.route('/add_branch', methods=['GET', 'POST'])
def add_branch():
    if request.method == 'POST':
        branch_id = request.form['branch_id']
        branch_name = request.form['branch_name']
        address = request.form['address']
        phone = request.form['phone']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO branches (BranchId, BranchName, address, PhoneNo) VALUES (%s, %s, %s, %s)",
                (branch_id, branch_name, address, phone)
            )
            conn.commit()
            flash('Branch added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add_branch.html')

@app.route('/edit_branch/<int:branch_id>', methods=['GET', 'POST'])
def edit_branch(branch_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        branch_name = request.form['branch_name']
        address = request.form['address']
        phone = request.form['phone']
        
        try:
            cursor.execute(
                "UPDATE branches SET BranchName=%s, address=%s, PhoneNo=%s WHERE BranchId=%s",
                (branch_name, address, phone, branch_id)
            )
            conn.commit()
            flash('Branch updated successfully!', 'success')
            return redirect(url_for('branches'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    try:
        cursor.execute("SELECT * FROM branches WHERE BranchId=%s", (branch_id,))
        branch = cursor.fetchone()
        if not branch:
            flash('Branch not found!', 'error')
            return redirect(url_for('branches'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('branches'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_branch.html', branch=branch)

@app.route('/delete_branch/<int:branch_id>')
def delete_branch(branch_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM branches WHERE BranchId=%s", (branch_id,))
        conn.commit()
        flash('Branch deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('branches'))
# ==================== LOCATION MANAGEMENT ====================
@app.route('/locations')
def locations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM locations ORDER BY LocationID")
        locations_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching locations: {e}")
        locations_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('locations.html', locations=locations_data)

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_id = request.form['location_id']
        branch_id = request.form['branch_id']
        address = request.form['address']
        is_pickup = 1 if request.form.get('is_pickup') else 0
        is_dropoff = 1 if request.form.get('is_dropoff') else 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO locations (LocationID, BranchID, Address, IsPickupPoint, IsDropoffPoint) VALUES (%s, %s, %s, %s, %s)",
                (location_id, branch_id, address, is_pickup, is_dropoff)
            )
            conn.commit()
            flash('Location added successfully!', 'success')
            return redirect(url_for('locations'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    # Get branches for dropdown
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT BranchId, BranchName FROM branches")
        branches = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching branches: {e}")
        branches = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('add_location.html', branches=branches)

@app.route('/edit_location/<int:location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        branch_id = request.form['branch_id']
        address = request.form['address']
        is_pickup = 1 if request.form.get('is_pickup') else 0
        is_dropoff = 1 if request.form.get('is_dropoff') else 0
        
        try:
            cursor.execute(
                "UPDATE locations SET BranchID=%s, Address=%s, IsPickupPoint=%s, IsDropoffPoint=%s WHERE LocationID=%s",
                (branch_id, address, is_pickup, is_dropoff, location_id)
            )
            conn.commit()
            flash('Location updated successfully!', 'success')
            return redirect(url_for('locations'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    try:
        cursor.execute("SELECT * FROM locations WHERE LocationID=%s", (location_id,))
        location = cursor.fetchone()
        if not location:
            flash('Location not found!', 'error')
            return redirect(url_for('locations'))
        
        cursor.execute("SELECT BranchId, BranchName FROM branches")
        branches = cursor.fetchall()
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('locations'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_location.html', location=location, branches=branches)

@app.route('/delete_location/<int:location_id>')
def delete_location(location_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM locations WHERE LocationID=%s", (location_id,))
        conn.commit()
        flash('Location deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('locations'))

# ==================== CUSTOMER MANAGEMENT ====================
@app.route('/customers')
def customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customers ORDER BY CustomerID")
        customers_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching customers: {e}")
        customers_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('customers.html', customers=customers_data)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        license_number = request.form['license_number']
        date_of_birth = request.form['date_of_birth']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO customers (CustomerID, First_Name, Last_Name, Email, PhoneNo, Address, LicenseNumber, DateofBirth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (customer_id, first_name, last_name, email, phone, address, license_number, date_of_birth)
            )
            conn.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add_customer.html')

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        license_number = request.form['license_number']
        date_of_birth = request.form['date_of_birth']
        
        try:
            cursor.execute(
                "UPDATE customers SET First_Name=%s, Last_Name=%s, Email=%s, PhoneNo=%s, Address=%s, LicenseNumber=%s, DateofBirth=%s WHERE CustomerID=%s",
                (first_name, last_name, email, phone, address, license_number, date_of_birth, customer_id)
            )
            conn.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    try:
        cursor.execute("SELECT * FROM customers WHERE CustomerID=%s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            flash('Customer not found!', 'error')
            return redirect(url_for('customers'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('customers'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE CustomerID=%s", (customer_id,))
        conn.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('customers'))

# ==================== CAR MANAGEMENT ====================
@app.route('/cars')
def cars():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.*, b.BranchName 
            FROM cars c 
            LEFT JOIN branches b ON c.BranchID = b.BranchId 
            ORDER BY c.CarID
        """)
        cars_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching cars: {e}")
        cars_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('cars.html', cars=cars_data)

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        car_id = request.form['car_id']
        model = request.form['model']
        make = request.form['make']
        year = request.form['year']
        car_type = request.form['car_type']
        registration_number = request.form['registration_number']
        branch_id = request.form['branch_id']
        availability_status = request.form['availability_status']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO cars (CarID, Model, Make, Year, CarType, RegistrationNumber, AvailabilityStatus, BranchID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (car_id, model, make, year, car_type, registration_number, availability_status, branch_id)
            )
            conn.commit()
            flash('Car added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT BranchId, BranchName FROM branches")
        branches = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching branches: {e}")
        branches = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('add_car.html', branches=branches)

@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        model = request.form['model']
        make = request.form['make']
        year = request.form['year']
        car_type = request.form['car_type']
        registration_number = request.form['registration_number']
        branch_id = request.form['branch_id']
        availability_status = request.form['availability_status']
        
        try:
            cursor.execute(
                "UPDATE cars SET Model=%s, Make=%s, Year=%s, CarType=%s, RegistrationNumber=%s, BranchID=%s, AvailabilityStatus=%s WHERE CarID=%s",
                (model, make, year, car_type, registration_number, branch_id, availability_status, car_id)
            )
            conn.commit()
            flash('Car updated successfully!', 'success')
            return redirect(url_for('cars'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    try:
        cursor.execute("SELECT * FROM cars WHERE CarID=%s", (car_id,))
        car = cursor.fetchone()
        if not car:
            flash('Car not found!', 'error')
            return redirect(url_for('cars'))
        
        cursor.execute("SELECT BranchId, BranchName FROM branches")
        branches = cursor.fetchall()
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('cars'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_car.html', car=car, branches=branches)

@app.route('/delete_car/<int:car_id>')
def delete_car(car_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cars WHERE CarID=%s", (car_id,))
        conn.commit()
        flash('Car deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('cars'))

# ==================== RENTAL MANAGEMENT ====================
@app.route('/rentals')
def rentals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT rt.*, 
                   r.CustomerID,
                   CONCAT(c.First_Name, ' ', c.Last_Name) as CustomerName
            FROM rentals rt
            LEFT JOIN reservations r ON rt.ReservationID = r.ReservationID
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            ORDER BY rt.RentalID
        """)
        rentals_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching rentals: {e}")
        rentals_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('rentals.html', rentals=rentals_data)

from datetime import datetime

@app.route('/add_rental', methods=['GET', 'POST'])
def add_rental():
    if request.method == 'POST':
        rental_id = request.form['rental_id']
        reservation_id = request.form['reservation_id']
        rental_start_date = request.form['rental_start_date']
        rental_end_date = request.form['rental_end_date']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get car type from reservation
        cursor.execute("""
            SELECT c.CarType 
            FROM reservations r 
            JOIN cars c ON r.CarID = c.CarID 
            WHERE r.ReservationID = %s
        """, (reservation_id,))
        result = cursor.fetchone()
        
        if not result:
            flash('Invalid reservation!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('add_rental'))
        
        car_type = result['CarType']
        
        # Calculate dynamic price
        price_breakdown = calculate_dynamic_price(car_type, rental_start_date, rental_end_date)
        total_cost = price_breakdown['total_price']
        
        try:
            cursor.execute(
                "INSERT INTO rentals (RentalID, ReservationID, RentalStartDate, RentalEndDate, TotalCost) VALUES (%s, %s, %s, %s, %s)",
                (rental_id, reservation_id, rental_start_date, rental_end_date, total_cost)
            )
            conn.commit()
            
            flash(f'✅ Rental added! Total: ₹{total_cost:.2f} for {price_breakdown["duration"]} days. You saved ₹{price_breakdown["savings"]:.2f}!', 'success')
            return redirect(url_for('rentals'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    # GET request: load reservations
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.ReservationID, 
                   CONCAT(c.First_Name, ' ', c.Last_Name) as CustomerName,
                   CONCAT(car.Make, ' ', car.Model, ' (', car.CarType, ')') as CarInfo
            FROM reservations r 
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            LEFT JOIN cars car ON r.CarID = car.CarID
            WHERE r.Status = 'Confirmed'
        """)
        reservations = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        reservations = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('add_rental.html', reservations=reservations)

@app.route('/api/calculate_price', methods=['POST'])
def api_calculate_price():
    """API endpoint for real-time price calculation"""
    data = request.get_json()
    
    car_type = data.get('car_type')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not all([car_type, start_date, end_date]):
        return {'error': 'Missing required fields'}, 400
    
    try:
        price_breakdown = calculate_dynamic_price(car_type, start_date, end_date)
        return price_breakdown
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/edit_rental/<int:rental_id>', methods=['GET', 'POST'])
def edit_rental(rental_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        reservation_id = request.form['reservation_id']
        rental_start_date = request.form['rental_start_date']
        rental_end_date = request.form['rental_end_date']
        actual_return_date = request.form.get('actual_return_date', None)
        
        # Handle empty actual_return_date
        if actual_return_date == '':
            actual_return_date = None
        
        # Get the OLD rental data to check if this is a NEW closure
        cursor.execute("SELECT ActualReturnDate FROM rentals WHERE RentalID = %s", (rental_id,))
        old_rental = cursor.fetchone()
        was_already_closed = old_rental and old_rental['ActualReturnDate'] is not None
        is_now_being_closed = actual_return_date is not None and not was_already_closed
        
        # Get car type and CarID from reservation for price recalculation
        cursor.execute("""
            SELECT c.CarType, c.CarID
            FROM reservations r 
            JOIN cars c ON r.CarID = c.CarID 
            WHERE r.ReservationID = %s
        """, (reservation_id,))
        result = cursor.fetchone()
        
        if result:
            car_type = result['CarType']
            car_id = result['CarID']
            # Recalculate price with new dates
            price_breakdown = calculate_dynamic_price(car_type, rental_start_date, rental_end_date)
            total_cost = price_breakdown['total_price']
        else:
            # Fallback to form input if car type not found
            total_cost = float(request.form.get('total_cost', 0))
            car_id = None
        
        try:
            # Update the rental
            cursor.execute(
                "UPDATE rentals SET ReservationID=%s, RentalStartDate=%s, RentalEndDate=%s, TotalCost=%s, ActualReturnDate=%s WHERE RentalID=%s",
                (reservation_id, rental_start_date, rental_end_date, total_cost, actual_return_date, rental_id)
            )
            conn.commit()
            
            # === AUTO-RELEASE CAR WHEN RENTAL IS CLOSED ===
            if is_now_being_closed and car_id:
                cursor.execute(
                    "UPDATE cars SET AvailabilityStatus = 'Available' WHERE CarID = %s",
                    (car_id,)
                )
                conn.commit()
                flash(f'✅ Rental closed! Car #{car_id} is now AVAILABLE for rent again. Payment record created: ₹{total_cost:.2f}', 'success')
            
            # === AUTO-CREATE PAYMENT IF RENTAL IS BEING CLOSED ===
            if is_now_being_closed:
                # Check if payment already exists for this rental
                cursor.execute("SELECT PaymentID FROM payments WHERE RentalID = %s", (rental_id,))
                existing_payment = cursor.fetchone()
                
                if not existing_payment:
                    # Generate new payment ID (find max + 1)
                    cursor.execute("SELECT IFNULL(MAX(PaymentID), 6000) + 1 as new_id FROM payments")
                    new_payment_id_result = cursor.fetchone()
                    new_payment_id = new_payment_id_result['new_id'] if new_payment_id_result else 6001
                    
                    # Create payment record with 'Pending' as payment method
                    cursor.execute("""
                        INSERT INTO payments 
                        (PaymentID, RentalID, PaymentDate, Amount, PaymentMethod, status) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        new_payment_id,
                        rental_id,
                        actual_return_date,  # Payment date = return date
                        total_cost,
                        'Pending',  # Set PaymentMethod to 'Pending'
                        'Pending'   # Status also set to Pending
                    ))
                    conn.commit()
            
            if not is_now_being_closed:
                flash(f'✅ Rental updated! New total: ₹{total_cost:.2f}', 'success')
            
            cursor.close()
            conn.close()
            return redirect(url_for('rentals'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('rentals'))
    
    # GET request - show the form with current data and price breakdown
    try:
        cursor.execute("SELECT * FROM rentals WHERE RentalID=%s", (rental_id,))
        rental = cursor.fetchone()
        if not rental:
            flash('Rental not found!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('rentals'))
        
        # Get car type for price breakdown
        cursor.execute("""
            SELECT c.CarType, CONCAT(c.Make, ' ', c.Model) as CarName
            FROM reservations r 
            JOIN cars c ON r.CarID = c.CarID 
            WHERE r.ReservationID = %s
        """, (rental['ReservationID'],))
        car_info = cursor.fetchone()
        
        # Calculate current price breakdown
        price_breakdown = None
        if car_info:
            car_type = car_info['CarType']
            price_breakdown = calculate_dynamic_price(
                car_type, 
                rental['RentalStartDate'], 
                rental['RentalEndDate']
            )
        
        # Get reservations for dropdown
        cursor.execute("""
            SELECT r.ReservationID, 
                   CONCAT(c.First_Name, ' ', c.Last_Name) as CustomerName,
                   CONCAT(car.Make, ' ', car.Model, ' (', car.CarType, ')') as CarInfo
            FROM reservations r 
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            LEFT JOIN cars car ON r.CarID = car.CarID
        """)
        reservations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('edit_rental.html', 
                             rental=rental, 
                             reservations=reservations,
                             price_breakdown=price_breakdown,
                             car_info=car_info)
                             
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('rentals'))





@app.route('/delete_rental/<int:rental_id>')
def delete_rental(rental_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM rentals WHERE RentalID=%s", (rental_id,))
        conn.commit()
        flash('Rental deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rentals'))

# ==================== RESERVATION MANAGEMENT ====================
@app.route('/reservations')
def reservations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, 
                   CONCAT(c.First_Name, ' ', c.Last_Name) as CustomerName,
                   CONCAT(car.Make, ' ', car.Model) as CarInfo
            FROM reservations r 
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            LEFT JOIN cars car ON r.CarID = car.CarID
            ORDER BY r.ReservationID
        """)
        reservations_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching reservations: {e}")
        reservations_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('reservations.html', reservations=reservations_data)

@app.route('/add_reservation', methods=['GET', 'POST'])
def add_reservation():
    if request.method == 'POST':
        reservation_id = request.form['reservation_id']
        customer_id = request.form['customer_id']
        car_id = request.form['car_id']
        reservation_date = request.form['reservation_date']
        pickup_location_id = request.form['pickup_location_id']
        dropoff_location_id = request.form['dropoff_location_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO reservations (ReservationID, CustomerID, CarID, ReservationDate, PickupLocationID, DropoffLocationID, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (reservation_id, customer_id, car_id, reservation_date, pickup_location_id, dropoff_location_id, 'Confirmed')
            )
            conn.commit()
            flash('Reservation added successfully!', 'success')
            return redirect(url_for('reservations'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    # GET request - Fetch all dropdown data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    customers = []
    cars = []
    pickup_locations = []
    dropoff_locations = []
    
    try:
        # Fetch customers
        cursor.execute("SELECT CustomerID, First_Name, Last_Name FROM customers ORDER BY First_Name")
        customers_raw = cursor.fetchall()
        customers = [{'CustomerID': c['CustomerID'], 'CustomerName': f"{c['First_Name']} {c['Last_Name']}"} for c in customers_raw]
        print(f"✅ Customers fetched: {len(customers)}")
        
    except Exception as e:
        print(f"❌ Error fetching customers: {e}")
    
    try:
        # Fetch available cars
        cursor.execute("SELECT CarID, Make, Model, CarType FROM cars WHERE AvailabilityStatus = 'Available' ORDER BY Make, Model")
        cars_raw = cursor.fetchall()
        cars = [{'CarID': c['CarID'], 'CarName': f"{c['Make']} {c['Model']} ({c['CarType']})"} for c in cars_raw]
        print(f"✅ Available cars fetched: {len(cars)}")
        
    except Exception as e:
        print(f"❌ Error fetching cars: {e}")
    
    try:
        # Fetch pickup locations
        cursor.execute("SELECT LocationID, Address FROM locations WHERE IsPickupPoint = 1 ORDER BY Address")
        pickup_raw = cursor.fetchall()
        pickup_locations = [{'LocationID': l['LocationID'], 'LocationName': l['Address']} for l in pickup_raw]
        print(f"✅ Pickup locations fetched: {len(pickup_locations)}")
        
    except Exception as e:
        print(f"❌ Error fetching pickup locations: {e}")
    
    try:
        # Fetch dropoff locations
        cursor.execute("SELECT LocationID, Address FROM locations WHERE IsDropoffPoint = 1 ORDER BY Address")
        dropoff_raw = cursor.fetchall()
        dropoff_locations = [{'LocationID': l['LocationID'], 'LocationName': l['Address']} for l in dropoff_raw]
        print(f"✅ Dropoff locations fetched: {len(dropoff_locations)}")
        
    except Exception as e:
        print(f"❌ Error fetching dropoff locations: {e}")
    
    cursor.close()
    conn.close()
    
    print(f"📊 FINAL COUNTS - Customers: {len(customers)}, Cars: {len(cars)}, Pickup: {len(pickup_locations)}, Dropoff: {len(dropoff_locations)}")
    
    return render_template('add_reservation.html', 
                         customers=customers, 
                         cars=cars, 
                         pickup_locations=pickup_locations,
                         dropoff_locations=dropoff_locations)



@app.route('/edit_reservation/<int:reservation_id>', methods=['GET', 'POST'])
def edit_reservation(reservation_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        car_id = request.form['car_id']
        reservation_date = request.form['reservation_date']
        pickup_location_id = request.form['pickup_location_id']
        dropoff_location_id = request.form['dropoff_location_id']
        status = request.form['status']
        
        try:
            cursor.execute(
                "UPDATE reservations SET CustomerID=%s, CarID=%s, ReservationDate=%s, PickupLocationID=%s, DropoffLocationID=%s, Status=%s WHERE ReservationID=%s",
                (customer_id, car_id, reservation_date, pickup_location_id, dropoff_location_id, status, reservation_id)
            )
            conn.commit()
            flash('Reservation updated successfully!', 'success')
            return redirect(url_for('reservations'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    try:
        cursor.execute("SELECT * FROM reservations WHERE ReservationID=%s", (reservation_id,))
        reservation = cursor.fetchone()
        if not reservation:
            flash('Reservation not found!', 'error')
            return redirect(url_for('reservations'))
        
        cursor.execute("SELECT CustomerID, CONCAT(First_Name, ' ', Last_Name) as CustomerName FROM customers")
        customers = cursor.fetchall()
        
        cursor.execute("SELECT CarID, CONCAT(Make, ' ', Model) as CarName FROM cars WHERE AvailabilityStatus = 'Available'")
        cars = cursor.fetchall()
        
        locations = []
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('reservations'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_reservation.html', reservation=reservation, customers=customers, cars=cars, locations=locations)

@app.route('/delete_reservation/<int:reservation_id>')
def delete_reservation(reservation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservations WHERE ReservationID=%s", (reservation_id,))
        conn.commit()
        flash('Reservation deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('reservations'))

# ==================== PAYMENT MANAGEMENT ====================
@app.route('/payments')
def payments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.*, 
                   rt.RentalID,
                   CONCAT(c.First_Name, ' ', c.Last_Name) as CustomerName
            FROM payments p
            LEFT JOIN rentals rt ON p.RentalID = rt.RentalID
            LEFT JOIN reservations r ON rt.ReservationID = r.ReservationID
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            ORDER BY p.PaymentID
        """)
        payments_data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching payments: {e}")
        payments_data = []
    finally:
        cursor.close()
        conn.close()
    return render_template('payments.html', payments=payments_data)

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        payment_id = request.form['payment_id']
        rental_id = request.form['rental_id']
        payment_date = request.form['payment_date']
        amount = request.form['amount']
        payment_method = request.form['payment_method']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO payments (PaymentID, RentalID, PaymentDate, Amount, PaymentMethod) VALUES (%s, %s, %s, %s, %s)",
                (payment_id, rental_id, payment_date, amount, payment_method)
            )
            conn.commit()
            flash('Payment added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT rt.RentalID, 
                   CONCAT(c.First_Name, ' ', c.Last_Name) as CustomerName,
                   rt.TotalCost
            FROM rentals rt
            LEFT JOIN reservations r ON rt.ReservationID = r.ReservationID
            LEFT JOIN customers c ON r.CustomerID = c.CustomerID
            WHERE rt.ActualReturnDate IS NULL
        """)
        rentals = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching rentals: {e}")
        rentals = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('add_payment.html', rentals=rentals)

@app.route('/edit_payment/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        rental_id = request.form['rental_id']
        payment_date = request.form['payment_date']
        amount = request.form['amount']
        payment_method = request.form['payment_method']
        status = request.form['status']  # Get status from form
        
        try:
            cursor.execute(
                "UPDATE payments SET RentalID=%s, PaymentDate=%s, Amount=%s, PaymentMethod=%s, status=%s WHERE PaymentID=%s",
                (rental_id, payment_date, amount, payment_method, status, payment_id)
            )
            conn.commit()
            
            if status == 'Completed' and payment_method != 'Pending':
                flash(f'✅ Payment #{payment_id} completed successfully! Method: {payment_method}', 'success')
            else:
                flash(f'Payment #{payment_id} updated successfully!', 'success')
                
            return redirect(url_for('payments'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    try:
        cursor.execute("SELECT * FROM payments WHERE PaymentID=%s", (payment_id,))
        payment = cursor.fetchone()
        if not payment:
            flash('Payment not found!', 'error')
            return redirect(url_for('payments'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('payments'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_payment.html', payment=payment)

    
@app.route('/delete_payment/<int:payment_id>')
def delete_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM payments WHERE PaymentID=%s", (payment_id,))
        conn.commit()
        flash('Payment deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('payments'))
@app.route('/map')
def map_view():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
