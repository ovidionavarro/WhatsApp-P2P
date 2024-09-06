from utils import getShaRepr
import os

direction = os.path.dirname(os.path.abspath(__file__))


class DB:
    @classmethod
    def register(cls,name:str,number:str):
        user_folder = os.path.join('DB', f'{name}_{number}')
        if(os.path.exists(user_folder)):
            return 'user already exists'
        os.makedirs(f'{user_folder}\\contacts.txt')
        
        
        return "True"