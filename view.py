from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Obtiene los datos del formulario
        name = request.form.get('name')
        number = request.form.get('number')

        # Puedes procesar los datos aquí o pasarlos a otra función
        return redirect(url_for('contacts', name=name, number=number))

    return render_template('index.html')


@app.route('/singup',methods=['GET', 'POST'])
def about():
    return render_template("singup.html")


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    app.run(debug=True)
