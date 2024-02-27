# AWS ECR Makefile Boilerplate

include .env
export $(shell sed 's/=.*//' .env)

# 設定項目
TAG := $(shell git rev-parse HEAD)

# ECR リポジトリのURLを取得
REPO_URL := $(shell aws ecr describe-repositories --repository-names $(REPO_NAME) --profile $(AWS_PROFILE) --region $(AWS_REGION) --query 'repositories[0].repositoryUri' --output text)

# Dockerイメージをビルド
.PHONY: build
build: test
	docker build -t $(IMAGE_NAME):$(TAG) .

# AWS ECRへのログイン
.PHONY: login
login:
	aws ecr get-login-password --region $(AWS_REGION) --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(REPO_URL)

# DockerイメージをECRへプッシュ
.PHONY: push
push: build login
	docker tag $(IMAGE_NAME):$(TAG) $(REPO_URL):$(TAG)
	docker push $(REPO_URL):$(TAG)

# ローカルのDockerイメージを削除
.PHONY: clean
clean:
	docker rmi -f $(IMAGE_NAME):$(TAG)
	docker rmi -f $(REPO_URL):$(TAG)

.PHONY: test
test:
	pipenv run python -m pytest
