FROM faust.cs.fau.de:5000/admincrashboard-deps

# SET UP USER MANAGEMENT
COPY welcome.button /etc/skel/welcome.button
COPY sudoers /etc/sudoers
COPY adduser.conf /etc/adduser.conf

COPY addnewuser.sh /usr/sbin/addnewuser
RUN chmod +x /usr/sbin/addnewuser
RUN chmod -R 755 /root

# install root ssh key
RUN mkdir -p /root/.ssh
COPY ssh-key.pub /root/.ssh/authorized_keys
COPY sshd_config /etc/ssh/sshd_config

# CRONJOB TO DELETE OLD USERS
COPY expire.sh /bin/expire
RUN chmod 0700 /bin/expire
COPY crontab /etc/crontab
RUN chmod 0644 /etc/crontab

# INSTALL APP
COPY --chown=crashboard:crashboard app app
EXPOSE 5000/tcp
EXPOSE 22/tcp
USER root

# INSTALL START SCRIPT
copy start.sh start.sh
RUN chmod 0700 start.sh

# RUN WEBAPP
ENTRYPOINT ["./start.sh"]
