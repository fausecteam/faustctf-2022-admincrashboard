admincrashboard
===============

This is the source code for the "admincrashboard" service from [FAUST CTF 2022](https://2022.faustctf.net).

**As it was written for a CTF service, the code is deliberately insecure and contains exploitable bugs. It
is provided for educational purposes only, do not even think about (re-) using it for anything productive!**

The code is released under the ISC License, see LICENSE.txt for details.

# Intended Vulnerabilities

 - Command Injection runs as serveruser
 - Directory Traversal to the flag using the editor
 - XXE in a button file