import os
from utils import getShaRepr,rem_dir,create_folder

current_directory = os.getcwd()
class HandleData():
    def __init__(self, id:int):
        self._id = id
        self.collector=[]
    
    
    def _inbetween(self, k: int, start: int, end: int) -> bool:
        if start < end:
            return start < k <= end
        else:  # The interval wraps around 0
            return start < k or k <= end

    def data(self,delete:bool,id=None):
        ret=''
        for user in os.listdir(os.path.join('DB')):
            # print (getShaRepr(f"{user}"))
            if id==None or id>getShaRepr(f"{user}"):
                ret+=f'{user}'
                for file in os.listdir(os.path.join('DB',user)):
                  with open(os.path.join('DB',user,file),'r') as f:
                    ret+=f'/{file}/{f.read()}'

                ret+='|'
                self.collector.append(os.path.join(current_directory,'DB',user))
        self._clean(delete)
        return ret
    
    def create(self,data:str):
        users=data.split('|')
        for user in users:
            if user !='' or '/' in users:
                parse=user.split('/')
                create_folder(os.path.join('DB',parse[0]))
                chats=parse[1:]
                for i in range(0,len(chats),2):
                    if i%2!=0:
                        continue
                    with open(os.path.join('DB',parse[0],f'{chats[i]}'),'w') as f:
                        f.write(chats[i+1])

    def _clean(self,delete:bool):
        if delete:
            for i in self.collector:
                rem_dir(i)
        self.collector=[]


# print(a.data(False,112))
# create_folder('D:\\Escuela\\4to2\\SD\\WhatsApp-P2P\\DB\\Pedro_1234563')
# 'Juan_123456/contacts.txt/Tal_123456/Tal_123456.txt/[you]:asdasdsdasd[Tal]:qwdwd|Tal_123456/contacts.txt/Juan_123456/Juan_123456.txt/[Juan]:asdasdsdasd[you]:qwdwd|'
