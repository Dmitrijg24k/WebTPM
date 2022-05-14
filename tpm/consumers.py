import json
from re import S
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import numpy as np
import math
import random
from random import randrange
import time
from .models import Sessions

class Machine:
    def __init__(self, k=3, n=4, l=6):
        self.k = k
        self.n = n
        self.l = l
        self.W = np.random.randint(-l, l + 1, [k, n])

    def get_output(self, X):
        '''
        Returns a binary digit tau for a given random vecor.
        Arguments:
        X - Input random vector
        '''
        k = self.k
        n = self.n
        W = self.W
        X = X.reshape([k, n])
        sigma = np.sign(np.sum(X * W, axis=1)) # Compute inner activation sigma Dimension:[K]
        tau = np.prod(sigma) # The final output
        self.X = X
        self.sigma = sigma
        self.tau = tau
        return tau
    def __call__(self, X):
        return self.get_output(X)
    def update(self, tau2, update_rule='hebbian'):
        '''
        Updates the weights according to the specified update rule.
        Arguments:
        tau2 - Output bit from the other machine;
        update_rule - The update rule. 
        Should be one of ['hebbian', 'anti_hebbian', random_walk']
        '''
        X = self.X
        tau1 = self.tau
        sigma = self.sigma
        W = self.W
        l = self.l
        if (tau1 == tau2):
            if update_rule == 'hebbian':
                self.hebbian(W, X, sigma, tau1, tau2, l)
                # for (i, j), _ in np.ndenumerate(self.W):
                #     self.W[i, j] += self.X[i, j] * self.tau * self.theta(self.sigma[i], self.tau) * self.theta(self.tau, tau2)
                #     self.W[i, j] = np.clip(self.W[i, j] , -1 * (self.l), self.l)
            elif update_rule == 'anti_hebbian':
                self.anti_hebbian(W, X, sigma, tau1, tau2, l)
            elif update_rule == 'random_walk':
                self.random_walk(W, X, sigma, tau1, tau2, l)
            else:
                raise Exception("Invalid update rule. Valid update rules are: " + 
                    "\'hebbian\', \'anti_hebbian\' and \'random_walk\'.")
    def theta(self,t1, t2):
        return 1 if t1 == t2 else 0
    def hebbian(self, W, X, sigma, tau1, tau2, l):
        k, n = W.shape
        for (i, j), _ in np.ndenumerate(W):
            W[i, j] += X[i, j] * tau1 * self.theta(sigma[i], tau1) * self.theta(tau1, tau2)
            W[i, j] = np.clip(W[i, j] , -l, l)
        self.W = W
    def anti_hebbian(self, W, X, sigma, tau1, tau2, l):
        k, n = W.shape
        for (i, j), _ in np.ndenumerate(W):
            W[i, j] -= X[i, j] * tau1 * self.theta(sigma[i], tau1) * self.theta(tau1, tau2)
            W[i, j] = np.clip(W[i, j], -l, l)
        self.W = W
    def random_walk(self, W, X, sigma, tau1, tau2, l):
        k, n = W.shape
        for (i, j), _ in np.ndenumerate(W):
            W[i, j] += X[i, j] * self.theta(sigma[i], tau1) * self.theta(tau1, tau2)
            W[i, j] = np.clip(W[i, j] , -l, l)
        self.W = W
    def chaosmap(self):
        r = sum(list(np.hstack(self.W)))
        rr = sum([abs(x) for x in (list(np.hstack(self.W)))])
        t = float(abs(r)) / float(rr)
        x = t
        for i in range(rr):
            x = (3.6 + t/2)* x *(1 - x)
        return x

def gen_rand_vector(sid, l, k, n): #сид, диапазон, количество нейронов, количество входов
    np.random.seed(sid)
    #print('sid, vector', sid, np.random.randint(-l, l + 1, [k, n]))
    return np.random.randint(-l, l + 1, [k, n])
def gen_sid():
    return random.randint(0, 1000)

