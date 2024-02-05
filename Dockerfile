FROM public.ecr.aws/lambda/python:3.11
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir sagemaker
COPY lambda_function.py /var/task/
CMD ["lambda_function.lambda_handler"]
