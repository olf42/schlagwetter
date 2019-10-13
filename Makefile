.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep -E '^[\.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: download
download: ## downloads the dataset
	wget "http://download.codingdavinci.de/index.php/s/YxQy9bzJSXk5cF6/download?path=%2F&files=Data_Ungluecke_2019-08-13.xml" -O Data_Ungluecke_2019-08-13.xml


.PHONY: develop
develop: ## install the requirements to run the program
	pip install -r requirements.txt	

.PHONY: convert
convert: ## Converts the xml file of the data provider to a json file 
	./schlagwetter.py convert Data_Ungluecke_2019-08-13.xml

export CUSTOM_COMPILE_COMMAND:= make update-requirements

.PHONY: update-requirements
update-requirements:
	python -m piptools compile --rebuild --upgrade --quiet requirements.in
	python -m piptools compile --rebuild --upgrade --quiet requirements-dev.in

.PHONY: install-agent
install-agent: ## Install provit agent
	cp schlagwetter.yaml ~/.provit/agents
