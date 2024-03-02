FROM amazonlinux:2 as builder
WORKDIR /app
RUN yum -y install python3 \
  python3-pip
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --target=/app --no-cache-dir -r requirements.txt

FROM public.ecr.aws/lambda/python:3.11 as runtime
WORKDIR /var/task
COPY --from=builder /app .
COPY src/ ./src
COPY lambda_function.py .
CMD ["lambda_function.lambda_handler"]