USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)
# change user and passwd if you use it

all: 
	 docker run -it --rm --name gemini-container2 -v $$PWD:/usr/src/app  gemini-app
	 #docker run -it --rm --name gemini-container2 -v $$PWD:/usr/src/app  --user `id -u`:`id -g`  gemini-app
build:
	 docker build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) -t gemini-app .
