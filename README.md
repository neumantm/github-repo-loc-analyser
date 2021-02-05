# github-repo-loc-analyser
Software to analyse the LOC and LOCC for random github repos

## Running workers
Start rabbitmq server: `docker run -p 5672:5672 rabbitmq`
Start worker `poetry run celery -A github_repo_loc_analyser.tasks worker `
