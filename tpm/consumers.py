import json
from re import S
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import numpy as np
import math
import random
from random import randrange
import time
from todos.models import Sessions


class mersenne_rng(object):
    def __init__(self, seed = 5489):
        self.state = [0]*624
        self.f = 1812433253
        self.m = 397
        self.u = 11
        self.s = 7
        self.b = 0x9D2C5680
        self.t = 15
        self.c = 0xEFC60000
        self.l = 18
        self.index = 624
        self.lower_mask = (1<<31)-1
        self.upper_mask = 1<<31

        # update state
        self.state[0] = seed
        for i in range(1,624):
            self.state[i] = self.int_32(self.f*(self.state[i-1]^(self.state[i-1]>>30)) + i)

    def twist(self):
        for i in range(624):
            temp = self.int_32((self.state[i]&self.upper_mask)+(self.state[(i+1)%624]&self.lower_mask))
            temp_shift = temp>>1
            if temp%2 != 0:
                temp_shift = temp_shift^0x9908b0df
            self.state[i] = self.state[(i+self.m)%624]^temp_shift
        self.index = 0

    def get_random_number(self):
        if self.index >= 624:
            self.twist()
        y = self.state[self.index]
        y = y^(y>>self.u)
        y = y^((y<<self.s)&self.b)
        y = y^((y<<self.t)&self.c)
        y = y^(y>>self.l)
        self.index+=1
        return self.int_32(y)

    def int_32(self, number):
        return int(0xFFFFFFFF & number)


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
        print(1111111111, X)
        X = X.reshape([k, n])
        print(2222222222, X)
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

    def theta(self, t1, t2):
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


def gen_rand_vector(seed, L, K, N): # сид, диапазон, количество нейронов, количество входов
    generator = mersenne_rng(seed)
    
    result = np.empty((K,N), dtype = int)
    for i in range(K):
        for j in range(N):
            result[i][j] = (generator.get_random_number() % (2 * L))
            if result[i][j] - L < 0:
                result[i][j] *= -1
    # print('seed, vector', seed, np.random.randint(-l, l + 1, [k, n]))
    return result


def gen_seed():
    return random.randint(0, 1000)


class TpmConsumer(WebsocketConsumer):
    # let ServerTPM = 
    def connect(self):
        self.accept()
        # print(dir(self.scope["user"]))
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
            # message = text_data_json['message']
            # self.ServerTPM = TPMClient(text_data_json['k'],text_data_json['n'], text_data_json['l'])
            self.send(text_data=json.dumps({
                'type': 'ServerReadySync',
                'message': 'Server is ready'
            }))
        if text_data_json['type'] == 'GetParametrs':
            #print('GetParametrs')
            # message = text_data_json['message']
            self.timer = 0
            self.k = text_data_json['k']
            self.n = text_data_json['n']
            self.l = text_data_json['l']
            self.ServerTPM = Machine(text_data_json['k'],text_data_json['n'], text_data_json['l'])
            #print('GetParametrs2')
            self.seed = gen_seed()
            # vector = []
            self.ServerTPM.X = gen_rand_vector(self.seed, self.l, self.k, self.n)#text_data_json['X']#gen_rand_vector(self.seed, self.l, self.k, self.n)
            print(self.seed, '-XXXXXXXXX----', self.ServerTPM.X)
            # for i in range(len(X)):
            #     vector.append([])
            #     for j in range(len(X[i])):
            #         vector[i].append(X[i][j])
            self.send(text_data=json.dumps({
                'type': 'GetFirstSeed',
                'seed': self.seed,
                'vector': self.ServerTPM.X.tolist()
            }))
        if text_data_json['type'] == 'GetResultClient':
            print('GetResultClient')
            #print(self.ServerTPM.k, self.ServerTPM.n, self.ServerTPM.l)
            #print("seed:{}".format(self.seed))
            # self.X = gen_rand_vector(self.seed, self.l, self.k, self.n)
            #print("Vector:{}".format(self.X))
            self.resultServer = self.ServerTPM.get_output(self.ServerTPM.X)
            self.seed = gen_seed()
            self.ServerTPM.X = gen_rand_vector(self.seed, self.l, self.k, self.n)
            #print("resultServer:{}".format(self.resultServer))
            #print("resultClient:{}".format(text_data_json['resultClient']))
            #self.ServerTPM.update(self.resultClient, 'hebbian')
            # message = text_data_json['message']
            # print('server-', self.ServerTPM.W)
            print(self.seed, '-XXXXXXXXX----', self.ServerTPM.X)
            print('chaosmap-', self.ServerTPM.chaosmap())
            if self.resultServer == text_data_json['resultClient']:
                print('resultServer = resultClient')
                print(self.ServerTPM.chaosmap())
                # ClientW = np.array(text_data_json['W'])
                # ttt = True
                # for i in range(len(self.ServerTPM.W)):
                #     for j in range(len(self.ServerTPM.W[i])):
                #         if self.ServerTPM.W[i][j] != ClientW[i][j]:
                #             ttt = False
                if self.ServerTPM.chaosmap()==text_data_json['chaosmap']:
                    print('resultServer chaosmap = resultClient chaosmap')
                    print(self.ServerTPM.chaosmap()==text_data_json['chaosmap'])
                    #print('server-', self.ServerTPM.W)
                    #print('client-',np.array(text_data_json['W']))
                    #print("FinishSync:{}".format(self.ServerTPM.W))
                    result = ''
                    for i in range(len(self.ServerTPM.W)):
                        for j in range(len(self.ServerTPM.W[i])):
                            result += str(self.ServerTPM.W[i][j])
                    session = Sessions(
                        sessionKey = result
                    )
                    currentSession = self.scope["user"].sessionId
                    if (currentSession):
                        currentSession.delete()
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
                    print('resultServer chaosmap != resultClient chaosmap')
                    # print(self.seed)
                    # print(self.ServerTPM.X)
                    # print('server-', self.ServerTPM.W)
                    # print('client-',np.array(text_data_json['W']))
                    # print('result1-',self.ServerTPM.tau)
                    # print('result2-',int(text_data_json['resultClient']))
                    self.ServerTPM.update(int(text_data_json['resultClient']), 'hebbian')
                    # print(self.seed)
                    # print(self.ServerTPM.W)
                    # vector = []
                    # for i in range(len(self.X)):
                    #     vector.append([])
                    #     for j in range(len(self.X[i])):
                    #         vector[i].append(X[i][j])
                    self.send(text_data=json.dumps({
                        'type': 'GetSeedAndResultTrue',
                        'seed': int(self.seed),
                        'vector': self.ServerTPM.X.tolist(),
                        "Result": int(self.resultServer),
                        "W": self.ServerTPM.W.tolist(),
                    }))
            else:
                print('resultServer != resultClient')
                # vector = []
                # for i in range(len(self.X)):
                #     vector.append([])
                #     for j in range(len(self.X[i])):
                #         vector[i].append(X[i][j])
                self.send(text_data=json.dumps({
                    'type': 'GetSeedAndResultFalse',
                    'seed': int(self.seed),
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