class TpmConsumer(WebsocketConsumer):
    # let ServerTPM = 
    def connect(self):
        self.accept()
        print(dir(self.scope["user"]))
        # self.send(text_data=json.dumps({
        #     'type': 'ServerReadySync',
        #     'message': 'Client connected'
        # }))
        print("client wants to connect")
        # self.room_group_name = 'text'

        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_group_name,
        #     self.channel_name
        # )
        # self.accept()
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        #print("connect0", message)
        # time.sleep(0.4)
        if text_data_json['type'] == 'ClientReadySync':
            # print(text_data_json)
            currentSession = self.scope["user"].sessionId
            if (currentSession):
                currentSession.delete()
            # message = text_data_json['message']
            # self.ServerTPM = TPMClient(text_data_json['k'],text_data_json['n'], text_data_json['l'])
            self.send(text_data=json.dumps({
                'type': 'ServerReadySync',
                'message': 'Server is ready'
            }))
        if text_data_json['type'] == 'GetParametrs':
            # print(text_data_json)
            # message = text_data_json['message']
            self.timer = 0
            self.k = text_data_json['k']
            self.n = text_data_json['n']
            self.l = text_data_json['l']
            self.ServerTPM = Machine(text_data_json['k'],text_data_json['n'], text_data_json['l'])
            self.sid = gen_sid()
            # vector = []
            self.ServerTPM.X = gen_rand_vector(self.sid, self.l, self.k, self.n)
            # for i in range(len(X)):
            #     vector.append([])
            #     for j in range(len(X[i])):
            #         vector[i].append(X[i][j])
            self.send(text_data=json.dumps({
                'type': 'GetFirstSid',
                'sid': self.sid,
                'vector': self.ServerTPM.X.tolist()
            }))
        if text_data_json['type'] == 'GetResultClient':
            #print(self.ServerTPM.k, self.ServerTPM.n, self.ServerTPM.l)
            #print("sid:{}".format(self.sid))
            # self.X = gen_rand_vector(self.sid, self.l, self.k, self.n)
            #print("Vector:{}".format(self.X))
            self.resultServer = self.ServerTPM.get_output(self.ServerTPM.X)
            self.ServerTPM.X = gen_rand_vector(self.sid, self.l, self.k, self.n)
            #print("resultServer:{}".format(self.resultServer))
            #print("resultClient:{}".format(text_data_json['resultClient']))
            #self.ServerTPM.update(self.resultClient, 'hebbian')
            # message = text_data_json['message']
            # print('server-', self.ServerTPM.W)
            print('chaosmap-', self.ServerTPM.chaosmap())
            self.sid = gen_sid()
            if self.resultServer == text_data_json['resultClient']:
                print(self.ServerTPM.chaosmap())
                # ClientW = np.array(text_data_json['W'])
                # ttt = True
                # for i in range(len(self.ServerTPM.W)):
                #     for j in range(len(self.ServerTPM.W[i])):
                #         if self.ServerTPM.W[i][j] != ClientW[i][j]:
                #             ttt = False
                if self.ServerTPM.chaosmap()==text_data_json['chaosmap']:
                    print(self.ServerTPM.chaosmap()==text_data_json['chaosmap'])
                    print('server-', self.ServerTPM.W)
                    print('client-',np.array(text_data_json['W']))
                    print("FinishSync:{}".format(self.ServerTPM.W))
                    result = ''
                    for i in range(len(self.ServerTPM.W)):
                        for j in range(len(self.ServerTPM.W[i])):
                            result += str(self.ServerTPM.W[i][j])
                    session = Sessions(
                        sessionKey = result
                    )
                    print(1111, session.id)
                    session.save()
                    self.scope["user"].sessionId = session
                    self.scope["user"].save()
                    self.send(text_data=json.dumps({
                        'type': 'FinishSync',
                        'message': 'FinishSync hehe',
                    }))
                    # print(11111111111111111111)
                    # time.sleep(60)
                    # print(22222222222222222222)
                    # currentSession = self.scope["user"].sessionId
                    # currentSession.delete()
                    # self.send(text_data=json.dumps({
                    #     'type': 'Resync',
                    #     'message': 'Resync tpms',
                    # }))
                else:
                    # print(self.sid)
                    # print(self.ServerTPM.X)
                    # print('server-', self.ServerTPM.W)
                    # print('client-',np.array(text_data_json['W']))
                    # print('result1-',self.ServerTPM.tau)
                    # print('result2-',int(text_data_json['resultClient']))
                    self.ServerTPM.update(int(text_data_json['resultClient']), 'hebbian')
                    #print(self.sid)
                    #print(self.ServerTPM.W)
                    # vector = []
                    # for i in range(len(self.X)):
                    #     vector.append([])
                    #     for j in range(len(self.X[i])):
                    #         vector[i].append(X[i][j])
                    self.send(text_data=json.dumps({
                        'type': 'GetSidAndResultTrue',
                        'sid': int(self.sid),
                        'vector': self.ServerTPM.X.tolist(),
                        "Result": int(self.resultServer),
                        "W": self.ServerTPM.W.tolist(),
                    }))
            else:
                # vector = []
                # for i in range(len(self.X)):
                #     vector.append([])
                #     for j in range(len(self.X[i])):
                #         vector[i].append(X[i][j])
                self.send(text_data=json.dumps({
                    'type': 'GetSidAndResultFalse',
                    'sid': int(self.sid),
                    'vector': self.ServerTPM.X.tolist(),
                    "Result": int(self.resultServer),
                }))                    
    
    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    def weights(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        self.ServerTPM.receive_vector(list_vec)
        self.ServerTPM.send_output(self)
        if self.ServerTPM.tpm.out == text_data['output']:
            self.ServerTPM.tpm.update_weights(text_data['output'])
        # self.send(text_data=json.dumps({
        #     'type': 'chat',
        #     'message': message
        # }))

    def join(self, event): #начать тут
        channel = event['channel']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    # def my_message(self, event):
    #     message = event['message']

    #     print("Message from client-" + message)
