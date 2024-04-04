#!/usr/local/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from flask import Flask, request, jsonify
import os
import json
import threading
import socket
import time
import base64
import httpx
import Crypto.Hash.SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad

class VsockClient:
    """Client"""
    def __init__(self, conn_tmo=5):
        self.conn_tmo = conn_tmo

    def connect(self, endpoint):
        """Connect to the remote endpoint"""
        self.sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        self.sock.settimeout(self.conn_tmo)
        self.sock.connect(endpoint)

    def send_data(self, data):
        """Send data to a remote endpoint"""
        self.sock.sendall(data)

    def recv_data(self):
        """Receive data from a remote endpoint"""
        while True:
            while True:
                try:
                    data = self.sock.recv(1024).decode()
                except socket.error:
                    break
                if not data:
                    break
                
                response = json.loads(data)

                if response['command'] == 'get-public-key':
                    set_public_key(response['public_key'])

            print()

    def disconnect(self):
        """Close the client socket"""
        self.sock.close()

def init_socket():
    global client
    client = VsockClient()

    while True:
        try:
            print('Connecting to Worker Secure...', flush=True)
            client.connect((16, 5005))
            threading.Thread(target=client.recv_data).start()
            break
        except Exception as e:
            time.sleep(10)

mode = os.environ.get('MODE', 'Secure')
private_key = None
public_key = None

def set_private_key(key):
    global private_key
    private_key = key

def set_public_key(key):
    global public_key
    public_key = key

def register_worker():
    while not public_key:
        cmd = json.dumps({'command': 'get-public-key'}).encode()
        client.send_data(cmd)
        print('Asked for public key to Worker Secure...', flush=True)
        time.sleep(10)
    
    print('Mode: {}'.format(mode))
    print('Hub URL: {}'.format(os.environ['HUB_URL']))
    print('Worker URL: {}'.format(os.environ['WORKER_URL']))
    print('Worker Wallet: {}'.format(os.environ['WORKER_WALLET']))
    print('Public key: {}'.format(public_key), flush=True)

    try:
        response = httpx.post(os.environ['HUB_URL'] + '/worker/register', json={
            'mode': mode,
            'url': os.environ['WORKER_URL'],
            'wallet': os.environ['WORKER_WALLET'],
            'public_key': public_key
        })

        if response.status_code == 200:
            print('Worker registered on Hub successfully.', flush=True)
        else:
            print('Error registering worker: {}'.format(response.text), flush=True)
            exit(1)
    except Exception as e:
        print('Error registering worker: {}'.format(e), flush=True)
        exit(1)

def safe_b64decode(data):
    return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))

app = Flask(__name__)

if mode == 'Secure':
    init_socket()
    threading.Thread(target=client.recv_data).start()
else:
    set_private_key(os.environ['PRIVATE_KEY'])
    set_public_key(os.environ['PUBLIC_KEY'])

register_worker()

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'mode': mode,
        'public_key': public_key,
        'hub_url': os.environ['HUB_URL'],
        'worker_url': os.environ['WORKER_URL'],
        'worker_wallet': os.environ['WORKER_WALLET']
    })

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({ 'status': 'Ok' })

@app.route('/decrypt', methods=['GET'])
def decrypt():
    data = request.args.get('data')
    key = request.args.get('key')
    iv = request.args.get('iv')

    if mode == 'Secure':
        cmd = json.dumps({
            'command': 'decrypt',
            'data': data,
            'key': key,
            'iv': iv
        }).encode()

        client.send_data(cmd)
    else:                   
        rsa_private_key = RSA.import_key(safe_b64decode(private_key))
        cipher_rsa = PKCS1_OAEP.new(rsa_private_key, hashAlgo=Crypto.Hash.SHA256)
        
        aes_key = cipher_rsa.decrypt(safe_b64decode(key))
        aes_iv = safe_b64decode(iv)
        
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        data = unpad(cipher_aes.decrypt(safe_b64decode(data)), AES.block_size)

        print(data.decode(), flush=True)

    return jsonify({})
