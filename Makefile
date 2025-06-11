.PHONY: run helm_install helm_upgrade docker-build-push uninstall

GIT_COMMIT := $(shell git rev-parse --short HEAD)
GIT_DIRTY := $(shell git diff --quiet || echo "-dirty")
TAG := $(GIT_COMMIT)$(GIT_DIRTY)

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

helm_install:
	helm install url-shortener --set image.tag $(TAG) ./helm-chart

helm_upgrade:
	helm upgrade url-shortener --set image.tag $(TAG) ./helm-chart

helm_template:
	helm template url-shortener ./helm-chart

uninstall:
	helm uninstall url-shortener

docker-build-push:
	docker build . -t localhost:5000/url-shortener:$(TAG)
	docker push localhost:5000/url-shortener:$(TAG)
