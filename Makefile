.PHONY: run helm_install helm_upgrade

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

helm_install:
	helm install url-shortener ./helm-chart

helm_upgrade:
	helm upgrade url-shortener ./helm-chart

docker-build-push:
	docker build . -t localhost:5000/url-shortener:latest
