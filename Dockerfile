FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

EXPOSE 8000

COPY ./ws-slack /app
COPY ./ws-sdk/dist/*.whl .

RUN pip3 install -r ./requirements.txt
RUN pip3 install *.whl

WORKDIR /app/ws-slack
CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]
