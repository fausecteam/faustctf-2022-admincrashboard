#!/usr/bin/env python3

from ctf_gameserver import checkerlib

import socket
import secrets
import requests
import string
import crypt
from bs4 import BeautifulSoup
from hmac import compare_digest
import base64
import subprocess
import os


port = 5002
http_port = 5000

identity=f"{os.path.dirname(__file__)}/ssh-key"

class TemplateChecker(checkerlib.BaseChecker):

    def cmd_via_ssh(self, cmd, extra_cmd=""):
        assert '"' not in cmd
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -oBatchMode=yes -i {identity} -p {port} root@{self.ip} \"{cmd}\""
        ssh_cmd += extra_cmd
        print(ssh_cmd)
        try:
            output = subprocess.check_output(ssh_cmd, timeout=30, shell=True)
            return checkerlib.CheckResult.OK, output
        except:
            # try to diff DOWN from FAULTY
            try:
                s = socket.socket(socket.AF_INET6)
                s.connect((self.ip, port))
                assert s.recv(3) == b"SSH"
                return checkerlib.CheckResult.FAULTY, None
            except:
                return checkerlib.CheckResult.DOWN, None


    def place_flag(self, tick):

        # create credentials
        #username = f"{secrets.choice(string.ascii_lowercase)}{secrets.token_hex(2+secrets.randbelow(5))}"
        #password = secrets.token_hex()
        flag = checkerlib.get_flag(tick)
        file = f"{secrets.token_hex(2+secrets.randbelow(5))}.button"

        
        checkerlib.set_flagid(f"you find the flag in root's home in {file}")
        print(f"you find the flag in root's home in {file}")
        print(f"flag: {flag}")

        # store credentials
        checkerlib.store_state(f"file_{tick}", file)

        print("credentials stored.")

        # place flag
        print("creating flag")
        print("nt nr 1")
        result, _ = self.cmd_via_ssh(f"echo {flag} > {file}")
        if result != checkerlib.CheckResult.OK:
            return result

        # check if flag was placed
        print("checking flag")
        result, output = self.cmd_via_ssh(f"cat {file}", extra_cmd=" | tail -n 1")
        if result != checkerlib.CheckResult.OK:
            return result
        fflag = output.decode()

        print(f"flag: {fflag}")
        if fflag != f"{flag}\n":
            print(f"wrong flag!")
            print(f"{flag}\n")
            return checkerlib.CheckResult.FAULTY

        print("PLACING FLAG OK")
        return checkerlib.CheckResult.OK

    def check_service(self):

        port = http_port

        print("ping index")
        res = requests.get(f"http://[{self.ip}]:{port}/")
        if res.status_code != 200:
            print("SERVICE DOWN")
            return checkerlib.CheckResult.DOWN

        # generate data
        print("generating random data")
        username = f"{secrets.choice(string.ascii_lowercase)}{secrets.token_hex(2+secrets.randbelow(5))}"
        password = secrets.token_hex()
        secret = secrets.token_hex()
        file = f"{secrets.token_hex(2+secrets.randbelow(5))}.button"

        print(f"username: {username}")
        print(f"password: {password}")
        print(f"file    : {file}")

        credentials = {
            'username': username,
            'password': password
        }

        # Create Account
        print("creating account")
        url = f"http://[{self.ip}]:{port}/register"
        res = requests.post(url, data = credentials)
        print(f"status: {res.status_code}")

        # login
        s = requests.Session()
        print("logging in")
        res = s.post(f"http://[{self.ip}]:{port}/login", data = credentials)
        res = s.get(f"http://[{self.ip}]:{port}/login", allow_redirects=False)
        print(f"status: {res.status_code}")
        if res.status_code != 302:
            print("ERROR! no redirect!")
            return checkerlib.CheckResult.FAULTY

        # create new file
        # TODO noch paar befehle
        cmd = str(base64.b64encode(f"echo {secret} | openssl passwd -6 -stdin".encode()))
        content = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<command>\n<name>Generate Password</name>\n<script>echo {cmd[1:]} | base64 --decode | . /dev/stdin</script>\n</command>"

        print("file content:")
        print(content)

        print("create button")
        res = s.post(f"http://[{self.ip}]:{port}/add", data = {'filename':file})
        print(f"status: {res.status_code}")
        print("place content")
        res = s.post(f"http://[{self.ip}]:{port}/edit?button=/home/{username}/{file}", data = {'content':content})
        print(f"status: {res.status_code}")

        # execute button
        print(f"execute button")
        res = s.get(f"http://[{self.ip}]:{port}/execute?button=/home/{username}/{file}")
        print(f"status: {res.status_code}")
        hash = res.text.split('\n')[0]
        print(f"hash: {hash}")

        # verify output
        print("check output")
        if not compare_digest(hash, crypt.crypt(secret, hash)):
            print("wrong hash!")
            return checkerlib.CheckResult.FAULTY

        print("CHECK SERVICE OK")
        return checkerlib.CheckResult.OK

    def check_flag(self, tick):
        # restore credentials

        flag = checkerlib.get_flag(tick)
        file = checkerlib.load_state(f"file_{tick}")
        print(f"flag: {flag}")
        print(f"file: {file}")

        # check if flag is there
        print("checking flag")
        result, output = self.cmd_via_ssh(f"cat {file}", extra_cmd=" | tail -n 1")
        if result != checkerlib.CheckResult.OK:
            return result
        fflag = output.decode()

        print(f"flag: {fflag}")
        if fflag != f"{flag}\n":
            print("wrong or no flag!")
            return checkerlib.CheckResult.FLAG_NOT_FOUND

        print("FLAG CHECK OK")
        return checkerlib.CheckResult.OK


if __name__ == '__main__':

    checkerlib.run_check(TemplateChecker)
