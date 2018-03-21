# Clone this repository
```
git clone git@git.proteus-tech.com:hotnow/htkn-platform.git
cd  htkn-platform
```

# Build docker image
```
docker build -t registry-hotnow.proteus-tech.com/service/htkn-platform .
```

# Run docker
```
docker run --rm -p "8081:<port>" -v "$(pwd)/aiohttp:/usr/src" --name htkn-platform registry-hotnow.proteus-tech.com/service/htkn-platform:latest python -u server.py
```

`port: port on your localhost that you want to run this service`

**Have to rerun docker after change source code

# Runtest
```
docker exec -it htkn-platform bash
python3 -m pytest
```
