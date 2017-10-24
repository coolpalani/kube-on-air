.PHONY: cluster boot bootstrap network teardown kuard
all: kuard
cluster boot: bootstrap
bootstrap network teardown:
	@ansible-playbook $@.yml

# Some kubectl alias targets
kuard:
	kubectl apply -f manifests/pods/$@.yml
get-%:
	kubectl get $*
show-%:
	kubectl describe $*

# Some cleanup targets
.PHONY: clean
clean: clean-kuard
clean-%:
	kubectl delete -f manifests/pods/$*.yml
dist-clean: clean teardown
	sudo $(RM) -rf .ansible
	$(RM) *.bak *.retry .*.sw? **/.*.sw?

# TravisCI targets
.PHONY: ci-ansible
ci-test-%: ci-ansible ci-ping-%
	ansible-playbook -vvv $*.yml \
		-i inventories/test/inventory.ini -c local -e travis_ci=true \
		-e gitsite=https://github.com/
ci-ping-%:
	ansible -vvv -m ping -i inventories/test/inventory.ini -c local $*
ci-ansible:
	git clone https://github.com/ansible/ansible .ansible
	cd .ansible \
		&& sudo pip install -r requirements.txt \
		&& sudo python setup.py install 2>&1 > /dev/null
