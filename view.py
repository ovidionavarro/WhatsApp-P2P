from flask import Flask, render_template, request, redirect, url_for
import sys, os
import logging
import socket
from chord_node import *


def init_app(node: 'ChordNode'):
    app = Flask(__name__)
    logging.basicConfig(level=logging.DEBUG)

    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            # Obtiene los datos del formulario
            name = request.form.get('name')
            number = request.form.get('number')
            # Puedes procesar los datos aquí o pasarlos a otra función
            resp = node.sing_in(getShaRepr(f"{name}_{number}"), name, number)
            logging.info(f'desde la pagina de inicio data= {resp} {type(resp)}')
            if resp == "True":
                return redirect(url_for('contacts', name=name, number=number))
            else:
                return redirect(url_for('singup'))

        return render_template('index.html')

    @app.route('/singup', methods=['GET', 'POST'])
    def singup():
        if request.method == 'POST':
            logging.debug('singup!!!!!!')
            # Obtiene los datos del formulario
            name = request.form.get('name')
            number = request.form.get('number')
            resp = node.sing_up(getShaRepr(f"{name}_{number}"), name, number)
            ###crear una pag de error en caso de resp=false
            return redirect(url_for('contacts', name=name, number=number))
        return render_template("singup.html")

    @app.route('/contacts')
    def contacts():
        name = request.args.get("name")
        numb = request.args.get("number")

        id = getShaRepr(f"{name}_{numb}")
        data = node.get_contacts(id, name, numb,'contacts')
        logging.info(f'esta es la dataaaaaaaaaaaaa{data}')
        return render_template('contacts.html')

    return app


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    node = ChordNode(ip, 8001, m)

    app = init_app(node)
    app.run(debug=False, host=ip, port=5001)
    while True:
        pass
