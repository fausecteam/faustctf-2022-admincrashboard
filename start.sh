docker-compose down
docker image rm faust.cs.fau.de:5000/admincrashboard-deps
docker image rm faust.cs.fau.de:5000/admincrashboard
docker-compose up --build