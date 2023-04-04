from flask import Flask, render_template, app
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = "C:/Users/Preston Wong/OneDrive - Wellington College/13DTS/Te-Reo-dictionary/dictionary.db"

def open_database(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None

@app.route('/')
def render_homepage():
    return render_template('home.html')

@app.route('/dictionary')
def render_menu_page():
    con = open_database(DATABASE)
    query = "SELECT id, maori, english, category, definition, level FROM dictionary"
    cur = con.cursor()
    cur.execute(query)
    dictionary_list = cur.fetchall()
    con.close()
    print(dictionary_list)
    return render_template('dictionary.html', dictionary=dictionary_list)

