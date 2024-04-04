#!/usr/local/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import socket
import json
import base64
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

    def recv_data(self):
        """Receive data from a remote endpoint"""
        while True:
            (from_client, (remote_cid, remote_port)) = self.sock.accept()
            # Read 1024 bytes at a time
            while True:
                try:
                    data = from_client.recv(1024).decode()
                except socket.error:
                    break
                if not data:
                    break
                
                cmd = json.loads(data)

                if cmd['command'] == 'get-public-key':
                    print('Sending public key to client...', flush=True)
                    print('Public key: {}'.format(base64.urlsafe_b64encode(public_key).decode()), flush=True)

                    response = json.dumps({
                        'command': 'get-public-key',
                        'public_key': base64.urlsafe_b64encode(public_key).decode()
                    }).encode()

                    from_client.sendall(response)

                if cmd['command'] == 'decrypt':
                    print('Decrypting: {}'.format(cmd['data']), flush=True)
                    
                    rsa_private_key = RSA.import_key(private_key)
                    cipher_rsa = PKCS1_OAEP.new(rsa_private_key, hashAlgo=Crypto.Hash.SHA256)
                    
                    aes_key = cipher_rsa.decrypt(self.safe_b64decode(cmd['key']))
                    aes_iv = self.safe_b64decode(cmd['iv'])
                    
                    cipher_aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
                    data = unpad(cipher_aes.decrypt(self.safe_b64decode(cmd['data'])), AES.block_size)

                    print(data.decode(), flush=True)
            print()
            from_client.close()

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
