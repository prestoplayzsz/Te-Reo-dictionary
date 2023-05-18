from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "uwrkfnafklgel"

DATABASE = "C:/Users/Preston Wong/OneDrive - Wellington College/13DTS/Te-Reo-dictionary/dictionary.db"


def open_database(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None

def is_logged_in():
    if session.get('email') is None:
        print('not logged in')
        return False
    else:
        print('logged in')
        return True

@app.route('/')
def render_homepage():
    return render_template('home.html', logged_in=is_logged_in())

@app.route('/dictionary/<cat_id>')
def render_menu_page(cat_id):
    con = open_database(DATABASE)
    query = "SELECT * FROM category"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()

    query = "SELECT * FROM dictionary WHERE cat_id=?"
    cur = con.cursor()
    cur.execute(query, (cat_id, ))
    dictionary_list = cur.fetchall()
    con.close()
    print(dictionary_list)
    print(category_list)
    return render_template('dictionary.html', dictionary=dictionary_list, categories=category_list)

@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    if is_logged_in():
        return redirect('/menu/1')
    print("logging in")
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        print(email)
        query = """SELECT id, fname, password FROM user WHERE email =?"""
        con = open_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchone()
        con.close()
        print(user_data )
        # if the given is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty result set
        try:
            user_id = user_data[0]
            first_name = user_data[1]
            db_password = user_data[2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check if the password is incorrect for that email

        if not bcrypt.check_password_hash(db_password, password):
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['user_id'] = user_id
        session['firstname'] = first_name

        print(session)
        return redirect('/')
    return render_template('login.html', logged_in=is_logged_in())

@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message+See+you+next+time!')

@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page():
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect("\signup?error=Passwords+do+not+match")

        if len(password) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+characters")


        hashed_password = bcrypt.generate_password_hash(password)
        con = open_database(DATABASE)
        query = "INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)"
        cur =con.cursor()

        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('/signup?error=Email+is+already+used')

        con.commit()
        con.close()

        return redirect("\login")

    return render_template('signup.html', logged_in=is_logged_in())

@app.route('/admin')
def render_admin():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    con = open_database(DATABASE)
    query = "SELECT * FROM category"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    print(category_list)
    query = "SELECT id, maori FROM dictionary"
    cur = con.cursor()
    cur.execute(query)
    english_list = cur.fetchall()
    print(english_list)
    con.close()
    return render_template("admin.html", logged_in=is_logged_in(), categories=category_list, words=english_list)

@app.route('/add_category', methods=['POST'])
def add_category():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == 'POST':
        print(request.form)
        cat_name = request.form.get('name').lower().strip()
        print(cat_name)
        con = open_database(DATABASE)
        query = "INSERT INTO category ('name') VALUES (?)"
        cur = con.cursor()
        cur.execute(query, (cat_name, ))
        con.commit()
        con.close()
        return redirect('/admin')

@app.route('/delete_category', methods=['POST'])
def render_delete_category():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        category = request.form.get('cat_id')
        print(category)
        category = category.split(", ")
        cat_id = category[0]
        cat_name = category[1]
        return render_template("delete_confirm.html", id=cat_id, name=cat_name, type="category")
    return redirect("/admin")

@app.route('/delete_category_confirm/<cat_id>')
def render_delete_category_confirm(cat_id):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    con = open_database(DATABASE)
    query = "DELETE FROM category WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (cat_id, ))
    con.commit()
    con.close()
    return redirect("/admin")

@app.route('/add_word', methods=['POST'])
def add_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == 'POST':
        maori_word = request.form.get('maori')
        print(maori_word)
        english_word = request.form.get('english')
        print(english_word)
        category = request.form.get('category')
        print(category)
        definition_word = request.form.get('definition')
        print(definition_word)
        return render_template("add_confirm.html", name=maori_word, name1=english_word, name2=category, name3=definition_word, type="word")
    return redirect("/admin")


@app.route('/add_word_confirm/<maori>, <english>, <category>, <definition>')
def render_add_word_confirm(maori, english, category, definition):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    con = open_database(DATABASE)
    print(maori, english, category, definition)
    query = "INSERT INTO dictionary ('maori', 'english', 'category', 'definition') VALUES (?, ?, ?, ?)"
    cur = con.cursor()
    print(maori, english, category, definition)
    cur.execute(query, (maori, english, category, definition, ))
    con.commit()
    con.close()
    return redirect("/admin")

@app.route('/delete_word', methods=['POST'])
def render_delete_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        word = request.form.get('maori')
        print(word)
        word = word.split(", ")
        word_id = word[0]
        word_name = word[1]
        return render_template("delete_confirm.html", id=word_id, name=word_name, type="word")
    return redirect("/admin")

@app.route('/delete_word_confirm/<maori>')
def render_delete_word_confirm(maori):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    con = open_database(DATABASE)
    query = "DELETE FROM dictionary WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (maori, ))
    con.commit()
    con.close()
    return redirect("/admin")

app.run(host='0.0.0.0', debug=True)
