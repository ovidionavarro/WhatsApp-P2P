# post_request.py
import requests

# URL de la API
url = 'http://localhost:8000/polls/user/'

# Datos del usuario
data = {
    'username': 'testuser2',
    'password': 'testpassword',
    'direction': '1234 Test St'
}

# Hacer la petición POST
response = requests.post(url, data=data)

# Imprimir la respuesta
print(response.status_code)

if response.text:
    print(response.json())
else:
    print("Empty response")