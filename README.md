#Simple Mesos Dashboard

![Dashboard](/screenshot/screenshot.png?raw=true "Screenshot")


## Docker

`
docker build -t mesos-dashboard .
docker run -e MESOS=http://my_mesos:5050/ -it mesos-dashboard
`
