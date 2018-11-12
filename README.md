# HOT Platform
<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License</a>.

## Pre-requisites
```
# docker
sudo apt-get install docker-ce

# docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.20.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Reset
```
./reset.sh
# navigate to localhost:8081
```

## Start development server
```
docker-compose up -d
```

## Run unit tests
```
./runtests.sh
```

## Build command
```
./build.sh build|push|remove <branch> docker-compose.yml|ci-compose.yml
```
