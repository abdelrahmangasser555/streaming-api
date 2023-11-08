FROM public.ecr.aws/docker/library/python:3.12.0-slim-bullseye
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.7.1 /lambda-adapter /opt/extensions/lambda-adapter

ARG VAR1
ARG VAR2

ENV OPENAI_API_KEY=$VAR1
ENV PINECONE_API_KEY=$VAR2
ENV AWS_LWA_INVOKE_MODE=response_stream

WORKDIR /app
ADD . .

RUN pip install langchain openai tiktoken fastapi pinecone-client uvicorn boto3

# run server
CMD ["python", "server_fast_api.py"]