FROM public.ecr.aws/lambda/python:3.10
WORKDIR ${LAMBDA_TASK_ROOT}
COPY . .
RUN pip3 install -r requirements.txt
CMD [ "transform.handler" ] 