FROM public.ecr.aws/lambda/python:3.10
WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY transform.py .
COPY utilities.py .

CMD [ "transform.handler" ] 