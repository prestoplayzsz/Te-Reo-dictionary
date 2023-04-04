from flask import Flask, render_template, app


@app.route('/')
def render_homepage():
    return render_template('home.html')