from flask import Flask, render_template, request, redirect, json, jsonify, url_for
from markupsafe import Markup
from datetime import datetime, timedelta, time
import re
import pyodbc

app = Flask(__name__)

# Azure SQL Database Configuration
DATABASE_CONFIG = {
    'server': 'debbiesdoggroomingsalon.database.windows.net',
    'database': 'debbiesrecords',
    'username': 'aidanxcannon',
    'password': 'Unbroken556%',
    'driver': '{ODBC Driver 18 for SQL Server}'
}

# Construct the connection string
CONNECTION_STRING = f"DRIVER={DATABASE_CONFIG['driver']};SERVER={DATABASE_CONFIG['server']},1433;DATABASE={DATABASE_CONFIG['database']};UID={DATABASE_CONFIG['username']};PWD={DATABASE_CONFIG['password']}"

appointment_columns = ['id', 'dog_name', 'dog_breed', 'owner_first_name', 'owner_last_name',
                       'phone_number', 'scheduled_date', 'ap_time', 'notes', 'arrived']

def get_db_connection():
    return pyodbc.connect(CONNECTION_STRING)

@app.route('/')
def index():
    return render_template('index.html')


#Employee route
@app.route('/employee_page')
def employee_page():
    return render_template('employee_page.html')

@app.route('/boarding', methods=['GET', 'POST'])
def boarding_signin():
    try:
        if request.method == 'POST':
                dog_name=request.form['dog_name'],
                dog_breed=request.form['dog_breed'],
                owner_first_name=request.form['owner_first_name'],
                owner_last_name=request.form['owner_last_name'],
                phone_number=request.form['phone_number'],
                drop_off_date=datetime.now(),
                pick_up_date=request.form['pick_up_date'],
                bath=request.form.get('bath') == 'on',
                meds=request.form.get('meds') == 'on',
                shop_food=request.form.get('shop_food') == 'on',
                spay_neutered=request.form.get('spay_neutered') == 'on',
                notes=request.form['notes'],
                med_info=request.form['med_info'],
                food_info=request.form['food_info']
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath, meds, shop_food, spay_neutered, notes, med_info, food_info) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath,
                     meds, shop_food, spay_neutered, notes, med_info, food_info))
                connection.commit()
                connection.close()
                return redirect('/thankyou')
        return render_template('boarding_signin.html')
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error processing the boarding sign-in."


@app.route('/grooming', methods=['GET', 'POST'])
def grooming_signin():
    if request.method == 'POST':
        dog_name = request.form['dog_name']
        owner_first_name = request.form['owner_first_name']
        owner_last_name = request.form['owner_last_name']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM dog_grooming WHERE dog_name=? AND owner_first_name=? AND owner_last_name=?", (dog_name, owner_first_name, owner_last_name))
        options = cursor.fetchall()
        connection.close()

        if options:
            # If the entry is found, redirect to the grooming check-in page for that entry
            return redirect(f'/grooming/{options[0][0]}/checkin')
        else:
            # If no entry is found, display an error message and pass the form data back to the template
            error_message = "No dog found."
            return render_template('grooming_signin.html', error_message=error_message, dog_name=dog_name,
                                   owner_first_name=owner_first_name, owner_last_name=owner_last_name)

    return render_template('grooming_signin.html')

