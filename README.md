# Pre-requisites
```
# docker
sudo apt-get install docker-ce

# docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.20.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

# Reset
```
./reset.sh
# navigate to localhost:8081
```

# Start development server
```
docker-compose up -d
```

# Run unit tests
```
./runtests.sh
```

# Build command
```
./build.sh build|push|remove <branch> docker-compose.yml|ci-compose.yml
```
