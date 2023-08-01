from flask import Flask, render_template, request, redirect, Markup
from datetime import datetime
import re
import pyodbc

app = Flask(__name__)

# Database connection details      
server = 'debbiesdoggroomingsalon.database.windows.net'
database = 'debbiesrecords'
username = 'aidanxcannon'
password = 'Unbroken556%'
driver = '{ODBC Driver 18 for SQL Server}'

# Establish a connection to the database
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
connection = pyodbc.connect(connection_string)
cursor = connection.cursor()

cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'dog_boarding'")
table_exists = cursor.fetchone() is not None

# If the dog_boarding table doesn't exist, create it
if not table_exists:
    cursor.execute("CREATE TABLE dog_boarding (id INT IDENTITY(1,1) PRIMARY KEY, dog_name NVARCHAR(255),"
                   " dog_breed NVARCHAR(255), owner_first_name NVARCHAR(255), owner_last_name NVARCHAR(255), "
                   "phone_number NVARCHAR(20), drop_off_date DATETIME, pick_up_date DATETIME, bath BIT, meds BIT, "
                   "shop_food BIT, spay_neutered BIT, notes NVARCHAR(MAX), med_info NVARCHAR(MAX), food_info NVARCHAR(MAX))")
    connection.commit()

cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'dog_grooming'")
table_exists = cursor.fetchone() is not None

# If the dog_grooming table doesn't exist, create it
if not table_exists:
    cursor.execute("CREATE TABLE dog_grooming (id INT IDENTITY(1,1) PRIMARY KEY, dog_name NVARCHAR(255),"
                   " dog_breed NVARCHAR(255), owner_first_name NVARCHAR(255), owner_last_name NVARCHAR(255), "
                   "phone_number NVARCHAR(20), scheduled_date DATETIME, notes NVARCHAR(MAX), arrived BIT)")
    connection.commit()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

#Employee route
@app.route('/employee_page')
def employee_page():
    return render_template('employee_page.html')

