import argparse
import time
import random
import simpy
from simpy.util import start_delayed
from collections import deque
import numpy.random as rnd

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--ascenseur", type=int, help="spécifie le nombre d'ascenseurs", default=1)
parser.add_argument("-c", "--capacité", type=int, help="Spécifie la capacité de l'ascenseur", default=1)
parser.add_argument("-v", "--vitesse", type=int, help="Spécifie la vitesse  de l'ascenseur ", default=10)
parser.add_argument("-o", "--ordonnancement", type=str, help="Spécifie l'ordonnancement utilisé par l'ascenseur", default="FCFS")
parser.add_argument("-i", "--idle", type=bool, help="définie si l'ascenseur utilise l'idle ou non", default=False)
parser.add_argument("-l", "--lamb", type=float, help="Spécifie la valeur du lambda", default=0.5)
parser.add_argument("-d", "--durée", type=int, help="Sécifie la durée de simulation", default=10000)

args = parser.parse_args()

ETAGES = [1,2,3,4,5,6,7]
VITESSE = args.vitesse
CAPACITE = args.capacité
ASCENSEURS = args.ascenseur
LAMBDA = args.lamb
DUREE = args.durée

ATTENTE = deque([])
EN_MARCHE = deque([])
RESTE = []

def print_by_id(list):
    result = []
    for item in list:
        result.append(item.id)
    return result

def print_by_expected(list):
    result = []
    for item in list:
        result.append(item.expected)
    return result

def getAllResult():
    
    for user in RESTE:
        print("L'individu ", user.id ," temps d'arriver:", user.arrival_time, "s" ," temps pour prendre l'ascenseur à l'arrivé", (user.waiting_time_up - user.arrival_time), "s", " temps pour prendre l'ascenseur afin de sortir:", (user.waiting_time_down - user.leaving_time_call), "s" ," quitte le batiment à :",  user.leaving_time, "s")


class Batiment:
    def __init__(self, env):
        self.floors = ETAGES
        self.action = env.process(self.run(env))
    def run(self, env):
        cpt = 0 #Le nombre d'utilisateur créer par la simulation
        print(env.now, " : Le pavillon est ouvert")
        for x in range(ASCENSEURS):
            Ascenseur(env, (x+1))   # Génère X ascenseur dans le batiment
        id = 1
        while True:
            yield env.timeout(int(rnd.poisson(lam=60/LAMBDA, size =1)))  # Processus d'arrivée de Poisson       
            if env.now < int(DUREE / (1.05)) : #Empeche de nouveau individus de monter pour pouvoir fermer le batiment
                new_user = Individu(env, id)
                ATTENTE.append(new_user)
                print(env.now, " : l'individu ", new_user.id, " attend au RDC")
                cpt += 1
            id += 1
            print("le nombre d'utilisateurs créer par la simulation est:",cpt)


class Individu:
    def __init__(self, env, id):
        self.id = id
        self.is_waiting = True
        self.is_working = False
        self.is_leaving = False
        self.working_time = random.choice(range(3000,4200)) # Un individu travail durant 60minutes en moyenne ce qui équivaut à 3600 secondes
        self.arrival_time = env.now
        self.waiting_time_up = 0 #Contient le temps d'attente pour monter dans l'ascenceur + temps perdu a attendre que les autres passagers s'arretent a leurs arrêts
        self.waiting_time_down = 0
        self.leaving_time_call = 0
        self.leaving_time = 0
        self.current = 1
        self.expected = random.randint(ETAGES[1], ETAGES[6])
        self.action = env.process(self.run(env))

    def run(self, env):
        while True:
            yield env.timeout(1)
            if(self.is_working == True):
                print(env.now, " : l'individu ", self.id, "commence son travail")
                yield env.timeout(self.working_time)
                print(env.now, " : l'individu ", self.id, " à fini son travail")
                self.is_working = False
                self.is_waiting = True
                self.is_leaving = True
                self.leaving_time_call = env.now
                ATTENTE.append(self) #Travail terminé l'utilisateur se rajoute dans la liste USER_WAITING
                EN_MARCHE.remove(self) #Travail terminé l'utilisateur se retire de la liste USER_WORKING
            if self.leaving_time != 0:
                self.leaving_time = env.now
                print(env.now, " : l'individu ", self.id, "quitte les lieux")
                break
 
