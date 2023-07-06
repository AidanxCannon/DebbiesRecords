from flask import Flask, render_template, request, redirect
import pyodbc

app = Flask(__name__)

# Database connection details
server = 'debbiesrecords.database.windows.net'
database = 'debbiesrecords'
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
    cursor.execute("CREATE TABLE dog_boarding (id INT IDENTITY(1,1) PRIMARY KEY, dog_name NVARCHAR(255), dog_breed NVARCHAR(255), owner_first_name NVARCHAR(255), owner_last_name NVARCHAR(255), phone_number NVARCHAR(20), pick_up_date DATE, bath BIT, meds BIT, shop_food BIT, spay_neutered BIT)")
    connection.commit()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Thank you route
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# Boarding Sign-in route
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

        # Insert the dog boarding record into the database
        cursor.execute("INSERT INTO dog_boarding (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, pick_up_date, bath, meds, shop_food, spay_neutered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (dog_name, dog_breed, owner_first_name, owner_last_name, phone_number, pick_up_date, bath, meds, shop_food, spay_neutered))
        connection.commit()

        # Redirect to the thank you page
        return redirect('/thankyou')

    return render_template('boarding_signin.html')

# View records route
@app.route('/records')
def records():
    # Fetch dog_id, dog name, owner's name, and phone number from the dog_boarding table
    cursor.execute("SELECT id, dog_name, owner_first_name, owner_last_name, phone_number FROM dog_boarding")
    records = cursor.fetchall()
    return render_template('records.html', records=records)


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

# Edit dog route
@app.route('/edit/<int:dog_id>', methods=['GET', 'POST'])
def edit_dog(dog_id):
    if request.method == 'POST':
        # Fetch the updated dog name from the form
        updated_dog_name = request.form['dog_name']

        # Update the dog record in the database
        cursor.execute("UPDATE dog_boarding SET dog_name=? WHERE id=?", (updated_dog_name, dog_id))
        connection.commit()

        return redirect('/records')
    else:
        # Fetch the existing dog record based on the dog ID
        cursor.execute("SELECT * FROM dog_boarding WHERE id=?", (dog_id,))
        record = cursor.fetchone()

        return render_template('edit.html', record=record)

# Add dog route
@app.route('/add', methods=['GET', 'POST'])
def add_dog():
    if request.method == 'POST':
        # Fetch the dog name from the form
        dog_name = request.form['dog_name']

        # Insert the dog record into the database
        cursor.execute("INSERT INTO dog_boarding (dog_name) VALUES (?)", (dog_name,))
        connection.commit()

        return redirect('/records')
    else:
        return render_template('add_dog.html')

# Delete dog route
@app.route('/delete/<dog_id>', methods=['POST'])
def delete_dog(dog_id):
    # Delete the dog record from the database
    cursor.execute("DELETE FROM dog_boarding WHERE id=?", (dog_id,))
    connection.commit()

    return redirect('/records')

@app.errorhandler(404)
def page_not_found(e):
    return "404 - Page Not Found", 404

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)