@app.route('/set_appointment', methods=['GET','POST'])
def set_appointment():
    if request.method == 'POST':
        # Fetch the appointment information from the form
        dog_name = request.form['dog_name']
        dog_breed = request.form['dog_breed']
        owner_first_name = request.form['owner_first_name']
        owner_last_name = request.form['owner_last_name']
        phone_number = request.form['phone_number']
        scheduled_date = request.form['scheduled_date']
        notes = request.form['notes']

        # Convert the scheduled_date to a datetime object
        scheduled_datetime = datetime.strptime(scheduled_date, '%Y-%m-%d')

        # Insert the appointment data into the dog_grooming table
        cursor.execute(
            "INSERT INTO dog_grooming (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, scheduled_date, notes, arrived) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, scheduled_datetime, notes, 0))
        connection.commit()



        # Redirect to the calendar page
        return redirect('/calendar')

    return render_template('appointment_form.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

# Thank you route
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


# Checked in route
@app.route('/check_in')
def check_in():
    return render_template('check_in.html')

@app.route('/boarding', methods=['GET', 'POST'])
def boarding_signin():
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

        #get current date
        drop_off_date = datetime.now()

        # Insert the dog boarding record into the database
        cursor.execute(
            "INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath, meds, shop_food, spay_neutered, notes, med_info, food_info) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath,
             meds, shop_food, spay_neutered, notes, med_info, food_info))
        connection.commit()

        # Redirect to the thank you page
        return redirect('/thankyou')

    return render_template('boarding_signin.html')

@app.route('/grooming', methods=['GET', 'POST'])
def grooming_signin():
    if request.method == 'POST':
        # Fetch the dog information from the form
        dog_name = request.form['dog_name']
        owner_first_name = request.form['owner_first_name']
        owner_last_name = request.form['owner_last_name']

        # Fetch the available options from the database based on dog and owner names
        cursor.execute("SELECT * FROM dog_grooming WHERE dog_name=? AND owner_first_name=? AND owner_last_name=?", (dog_name, owner_first_name, owner_last_name))
        options = cursor.fetchall()

        if options:
            # If the entry is found, redirect to the grooming check-in page for that entry
            return redirect(f'/grooming/{options[0][0]}/checkin')
        else:
            # If no entry is found, display an error message and pass the form data back to the template
            error_message = "No dog found."
            return render_template('grooming_signin.html', error_message=error_message, dog_name=dog_name,
                                   owner_first_name=owner_first_name, owner_last_name=owner_last_name)

    # If it's a GET request, simply render the grooming_signin.html template
    return render_template('grooming_signin.html')

@app.route('/grooming/<int:entry_id>/checkin', methods=['GET', 'POST'])
def grooming_checkin(entry_id):
    # Fetch the specific entry from the database based on the entry_id
    cursor.execute("SELECT * FROM dog_grooming WHERE id=?", (entry_id,))
    entry = cursor.fetchone()

    if request.method == 'POST':
        # Process the check-in action here if needed

        arrived = request.form.get('arrived') == 'on'

        # Redirect back to the grooming sign-in page

        # Mark the entry as checked in into the database
        cursor.execute("UPDATE dog_grooming SET arrived=1 WHERE id=?", (entry_id,))
        connection.commit()  # Commit the changes to the database

        return redirect('/check_in')

    return render_template('grooming_checkin.html', entry=entry)


def format_datetime(value, format='%B %dth, %Y'):
    if value:
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        formatted_date = date_obj.strftime(format)
        return formatted_date
    return ''

app.jinja_env.filters['datetimeformat'] = format_datetime

@app.route('/records')
def records():
    # Fetch dog records from the dog_boarding table
    cursor.execute("SELECT id, dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, "
                   "pick_up_date, bath, meds, shop_food, spay_neutered, notes "
                   "FROM dog_boarding")
    records = cursor.fetchall()

    formatted_records = []
    for record in records:
        # Convert drop_off_date and pick_up_date to strings
        drop_off_date_str = record[6].strftime('%Y-%m-%d') if record[6] else None
        pick_up_date_str = record[7].strftime('%Y-%m-%d') if record[7] else None

        # Format the drop_off_date and pick_up_date with the proper suffix
        formatted_drop_off_date = format_date_with_suffix(drop_off_date_str)
        formatted_pick_up_date = format_date_with_suffix(pick_up_date_str)

        # Format the boolean fields
        bath = "Yes" if record[8] == 1 else "No"
        meds = "Yes" if record[9] == 1 else "No"
        shop_food = "Yes" if record[10] == 1 else "No"
        spay_neutered = "Yes" if record[11] == 1 else "No"

        # Create a new record with the formatted fields
        formatted_record = record[:6] + (formatted_drop_off_date, formatted_pick_up_date, bath, meds, shop_food, spay_neutered)
        formatted_records.append(formatted_record)

    # Sort the formatted records based on pick_up_date in ascending order
    sorted_records = sorted(formatted_records, key=lambda x: datetime.strptime(remove_suffix(x[7]), '%B %d, %Y') if isinstance(x[7], str) else datetime.max)

    return render_template('records.html', records=sorted_records)

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

@app.route('/add-entry', methods=['GET', 'POST'])
def add_entry():
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

    # View route for a specific dog's information
@app.route('/view/<int:dog_id>')
def view(dog_id):
    # Fetch complete information for the selected dog from the dog_boarding table
    cursor.execute("SELECT * FROM dog_boarding WHERE id = ?", (dog_id,))
    dog_info = cursor.fetchone()
    if dog_info:
        return render_template('view.html', dog_info=dog_info)
    else:
        return "Dog not found."

@app.route('/edit/<int:dog_id>', methods=['GET', 'POST'])
def edit_dog(dog_id):
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

# Delete dog route
@app.route('/delete/<dog_id>', methods=['POST'])
def delete_dog(dog_id):
    # Delete the dog record from the database
    cursor.execute("DELETE FROM dog_boarding WHERE id=?", (dog_id,))
    connection.commit()

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

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
