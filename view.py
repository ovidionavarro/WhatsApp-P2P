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
        contacts_list = node.get_contacts(id, name, numb, 'contacts').split('\n')

        # Procesa la lista de contactos para dividir el nombre y número
        processed_contacts = []
        for contact in contacts_list:
            if contact:  # Evita entradas vacías
                contact_parts = contact.split('_')
                if len(contact_parts) == 2:
                    processed_contacts.append({
                        'name': contact_parts[0],
                        'number': contact_parts[1]
                    })

        context = {
            'contacts': processed_contacts,
            'id': id,
            'name': name,
            'number': numb
        }
        logging.info(f'Contactos de {name}-{numb}: {processed_contacts}')
        return render_template('contacts.html', **context)

    @app.route('/add_contacts', methods=['GET', 'POST'])
    def add_contacts():
        my_name = request.args.get("name")
        my_number = request.args.get("number")
        my_id = request.args.get("id")
        if request.method == 'POST':

            logging.info('Adding Contact!!!!!!')
            # Obtiene los datos del formulario
            name = request.form.get('name')
            number = request.form.get('number')
            resp = node.sing_in(getShaRepr(f"{name}_{number}"), name, number)
            if resp != 'True':
                logging.info(f'WARNING!!!!!!!! user {name}_{number} DONT exist,')
            ###crear una pag de error en caso de resp=false
            created=node.add_contact(my_id,my_name,my_number,name,number)
            logging.info('Usuario creado')
            return redirect(url_for('contacts', name=my_name, number=my_number))

        return render_template("add_contacts.html")

    @app.route('/send_message/<contact_name>/<contact_number>', methods=['GET', 'POST'])
    def send_message(contact_name, contact_number):
        if request.method == 'POST':
            # Obtén el mensaje del formulario
            message = request.form.get('message')

            # Aquí puedes implementar la lógica para enviar el mensaje
            # Por ejemplo, puedes usar la red Chord para enviar el mensaje al contacto
            logging.info(f"Sending message to {contact_name} ({contact_number}): {message}")

            # Retorna a la página de contactos después de enviar el mensaje
            return redirect(url_for('contacts', name=request.args.get('name'), number=request.args.get('number')))

        return render_template('send_message.html', contact_name=contact_name, contact_number=contact_number)

    return app


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    node = ChordNode(ip, 8001, m)

    app = init_app(node)
    app.run(debug=False, host=ip, port=5001)
    while True:
        pass
