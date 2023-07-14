from flask import Flask, render_template, request, redirect, Markup
from datetime import datetime
from dateutil.parser import parse
import re
import pyodbc

app = Flask(__name__)

# Database connection details
server = 'debbiesdbserver.database.windows.net'
database = 'debbiesdb'
username = 'aidanxcannon'
password = 'Unbroken556%'
driver = '{SQL Server}'

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
                   "shop_food BIT, spay_neutered BIT, notes NVARCHAR(MAX))")
    connection.commit()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Thank you route
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


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

        # Convert the drop-off date to a datetime object
        drop_off_date = datetime.now()

        # Insert the dog boarding record into the database
        cursor.execute(
            "INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath, meds, shop_food, spay_neutered, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath,
             meds, shop_food, spay_neutered, notes))
        connection.commit()

        # Redirect to the thank you page
        return redirect('/thankyou')

    return render_template('boarding_signin.html')


def format_datetime(value, format='%B %dth, %Y'):
    if value:
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        formatted_date = date_obj.strftime(format)
        return formatted_date
    return ''


app.jinja_env.filters['datetimeformat'] = format_datetime

@app.route('/records')
def records():
    # Fetch dog_id, dog name, owner's name, and phone number from the dog_boarding table
    cursor.execute("SELECT id, dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, "
                   "pick_up_date, bath, meds, shop_food, spay_neutered FROM dog_boarding")
    records = cursor.fetchall()

    formatted_records = []
    for record in records:
        # Convert drop_off_date and pick_up_date to strings
        drop_off_date_str = record[6].strftime('%Y-%m-%d') if record[6] else None
        pick_up_date_str = record[7].strftime('%Y-%m-%d') if record[7] else None

        # Format the drop_off_date and pick_up_date with the proper suffix
        formatted_drop_off_date = format_datetime(drop_off_date_str)
        formatted_pick_up_date = format_datetime(pick_up_date_str)

        # Format the boolean fields
        bath = "Yes" if record[8] == 1 else "No"
        meds = "Yes" if record[9] == 1 else "No"
        shop_food = "Yes" if record[10] == 1 else "No"
        spay_neutered = "Yes" if record[11] == 1 else "No"

        # Create a new record with the formatted fields
        formatted_record = record[:6] + (formatted_drop_off_date, formatted_pick_up_date, bath, meds, shop_food, spay_neutered)
        formatted_records.append(formatted_record)

    return render_template('records.html', records=formatted_records)



def format_phone_number(phone_number):
    if phone_number:
        formatted_phone_number = f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
        return formatted_phone_number

    return ''


def format_date_with_suffix(date):
    if isinstance(date, str):
        date = parse(date).date()

    if date:
        day = date.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        formatted_date = date.strftime(f"%B {day}{suffix}, %Y")
        return formatted_date

    return ''




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

        # Convert the drop-off date to a datetime object
        drop_off_date = datetime.now()

        # Insert the dog boarding record into the database
        cursor.execute(
            "INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath, meds, shop_food, spay_neutered, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, drop_off_date, pick_up_date, bath,
             meds, shop_food, spay_neutered, notes))
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

        # Validate the phone number format
        if not re.match(r'^\d{10}$', updated_phone_number):
            return "Invalid phone number format. Please enter a 10-digit number."

        # Update the dog record in the database
        cursor.execute(
            "UPDATE dog_boarding SET dog_name=?, dog_breed=?, owner_first_name=?, owner_last_name=?, phone_number=?, "
            "drop_off_date=?, pick_up_date=?, bath=?, meds=?, shop_food=?, spay_neutered=? WHERE id=?",
            (updated_dog_name, updated_dog_breed, updated_owner_first_name, updated_owner_last_name,
             updated_phone_number, updated_drop_off_date, updated_pick_up_date, updated_bath, updated_meds,
             updated_shop_food, updated_spay_neutered, dog_id))
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




@app.route('/add', methods=['POST'])
def add_dog():
    if request.method == 'POST':
        # Fetch the form data
        dog_name = request.form['dog_name']
        dog_breed = request.form['dog_breed']
        owner_first_name = request.form['owner_first_name']
        owner_last_name = request.form['owner_last_name']
        phone_number = request.form['phone_number']
        pick_up_date = request.form['pick_up_date']
        bath = 'bath' in request.form
        meds = 'meds' in request.form
        shop_food = 'shop_food' in request.form
        spay_neutered = 'spay_neutered' in request.form

        # Insert the dog record into the database
        cursor.execute("INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, pick_up_date, bath, meds, shop_food, spay_neutered) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, pick_up_date, bath, meds, shop_food, spay_neutered))
        connection.commit()

        return redirect('/records')




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
