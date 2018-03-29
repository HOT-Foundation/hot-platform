# Pre-requisites

Clone repository
```
git clone git@git.proteus-tech.com:hotnow/htkn-platform.git
cd htkn-platform
```

Log in to proteus docker-registry (https://ratticdb.proteus-tech.com:7078/cred/detail/918/)
** If you get 404 error, Please contract infra give you a permission.
```
docker login registry-hotnow.proteus-tech.com
```

Required software
```
# docker
sudo apt-get install docker-ce

# docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.20.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

# One-line installation
```
docker-compose build && docker-compose up -d

navigate to localhost:8081
```

# Build local development container
Do this everytime you want to install new python package
```
docker-compose build
```

# Start development server
```
docker-compose up -d
```

# Run unit tests
```
./runtests.sh
```

# Reset
Build new image and reset environment
```
./reset.sh
```