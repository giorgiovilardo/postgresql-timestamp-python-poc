container_name := "postgrespoc"

[private]
default:
  @just --list --unsorted

sync:
  pip-sync requirements.txt

req:
  pip-compile --strip-extras -o requirements.txt requirements.in

startdb name=container_name:
  docker run --name {{name}} -e POSTGRES_PASSWORD=password --rm -d -p 5432:5432 postgres:latest

stopdb name=container_name:
  docker kill {{name}}

shell name=container_name:
  docker exec -u postgres -it {{name}} bash

psql name=container_name:
  docker exec -u postgres -it {{name}} psql
