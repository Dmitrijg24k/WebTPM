import json
from re import S
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import numpy as np
import math
from random import randrange


class TpmConsumer(WebsocketConsumer):
    # let ServerTPM = 
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            'type': 'ServerReadySync',
            'message': 'Client connected'
        }))
        # self.room_group_name = 'text'

        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_group_name,
        #     self.channel_name
        # )
        # self.accept()
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        #print("connect0", message)
        if text_data_json['type'] == 'GetParametrs':
            print("connect1")
            message = text_data_json['message']
            self.ServerTPM = TPMClient(text_data_json['k'],text_data_json['n'], text_data_json['l'])
            self.send(text_data=json.dumps({
                'type': 'start',
                'message': message
            }))
        if text_data_json['type'] == 'weights':
            # print("connect2", self.ServerTPM.tpm.k)
            message = text_data_json['message']
            self.ServerTPM.receive_vector(text_data_json['list_vec'])
            self.ServerTPM.send_output(self)
            if self.ServerTPM.tpm.out == text_data_json['output']:
                self.ServerTPM.tpm.update_weights(text_data_json['output'])
            # self.send(text_data=json.dumps({
            #     'type': 'chat',
            #     'message': message
            # }))
        if text_data_json['type'] == 'receive_chaos_output':
            print("connect3", text_data_json['output'], self.ServerTPM.tpm.chaosmap())
            self.send(text_data=json.dumps({
                'type': 'receive_chaos_output2',
                'message': message,
                'output': self.ServerTPM.tpm.chaosmap(),
            }))
            if text_data_json['output'] == self.ServerTPM.tpm.chaosmap():
                self.ServerTPM.IsSync = True
                print('SUCCESS: synched with Alice')
                self.disconnect()
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )
    
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

class TPMClient:
    def __init__(self, k = 16, n = 16, l = 100):
        self.user = None
        self.tpm = TPM(k, n, l)
        self.n = 0
        self.IsSync = False

    def send_vector_and_output(self, sio):
        vector = self.rand_vec()
        list_vec = [np.array(vector[x:x+16]) for x in range(0, len(vector), 16)]
        self.tpm.get_output(list_vec)

        # sio.emit('weights',
        #     {
        #         'msg':'sending random vector and output',
        #         'vector': vector,
        #         'output': self.tpm.out,
        #         # 'sid': tpmclient.partner_sid
        #     }
        # )
        sio.send(text_data=json.dumps({
            'type': 'weights',
            'message': 'sending random vector and output',
            'vector': vector,
            'output': self.tpm.out,
        }))
        self.n += 1

    def receive_vector(self, vector_):
        vec = [np.array(x) for x in vector_]
        self.tpm.get_output(vec)

    def rand_vec(self):
        l = []
        for i in range(256):
            l.append(randrange(-100, 100))
        return l

    def send_output(self, sio): #tut
        # sio.emit('send_output',
        #     {
        #         'msg':'sending output',
        #         'output': self.tpm.out,
        #         # 'sid': tpmclient.partner_sid
        #     }
        # )
        sio.send(text_data=json.dumps({
            'type': 'output_received',
            'message': 'sending output',
            'output': self.tpm.out,
            # 'sid': tpmclient.partner_sid
        }))

    def send_chaos_output(self):
        sio.emit('send_chaos_output',
            {
                'msg':'sending chaos output',
                'output': self.tpm.chaosmap(),
                # 'sid': tpmclient.partner_sid
            }
        )

    def save_key(self):
        re = [abs(item+155) for sublist in self.tpm.weights for item in sublist]
        key = bytes(abs(x) for x in re).decode('cp437')
        print(key)
        # with open("KEYS/{}.txt".format(CHANNEL), "w") as text_file:
        #     print(key, file=text_file)


class TPM:
    def __init__(self, k_, n_, l_):
        self.k = k_
        self.n = n_
        self.l = l_
        self.weights = self.initialize_w()
        self.inputs = None
        self.H = np.zeros(self.k)
        self.out = None
        self.X = None

    def get_output(self, input_):
        self.X = input_
        self.out = 1

        for i in range(self.k):
            self.H[i] = self.signum(np.dot(input_[i], self.weights[i]))
            self.out *= self.signum(np.dot(input_[i], self.weights[i]))

    def initialize_w(self):
        p = []
        for i in range(self.k):
            p.append(np.random.randint(-self.l, self.l, size=self.n))
        return p

    def signum(self, x):
        return math.copysign(1, x)

    def update_weights(self, outputB):
        for i in range(self.k):
            for j in range(self.n):
                self.weights[i][j] += self.X[i][j] * self.out * self.isequal(self.out, self.H[i]) * self.isequal(self.out, outputB)
                self.weights[i][j] = self.g(self.weights[i][j])

    def isequal(self, A, B):
        if A==B:
            return 1.0
        else:
            return 0.0

    def g(self, w):
        if w > self.l:
            return self.l
        if w < -self.l:
            return -self.l
        else:
            return w

    def chaosmap(self):
        r = sum(list(np.hstack(self.weights)))
        #print('r-', r)
        rr = sum([abs(x) for x in (list(np.hstack(self.weights)))])
        #print('rr-', rr)
        t = float(abs(r)) / float(rr)
        #print('t-', t)
        x = t
        for i in range(rr):
            x = (3.6 + t/2)* x *(1 - x)
        #print('x-', x)
        return x
