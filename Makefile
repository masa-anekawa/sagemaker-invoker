# AWS ECR Makefile Boilerplate

# 設定項目
AWS_PROFILE := default
AWS_REGION := ap-northeast-1
REPO_NAME := yui-gpt-sagemaker-invoker
IMAGE_NAME := yui-gpt-sagemaker-invoker
TAG := $(shell tar c lambda_function.py test Dockerfile Pipfile.lock | md5sum | awk '{print $$1}')

# ECR リポジトリのURLを取得
REPO_URL := $(shell aws ecr describe-repositories --repository-names $(REPO_NAME) --profile $(AWS_PROFILE) --region $(AWS_REGION) --query 'repositories[0].repositoryUri' --output text)

# Dockerイメージをビルド
build:
# build: test
	docker build -t $(IMAGE_NAME):$(TAG) .

# AWS ECRへのログイン
login:
	aws ecr get-login-password --region $(AWS_REGION) --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(REPO_URL)

# DockerイメージをECRへプッシュ
push: build login
	docker tag $(IMAGE_NAME):$(TAG) $(REPO_URL):$(TAG)
	docker push $(REPO_URL):$(TAG)

# ローカルのDockerイメージを削除
clean:
	docker rmi -f $(IMAGE_NAME):$(TAG)
	docker rmi -f $(REPO_URL):$(TAG)

test:
	pipenv run python -m pytest

.PHONY: build runlocal login push clean test
