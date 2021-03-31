FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

EXPOSE 8000

COPY ./ws-slack /app
COPY ./ws-sdk/dist/*.whl .

RUN pip3 install -r ./requirements.txt
#RUN pip3 install git+https://github.com/whitesource-ps/ws-sdk.git@internal#egg=ws_sdk
#RUN pip install --extra-index-url=https://github.com/whitesource-ps/ws-sdk
RUN pip3 install *.whl

WORKDIR /app/ws-slack
CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]
