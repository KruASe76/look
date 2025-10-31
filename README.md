# look

**RESTful API for a yet another tinder-like clothing application.**


## Running the application

### Production

0. Requirements
   - `docker`
   - `make`
   - `curl`

1. Get the `Makefile`
```shell
mkdir look
cd look
curl -sSL https://github.com/KruASe76/look/raw/refs/heads/main/Makefile -o Makefile
```

2. Set up and run the application
```shell
make
```

3. Other `make` commands
```shell
make stop     # stop the application
make restart  # stop and start the application
make clean    # stop the application and delete all persistent data
make run      # only run the application (do not check for certificates or pull the image)
make pull     # pull the application image
```

### Development

0. Requirements
   - `docker`
   - `make`
   - `git`

1. Clone the repository
```shell
git clone https://github.com/KruASe76/look.git
cd look
```

2. Set up and run the application in dev mode
```shell
make dev
```

3. Other `make` commands
```shell
make stop     # stop the application
make redev    # stop and start the application in dev mode
make clean    # stop the application and delete all persistent data
```


## Stack
- Language: [**Python 3.13**](https://www.python.org/)
- RESTful API framework: [**FastAPI**](https://fastapi.tiangolo.com/)
- Database: [**PostgreSQL**](https://www.postgresql.org/) via [**SQLModel**](https://sqlmodel.tiangolo.com/)
- Search engine: [**Elasticsearch**](https://www.elastic.co/elasticsearch)
- Deployment: [**Docker compose**](https://www.docker.com/) with [**Traefik**](https://doc.traefik.io/traefik/)
