import logging

from utils import getShaRepr
import os

direction = os.path.dirname(os.path.abspath(__file__))

def find_user(name):
    for user in os.listdir(os.path.join('DB')):
        if user==name:
            return True

    logging.info(f'ruta no encontrada{name}')
    return False

class DB:
    @classmethod
    def register(cls,name:str,number:str):
        user_folder = os.path.join('DB', f'{name}_{number}')
        if(os.path.exists(user_folder)):
            return 'user already exists'
        os.makedirs(f'{user_folder}')
        with open(os.path.join('DB', f'{name}_{number}','contacts.txt'),'w') as f:
            f.write('')
        
        return "True"
    
    @classmethod
    def sing_in(cls,name,number):
        user_folder = os.path.join('DB', f'{name}_{number}')
        if(os.path.exists(user_folder)):
            return 'True'
        else:
            return 'False'

    @classmethod
    def get_contacts(cls,name,number,endpoint):
        aux_dir=find_user(f'{name}_{number}')
        if (aux_dir):
            dir_temp=os.path.join('DB',f'{name}_{number}',f'{endpoint}.txt')
            with open(dir_temp,'r') as f:
                return f.read().strip()
        else:
            print(aux_dir,33333333333333333)

    @classmethod
    def add_contact(cls,my_name,my_number,name,number):
        aux_dir=find_user(f'{my_name}_{my_number}')
        if aux_dir:

            with open(os.path.join('DB',f'{my_name}_{my_number}', f'{name}_{number}.txt'),'w') as f:
                f.write('')
            with open(os.path.join('DB', f'{my_name}_{my_number}','contacts.txt'),'a') as f:
                f.write(f'\n{name}_{number}')
            return "True"
        return 'False'