@app.route('/grooming_checkin', methods=['GET', 'POST'])
def grooming_checkin(entry_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dog_grooming WHERE id=?", (entry_id,))
    entry = cursor.fetchone()

    if request.method == 'POST':
        arrived = request.form.get('arrived') == 'on'
        cursor.execute("UPDATE dog_grooming SET arrived=1 WHERE id=?", (entry_id,))
        connection.commit()
        connection.close()
        return redirect('/check_in')

    connection.close()
    return render_template('grooming_checkin.html', entry=entry)


@app.route('/records')
def records():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath, meds, shop_food, spay_neutered, notes FROM dog_boarding")
    records = cursor.fetchall()
    connection.close()

    formatted_records = []
    for record in records:
        drop_off_date_str = record.drop_off_date.strftime('%Y-%m-%d') if record.drop_off_date else None
        pick_up_date_str = record.pick_up_date.strftime('%Y-%m-%d') if record.pick_up_date else None
        formatted_drop_off_date = format_date_with_suffix(drop_off_date_str)
        formatted_pick_up_date = format_date_with_suffix(pick_up_date_str)
        bath = "Yes" if record.bath else "No"
        meds = "Yes" if record.meds else "No"
        shop_food = "Yes" if record.shop_food else "No"
        spay_neutered = "Yes" if record.spay_neutered else "No"
        formatted_record = (record.id, record.dog_name, record.dog_breed, record.owner_first_name, record.owner_last_name,
                            record.phone_number, formatted_drop_off_date, formatted_pick_up_date, bath, meds, shop_food,
                            spay_neutered, record.notes)
        formatted_records.append(formatted_record)

    sorted_records = sorted(formatted_records,
                            key=lambda x: datetime.strptime(remove_suffix(x[7]), '%B %d, %Y') if isinstance(x[7],
                                                                                                           str) else datetime.max)

    return render_template('records.html', records=sorted_records)

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    try:
        return render_template('calendar.html')
    except Exception as e:
        print(f"Error in calendar function: {e}")
        return render_template('calendar.html', error_message="There was an error while fetching appointments.")

@app.route('/api/fetch_appointments', methods=['GET'])
def fetch_appointments():
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch all appointments from the database
        cursor.execute("SELECT * FROM dog_grooming")
        appointment_list = cursor.fetchall()

        # Convert the raw data from the database into the desired format
        appointments = []
        for appointment in appointment_list:
            ap_datetime = datetime.combine(appointment[6], appointment[7] if appointment[7] else time(0,0))
            appointments.append({
                'title': appointment[1],  # Using dog's name as the title
                'start': ap_datetime.isoformat(),
                'end': (ap_datetime + timedelta(hours=.25)).isoformat(),  # Assuming each appointment is 1 hour
                'extendedProps': {
                    'dog_breed': appointment[2],
                    'owner_first_name': appointment[3],
                    'owner_last_name': appointment[4],
                    'phone_number': appointment[5],
                    'notes': appointment[8],
                    'arrived': appointment[9]
                }
            })

        return jsonify(appointments)

    except Exception as e:
        print(f"Error in fetch_appointments function: {e}")
        return jsonify([]), 500


@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    try:
        print(request.form)
        connection = get_db_connection()
        cursor = connection.cursor()
        print(request.form)

        dog_name = request.form['dog_name']
        dog_breed = request.form['dog_breed']
        owner_first_name = request.form['owner_first_name']
        owner_last_name = request.form['owner_last_name']
        phone_number = request.form['phone_number']
        scheduled_date = request.form['scheduled_date']
        ap_time = request.form['ap_time']
        notes = request.form['notes']
        arrived = False

        # Debug prints
        print("Debug Values:")
        print("Dog Name:", dog_name)
        print("Dog Breed:", dog_breed)
        print("Owner First Name:", owner_first_name)
        print("Owner Last Name:", owner_last_name)
        print("Phone Number:", phone_number)
        print("Scheduled Date:", scheduled_date)
        print("Appointment Time:", ap_time)
        print("Notes:", notes)

        query = """
            INSERT INTO dog_grooming 
            (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, scheduled_date, ap_time, notes, arrived) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
        dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, scheduled_date, ap_time, notes, arrived))

        connection.commit()
        return redirect(url_for('calendar'))

    except Exception as e:
        print(f"Error in add_appointment function: {e}")
        return str(e), 500


@app.route('/calendar', methods=['GET'])
def your_calendar_view_function():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM dog_grooming ORDER BY scheduled_date ASC")
        raw_appointments = cursor.fetchall()
        appointments = [dict(zip([column[0] for column in cursor.description], row)) for row in raw_appointments]
        return render_template('calendar.html', dog_grooming=json.dumps(appointments))
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error while fetching appointments."

@app.route('/view/<int:entry_id>', methods=['GET', 'POST'])
def view(entry_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch the specific entry from the dog_boarding table
    cursor.execute("SELECT * FROM dog_boarding WHERE id=?", (entry_id,))
    entry = cursor.fetchone()
    connection.close()

    return render_template('view.html', entry=entry)

@app.route('/edit_dog/<int:entry_id>', methods=['GET', 'POST'])
def edit_dog(dog_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    if request.method == 'POST':
        # Fetch the updated dog information from the form
        updated_dog_name = request.form['dog_name']
        updated_dog_breed = request.form['dog_breed']
        updated_owner_first_name = request.form['owner_first_name']
        updated_owner_last_name = request.form['owner_last_name']
        updated_phone_number = request.form['phone_number']
        updated_drop_off_date = request.form['drop_off_date']
        updated_pick_up_date = request.form['pick_up_date']
        updated_bath = 'bath' in request.form
        updated_meds = 'meds' in request.form
        updated_shop_food = 'shop_food' in request.form
        updated_spay_neutered = 'spay_neutered' in request.form
        updated_notes = request.form['notes']
        updated_med_info = request.form['med_info']
        updated_food_info = request.form['food_info']

        # Fetch the existing dog record based on the dog ID
        cursor.execute("SELECT * FROM dog_boarding WHERE id=?", dog_id)
        existing_record = cursor.fetchone()

        if updated_drop_off_date.strip() == '':
            updated_drop_off_date = existing_record[6]  # Use existing drop_off_date if not modified
        else:
            updated_drop_off_date = datetime.strptime(updated_drop_off_date, '%Y-%m-%d')

            # Determine if the pick-up date should be updated
        if updated_pick_up_date.strip() == '':
            updated_pick_up_date = existing_record[7]  # Use existing pick_up_date if not modified
        else:
            updated_pick_up_date = datetime.strptime(updated_pick_up_date, '%Y-%m-%d')


        # Update the dog record in the database
        cursor.execute(
            "UPDATE dog_boarding SET dog_name=?, dog_breed=?, owner_first_name=?, owner_last_name=?, phone_number=?, "
            "drop_off_date=?, pick_up_date=?, bath=?, meds=?, shop_food=?, spay_neutered=?, notes=?, med_info=?, food_info =? WHERE id=?",
            (updated_dog_name, updated_dog_breed, updated_owner_first_name, updated_owner_last_name,
             updated_phone_number, updated_drop_off_date, updated_pick_up_date, updated_bath, updated_meds,
             updated_shop_food, updated_spay_neutered, updated_notes, updated_med_info, updated_food_info, dog_id))
        connection.commit()

        return redirect('/records')
    else:
        # Fetch the existing dog record based on the dog ID
        cursor.execute("SELECT * FROM dog_boarding WHERE id=?", (dog_id,))
        record = cursor.fetchone()

        # Convert drop_off_date and pick_up_date to strings
        drop_off_date_str = record[6].strftime('%Y-%m-%d') if record[6] else None
        pick_up_date_str = record[7].strftime('%Y-%m-%d') if record[7] else None

        # Format the drop_off_date and pick_up_date with the proper suffix
        formatted_drop_off_date = format_date_with_suffix(drop_off_date_str)
        formatted_pick_up_date = format_date_with_suffix(pick_up_date_str)

        # Pass the formatted drop_off_date and formatted_pick_up_date to the template
        return render_template('edit.html', record=record, formatted_drop_off_date=formatted_drop_off_date, formatted_pick_up_date=formatted_pick_up_date)

@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    connection = get_db_connection()
    cursor = connection.cursor()
    if request.method == 'POST':
        # Fetch the dog information from the form
        dog_name = request.form['dog_name']
        dog_breed = request.form['dog_breed']
        owner_first_name = request.form['owner_first_name']
        owner_last_name = request.form['owner_last_name']
        phone_number = request.form['phone_number']
        pick_up_date = request.form['pick_up_date']
        bath = request.form.get('bath') == 'on'
        meds = request.form.get('meds') == 'on'
        shop_food = request.form.get('shop_food') == 'on'
        spay_neutered = request.form.get('spay_neutered') == 'on'
        notes = request.form['notes']
        med_info = request.form['med_info']
        food_info = request.form['food_info']

        # Convert the drop-off date to a datetime object
        drop_off_date = datetime.now()

        # Insert the dog boarding record into the database
        cursor.execute(
            "INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath, meds, shop_food, spay_neutered, notes, med_info, food_info) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath,
             meds, shop_food, spay_neutered, notes, med_info, food_info))
        connection.commit()

        # Redirect to the records page
        return redirect('/records')

    return render_template('add_entry.html')

@app.route('/delete_dog/<int:entry_id>', methods=['POST'])
def delete_dog(dog_id):
    def delete_dog(entry_id):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM dog_boarding WHERE id=?", (entry_id,))
        connection.commit()
        connection.close()
    return redirect('/records')

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B %dth, %Y'):
    if value:
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        formatted_date = date_obj.strftime(format)
        return Markup(formatted_date)
    return ''

@app.errorhandler(404)
def page_not_found(e):
    return "404 - Page Not Found", 404

def format_phone_number(phone_number):
    if phone_number:
        formatted_phone_number = f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
        return formatted_phone_number
    return ''

def format_date_with_suffix(date_str):
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day = date.day
        suffix = 'th' if day in (11, 12, 13) else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return date.strftime(f'%B {day}{suffix}, %Y')
    return None  # Return None for empty date_str

def remove_suffix(date_string):
    suffixes = {'st', 'nd', 'rd', 'th'}
    return re.sub(r'\b(\d+)(st|nd|rd|th)\b', r'\1', date_string)

if __name__ == '__main__':
    app.run(debug=True)

