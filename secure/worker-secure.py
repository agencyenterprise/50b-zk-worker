#!/usr/local/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import socket
import json
import base64
import subprocess
import Crypto.Hash.SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad

class VsockServer:
    """Server"""
    def __init__(self, conn_backlog=128):
        self.conn_backlog = conn_backlog

    def bind(self, port):
        """Bind and listen for connections on the specified port"""
        self.sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        self.sock.bind((socket.VMADDR_CID_ANY, port))
        self.sock.listen(self.conn_backlog)

    def safe_b64decode(self, data):
        return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
    
    def decrypt_witness(self, ciphered_witness, ciphered_aeskey, iv):
        rsa_private_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_private_key, hashAlgo=Crypto.Hash.SHA256)
        
        aes_key = cipher_rsa.decrypt(self.safe_b64decode(ciphered_aeskey))
        aes_iv = self.safe_b64decode(iv)
        
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        return unpad(cipher_aes.decrypt(self.safe_b64decode(ciphered_witness)), AES.block_size)

    def handle_socket_command(self, cmd, from_client):
        try:
            if cmd['command'] == 'get-public-key':
                print('Sending public key to client...', flush=True)
                print('Public key: {}'.format(base64.urlsafe_b64encode(public_key).decode()), flush=True)

                response = json.dumps({
                    'command': 'get-public-key',
                    'public_key': base64.urlsafe_b64encode(public_key).decode()
                }).encode()

                from_client.sendall(response)

            if cmd['command'] == 'compute-proof':
                jobId = cmd['jobId']
                zkey = cmd['zkey']
                ciphered_witness = cmd['witness']
                ciphered_aeskey = cmd['key']
                iv = cmd['iv']

                print('Computing proof for: {}'.format(ciphered_witness), flush=True)

                witness = self.decrypt_witness(ciphered_witness, ciphered_aeskey, iv)

                p = subprocess.Popen(['/usr/local/bin/node', '/app/scripts/proof.js', zkey, witness], stdout=subprocess.PIPE)
                proof = p.stdout.read().decode().replace('\n', '')

                response = json.dumps({
                    'command': 'compute-proof',
                    'jobId': jobId,
                    'proof': proof,
                }).encode()

                from_client.sendall(response)
        except Exception as e:
            print('Error executing command "{}": {}'.format(cmd, e), flush=True)

    def recv_data(self):
        """Receive data from a remote endpoint"""
        print('Waiting for command...', flush=True)
        (from_client, (remote_cid, remote_port)) = self.sock.accept()
        while True:
            data = bytearray()
            while True:
                try:
                    chunk = from_client.recv(1024)
                except socket.error:
                    break

                if not chunk:
                    break

                data.extend(chunk)

                try:
                    cmd = json.loads(data.decode())
                    self.handle_socket_command(cmd, from_client)
                    break
                except ValueError:
                    continue

def main():
    global private_key
    global public_key

    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    server = VsockServer()
    server.bind(5005)
    server.recv_data()

if __name__ == "__main__":
    main()
