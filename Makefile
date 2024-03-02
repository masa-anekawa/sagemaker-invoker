# AWS ECR Makefile Boilerplate

include .env
export $(shell sed 's/=.*//' .env)

# 設定項目
TAG := $(shell git rev-parse HEAD)

# ECR リポジトリのURLを取得
REPO_URL := $(shell aws ecr describe-repositories --repository-names $(REPO_NAME) --profile $(AWS_PROFILE) --region $(AWS_REGION) --query 'repositories[0].repositoryUri' --output text)

# Install python dependencies via poetry
.PHONY: install
install:
	poetry install --no-root

.PHONY: test
test: install
	poetry run python -m pytest

# requirements.txtを生成
requirements.txt: pyproject.toml
	poetry export -f requirements.txt --output requirements.txt

# Dockerイメージをビルド
.PHONY: build
build: test requirements.txt
	docker build --platform linux/amd64 -t $(IMAGE_NAME):$(TAG) .

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
