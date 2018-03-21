
Clone this repository

```
git clone https://git.proteus-tech.com/hotnow/htkn-platform
cd  htkn-platform
```

Build docker image
```
docker build -t registry-hotnow.proteus-tech.com/service/htkn-platform .
```

Run docker
```
docker run --rm -p "8081:<port>" -v "$(pwd)/aiohttp:/usr/src" registry-hotnow.proteus-tech.com/service/htkn-platform:latest python -u server.py
```

Runtest
```
docker exec -it thirsty_carson bash
python3 -m pytest
```