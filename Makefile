docker:
	docker build -t atc_mithermometer_builder .

build: docker
	docker run -ti --user $$(id -u):$$(id -g) -v $$(pwd)/ATC_Thermometer:/code atc_mithermometer_builder make
