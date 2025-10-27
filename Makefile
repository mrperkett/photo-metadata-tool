IMAGE_NAME = photo-metadata-tool
REGISTRY = ghcr.io/mrperkett
VERSION := $(shell python3 scripts/get_version.py)

build:
	docker build -t ${REGISTRY}/$(IMAGE_NAME):$(VERSION) -t ${REGISTRY}/${IMAGE_NAME}:latest .


push: build
	docker push ${REGISTRY}/$(IMAGE_NAME):$(VERSION)
	docker push ${REGISTRY}/${IMAGE_NAME}:latest