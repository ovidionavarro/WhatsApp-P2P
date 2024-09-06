from flask import Flask, render_template, request, redirect, url_for
import sys, os
import logging
import socket

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Obtiene los datos del formulario
        name = request.form.get('name')
        number = request.form.get('number')

        # Puedes procesar los datos aquí o pasarlos a otra función
        return redirect(url_for('contacts', name=name, number=number))

    return render_template('index.html')


@app.route('/singup', methods=['GET', 'POST'])
def singup():
    if request.method == 'POST':
        logging.debug('singup!!!!!!')
        # Obtiene los datos del formulario
        name = request.form.get('name')
        number = request.form.get('number')
        user_folder = os.path.join('DB', f'{name}_{number}')
        os.makedirs(user_folder, exist_ok=True)
        return redirect(url_for('contacts', name=name, number=number))

    return render_template("singup.html")


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


