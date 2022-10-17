#!/bin/bash

USERNAME=$1
PASSWORD=$2
if [[ "$USERNAME" =~ [^a-zA-Z0-9] ]]; then
  echo "INVALID USERNAME"
  exit
fi
if [[ "$PASSWORD" =~ [^a-zA-Z0-9] ]]; then
  echo "INVALID PASSWORD"
  exit
fi

adduser --gecos "" $USERNAME || exit
chgrp crashboard /home/$USERNAME
echo $USERNAME":"$PASSWORD | chpasswd