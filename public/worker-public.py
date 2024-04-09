#!/usr/local/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from flask import Flask, request, jsonify
import os
import json
import threading
import socket
import time
import base64
import subprocess
import tempfile
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
                handle_secure_response(response)

            print()

    def disconnect(self):
        """Close the client socket"""
        self.sock.close()

mode = os.environ.get('MODE', 'Secure')
public_key = None

def init_worker():
    if mode == 'Secure':
        init_secure_socket()
    else:
        handle_secure_response({
            'command': 'get-public-key',
            'public_key': os.environ['PUBLIC_KEY'],
        })

def init_secure_socket():
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

def handle_secure_response(response):
    if response['command'] == 'get-public-key':
        set_public_key(response['public_key'])

    if response['command'] == 'compute-proof':
        call_hub('Proof', '/worker/proof', {
            'jobId': response['jobId'],
            'proof': response['proof']
        })

def set_public_key(key):
    global public_key
    public_key = key

def register_worker():
    if mode == 'Secure':
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

    call_hub('Worker registration', '/workers/register', {
        'mode': mode,
        'url': os.environ['WORKER_URL'],
        'wallet': os.environ['WORKER_WALLET'],
        'signingPublicKey': public_key
    })

def call_hub(action, endpoint, data):
    try:
        response = httpx.post(os.environ['HUB_URL'] + endpoint, json=data)

        if response.status_code == 200:
            print('{} sent to the Hub successfully.'.format(action), flush=True)
        else:
            print('Error executing "{}" action: {}'.format(action, response.text), flush=True)
            exit(1)
    except Exception as e:
        print('Error executing "{}" action: {}'.format(action, e), flush=True)
        exit(1)

def safe_b64decode(data):
    return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))

def convert_r1cs_to_zkey(r1cs):
    r1cs_file = tempfile.NamedTemporaryFile(delete=False)
    r1cs_file.write(safe_b64decode(r1cs))
    r1cs_file.close()
   
    p = subprocess.Popen(['/usr/local/bin/node', 'scripts/setup.js', r1cs_file.name], stdout=subprocess.PIPE)
    zkeyFilename = p.stdout.read().decode().replace('\n', '')

    zkey = base64.urlsafe_b64encode(open(zkeyFilename, 'rb').read()).decode()
    
    os.unlink(r1cs_file.name)
    os.unlink(zkeyFilename)

    return zkey

def decrypt_witness_mocked(ciphered_witness, ciphered_aeskey, iv):
    private_key = os.environ['PRIVATE_KEY']
    rsa_private_key = RSA.import_key(safe_b64decode(private_key))
    cipher_rsa = PKCS1_OAEP.new(rsa_private_key, hashAlgo=Crypto.Hash.SHA256)
    
    aes_key = cipher_rsa.decrypt(safe_b64decode(ciphered_aeskey))
    aes_iv = safe_b64decode(iv)
    
    cipher_aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    return unpad(cipher_aes.decrypt(safe_b64decode(ciphered_witness)), AES.block_size)

app = Flask(__name__)

init_worker()
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

@app.route('/proof', methods=['GET'])
def proof():
    jobId = request.args.get('jobId')
    r1cs = request.args.get('r1cs')
    ciphered_witness = request.args.get('witness')
    ciphered_aeskey = request.args.get('key')
    iv = request.args.get('iv')

    zkey = convert_r1cs_to_zkey(r1cs)   

    if mode == 'Secure':
        cmd = json.dumps({
            'command': 'compute-proof',
            'jobId': jobId,
            'zkey': zkey,
            'witness': ciphered_witness,
            'key': ciphered_aeskey,
            'iv': iv
        }).encode()

        client.send_data(cmd)
    else:
        witness = decrypt_witness_mocked(ciphered_witness, ciphered_aeskey, iv)

        p = subprocess.Popen(['/usr/local/bin/node', 'scripts/proof.js', zkey, witness], stdout=subprocess.PIPE)
        proof = p.stdout.read().decode().replace('\n', '')

        handle_secure_response({
            'command': 'compute-proof',
            'jobId': jobId,
            'proof': proof,
        })

    return jsonify({})
