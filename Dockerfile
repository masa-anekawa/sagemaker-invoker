FROM public.ecr.aws/lambda/python:3.11 as runtime
WORKDIR /var/task
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/ ./src
COPY lambda_function.py .
CMD ["lambda_function.lambda_handler"]