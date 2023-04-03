from flask import Flask, render_template, redirect, request, app


@app.route('/')
def render_homepage():
    return render_template('home.html')