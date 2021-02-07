# github-repo-loc-analyser
Software to analyse the LOC and LOCC for random github repos

## Runing with docker
See the [docker-compose.yaml](docker-compose.yaml).

## Configuration
An example `grla.conf` for use with the docker compose file looks like this:
```
[main]
logging_conf = /app/docker-default-logging.conf
data_dir = /data
tmp_dir = /tmp-large
num_repos_per_page = 3
num_repo_pages = 3
debug_remove_data = False
debug_abort_on_error = False
old_repo_date = 2012-06-01
new_repo_date = 2020-06-01
minimum_code_lines = 100
github_auth = token 00000000000000000000000000000000

[repo_filters]
languages = Java,Python
size = 10..100000
stars = >20
old_repo_created = <2012-01-01
old_repo_updated = >2012-01-01
new_repo_created = <2020-01-01
new_repo_updated = >2020-01-01

[celery]
broker_url = amqp://guest:guest@rabbitmq:5672//
result_backend = rpc://
```

## Development
### Running workers
Start rabbitmq server: `docker run -p 5672:5672 rabbitmq`
Start worker `poetry run celery -A github_repo_loc_analyser.tasks worker -P solo`
We need to use a `solo` task pool, because otherwise the worker concurrently clones multiple repos into the same folder.
