from flask import Flask, render_template, request, redirect, url_for
import sys, os
import logging
import socket
from chord_node import *


def init_app(node:'ChordNode'):
    
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
            resp=node.sing_up(getShaRepr(f"{name}_{number}"),f"{name}_{number}")
            # user_folder = os.path.join('DB', f'{name}_{number}')
            # os.makedirs(user_folder, exist_ok=True)
            return redirect(url_for('contacts', name=name, number=number))
        return render_template("singup.html")


    @app.route('/contacts')
    def contacts():
        return render_template('contacts.html')
    
    return app

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    node = ChordNode(ip, 8001, m)

    app=init_app(node)
    app.run(debug=False,host='0.0.0.0',port=5001)
    while True:
        pass

