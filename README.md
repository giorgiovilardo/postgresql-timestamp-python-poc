# :ok:

```shell
pyenv local 3.12.1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker run --name postgrespoc -e POSTGRES_PASSWORD=password --rm -d -p 5432:5432 postgres:latest
python main.py

# Good
xh localhost:8000 tz="2024-02-13T23:45:14Z" no_tz="2024-02-13T22:45:14"
xh localhost:8001 tz="2024-02-13T23:45:14Z" no_tz="2024-02-13T22:45:14"
# Bad
xh localhost:8000 tz="2024-02-13T23:45:14Z" no_tz="2024-02-13T22:45:14Z"
xh localhost:8001 tz="2024-02-13T23:45:14Z" no_tz="2024-02-13T22:45:14Z"
# Bad
xh localhost:8000 tz="2024-02-13T23:45:14Z" no_tz="2024-02-13T21:45:14-0100"
xh localhost:8001 tz="2024-02-13T23:45:14Z" no_tz="2024-02-13T21:45:14-0100"

# or `just startdb`
docker kill postgrespoc
# or `just stopdb`
```