class Ascenseur:
    def __init__(self,env, id):
        self.id = id
        self.speed = VITESSE
        self.capacity = CAPACITE
        self.action = env.process(self.run(env))
        self.e_current = 1
        self.shaft = deque([])
        
    def move(self, env, user):
 
        eta_out = abs((user.expected - self.e_current)*self.speed) #Temps pour que l'ascenceur depose l'individu au bon etage
        yield env.timeout(eta_out) #On bloque l'ascenceur tant qu'il n'a pas deposé l'individu   
        self.e_current = user.expected #definir le nouvel etage ou se trouve l'ascenceur       
        print(env.now, " :l'ascenseur ", self.id, " dépose l'individu  ", user.id, " à l'étage |", self.e_current, "| temps nécessaire ", eta_out , "s")
        self.shaft.remove(user) # L'utilisateur arrive a son etage on le retire de la liste          
        if user.is_leaving is True :
            user.leaving_time = env.now
            RESTE.append(user)
        else : 
            user.is_working = True
            user.current = self.e_current
            user.expected = 1
            EN_MARCHE.append(user) # On rajoute l'utilisateur a la liste USER_WORKING
        

    def idle(self, env):
        eta_out = abs((3 - self.e_current)*self.speed)
        print(env.now, " : ascenseur ",self.id, " IDLE à l'étage 3, à pris :", eta_out, "s")
        
        yield env.timeout(eta_out)
        self.e_current = 3
    
    def FCFS_gestionnaire_users(self, env):   
        while len(self.shaft) != 0 : 
            for user in list(self.shaft) :
                if user.is_leaving is False: #Si individu monte travailler on enregistre le temps d'attente pour pouvoir monter
                    user.waiting_time_up = env.now   
                               
                yield env.process(self.move(env, user))
        
    def FCFS(self, env):
        if(len(ATTENTE) != 0):  
            selected_user = ATTENTE.popleft() #On defile le premier individu en attente
            self.shaft.append(selected_user) #On enfile le premier individu dans notre cage d'ascenceur
            eta_in = abs((self.e_current - selected_user.current)*self.speed) #Temps pour que l'ascenceur rejoigne l'individu au bon etage
            print(env.now, " : l'individu", selected_user.id, "appel l'ascenseur ", self.id, " à l'étage |", selected_user.current, "| pour atteindre l'étage |", selected_user.expected, "|")
            yield env.timeout(eta_in) #On bloque l'ascenceur tant qu'il n'a pas atteint l'individu
            self.e_current = selected_user.current            
            print(env.now, " : l'ascenseur ", self.id, " prend l'individu", selected_user.id, "à l'étage |",self.e_current,"| l'operation est éffectuée en ", eta_in, "s")
            if selected_user.is_leaving is True:
                selected_user.waiting_time_down = env.now
            elif selected_user.is_leaving is False:
                selected_user.waiting_time_up = env.now            
            for user in list(ATTENTE):        
                if len(list(self.shaft)) < CAPACITE:
                    if user.current == selected_user.current:  
                        if user.is_leaving is True:
                            user.waiting_time_down = env.now
                        elif user.is_leaving is False:
                            user.waiting_time_up = env.now
                        self.shaft.append(user)
                        ATTENTE.remove(user)
            cage = print_by_id(self.shaft)
            print(env.now, " : L'ascenseur ", self.id, " à pris l'individu", cage)
            yield env.process(self.FCFS_gestionnaire_users(env))  
        elif (len(ATTENTE) == 0 and args.idle is True and self.e_current != 3):
            yield env.process(self.idle(env))
        
            
    def SSTF(self, env):
        tmp = 100
        if(len(ATTENTE) != 0):
            for user in list(ATTENTE):
                if user.is_waiting == True:
                    if(abs(self.e_current - user.current) < tmp):
                        tmp = abs(self.e_current - user.current)
                        selected_user = user
            
            ATTENTE.remove(selected_user) #On defile le premier individu en attente
            self.shaft.append(selected_user) #On enfile le premier individu dans notre cage d'ascenceur
            eta_in = abs((self.e_current - selected_user.current)*self.speed) #Temps pour que l'ascenceur rejoigne l'individu au bon etage
            print(env.now, " : l'individu ", selected_user.id, " appel l'ascenseur ", self.id, " à l'étage |", selected_user.current, "| pour atteindre l'étage |", selected_user.expected, "|")
            yield env.timeout(eta_in)
            self.e_current = selected_user.current            
            print(env.now, " : L'ascenseur ", self.id, " prend l'individu ", selected_user.id, "à l'étage |",self.e_current," | l'operation est éffectuée en:  ", eta_in, "s")
            for user in list(ATTENTE):
                if len(list(self.shaft)) < CAPACITE:
                    if user.current == selected_user.current:
                        self.shaft.append(user)
                        ATTENTE.remove(user)
            yield env.process(self.SSTF_gestionnaire_users(env))
        
        elif (len(ATTENTE) == 0 and args.idle is True and self.e_current != 3):
            yield env.process(self.idle(env))

    def SSTF_gestionnaire_users(self, env):
        for _ in range(len(self.shaft)) :      
            tmp = 100              
            for user in list(self.shaft): 
                if(abs(self.e_current - user.expected) < tmp):
                    tmp = abs(self.e_current - user.expected)
                    chosen_user = user
        
            if chosen_user.is_leaving is True:
                chosen_user.waiting_time_down = env.now
            elif chosen_user.is_leaving is False:
                chosen_user.waiting_time_up = env.now   
                
            print("utilisateur choisit: ", chosen_user.id)
            yield env.process(self.move(env, chosen_user))
        
    def run(self, env):
        print(env.now ," : l'ascenseur ",self.id," est en marche")
        while True :
            yield env.timeout(1)
            if(args.ordonnancement == "FCFS"):  
                yield env.process(self.FCFS(env))
            elif(args.ordonnancement == "SSTF"):
                yield env.process(self.SSTF(env))
                
              
env = simpy.Environment()
pavillon = Batiment(env)
env.run(until=DUREE)

getAllResult() 