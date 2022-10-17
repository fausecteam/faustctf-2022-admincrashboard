#!/usr/bin/env python3

import os
from pwd import getpwuid, getpwnam
from venv import create
from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import pam
from getpass import getpass
from flask_session import Session
from lxml import etree
import subprocess
import uuid

'''
    ToDo fix all vulnerabilities

    some while ago, our service got hacked. our security researchers
    found 4 (intended) vulnerabilities. Unfortunately Marty took the
    report back to the past to fix the vulnerabilities before we get
    hacked. Appearently this didn't affect our timeline. So we have
    to redo all the work and find and fix everything again.

    good luck!
'''

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = str(uuid.uuid4())
#app.config['SESSION_PERMANENT'] = False
#app.config['SESSION_USE_SIGNER'] = True

server_session = Session(app)

def user_valid(username, password):
    p = pam.pam()
    return p.authenticate(username, password, service='sshd')

def logged_in():
    return session.get('username', False)

def parse(file):
    tree = etree.parse(file)
    root = tree.getroot()
    name = root.findtext("name")
    script = root.findtext("script")
    return (name, script)

def getAllButtons():
    buttons = []
    for dirpath, dirs, files in os.walk(f"/home/{session.get('username')}"):
        for file in files:
            if file.endswith('.button'):
                try:
                    file = f"{dirpath}/{file}"
                    name, script = parse(file)
                    buttons.append({"name":name,"script":script})
                except (etree.XMLSyntaxError):
                    buttons.append({})
                buttons[-1]["file"] = file
    return buttons

def run(cmd):
    secure_cmd = f"sudo -u {session.get('username')} {cmd}"
    print(secure_cmd)
    return subprocess.check_output(secure_cmd, shell=True)


def save(file, content):
    result = subprocess.run(['sudo', '-u', session.get('username') ,'sed', '-n', f"w {file}"], input=content, encoding='ascii')
    if result.returncode != 0:
        flash("Error Writing to File")


def create(file):
    app.logger.warning(file)
    result = subprocess.run(['sudo', '-u', session.get('username'), 'cp', '/etc/skel/welcome.button', file])
    if result.returncode != 0:
        flash("Error creating file")

def existsUser(user):
    try:
        getpwnam(user)
        return True
    except:
        return False

def createUser(username, password):
    result = subprocess.run(['sudo', 'addnewuser', username, password])
    if result.returncode != 0:
        flash("Error creating user!")
        return redirect(url_for('register'))
    
    return redirect(url_for('login'))


@app.route("/")
def index():
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.pop('username', default=None)
    return redirect(url_for('login'))


@app.route("/login", methods=['GET','POST'])
def login():

    if logged_in():
        return redirect(url_for('crashboard'))
        
    if request.method == 'GET':
        return render_template("login.html")

    if request.method == 'POST':
        username = request.form.get("username", False)
        password = request.form.get("password", False)

        if user_valid(username, password):
            session['username'] = username
            return redirect(url_for('crashboard'))

        else:
            flash("Login failed")
            return redirect(url_for('login'))


@app.route("/crashboard", methods=['GET'])
def crashboard():
    if not logged_in():
        return redirect(url_for('login'))

    buttons = getAllButtons()

    return render_template("crashboard.html",buttons=buttons)

@app.route("/execute")
def execute():

    if not logged_in():
        return redirect(url_for('login'))

    file = request.args.get("button")
    _,cmd = parse(file)
    return run(cmd)

@app.route("/edit", methods=['GET','POST'])
def edit():

    if not logged_in():
        return redirect(url_for('login'))


    if request.method == 'GET':
        file = request.args.get("button")
        with open(file) as f:
            content = f.read()
        
        return render_template("edit.html", file=file, content=content)

    if request.method == 'POST':
        file = request.args.get("button")
        content = request.form.get("content", False)

        save(file, content)

        return redirect(url_for('crashboard'))

@app.route("/register", methods=['GET', 'POST'])
def register():

    if logged_in():
        return redirect(url_for('crashboard'))

    if request.method == 'GET':
        return render_template("register.html")

    if request.method == 'POST':
        username = request.form.get("username", False)
        password = request.form.get("password", False)

        if not existsUser(username):
            return createUser(username, password)
        else:
            flash("User already exists")
            return redirect(url_for('register'))

@app.route('/add', methods=['POST'])
def add():

    if not logged_in():
        return redirect(url_for('login'))
    
    filename = request.form.get("filename", False)
    
    if not filename:
        flash("Please provide a valid filename")
        return redirect(url_for('crashboard'))

    path = os.path.join(f"/home/{session.get('username')}", filename)

    create(path)
    
    return redirect(url_for('crashboard'))


    

@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(host="::")
