#!/bin/bash
host="$1"
port="$2"

while ! nc -z "$host" "$port"; do
  echo "Esperando a que $host:$port esté disponible..."
  sleep 1
done

echo "$host:$port está disponible!"
exec "${@:3}"