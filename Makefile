SERVICE := admincrashboard
DESTDIR ?= dist_root
SERVICEDIR ?= /srv/$(SERVICE)

.PHONY: check exploit build install

check:
	python3 checker/template.py localhost 0 0

exploit:
	python3 exploits/XML_eXternal_entity_attack.py
	python3 exploits/directory_traversion.py 
	python3 exploits/misconfiguration.py
	python3 exploits/command_injection.py

install:
	mkdir -p $(DESTDIR)$(SERVICEDIR)
	cp -r docker-compose.yml $(DESTDIR)$(SERVICEDIR)
	cp -r admincrashboard $(DESTDIR)$(SERVICEDIR)/admincrashboard
	mkdir -p $(DESTDIR)/etc/systemd/system/faustctf.target.wants/
	ln -s /etc/systemd/system/docker-compose@.service $(DESTDIR)/etc/systemd/system/faustctf.target.wants/docker-compose@admincrashboard.service
