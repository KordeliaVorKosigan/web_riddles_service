FROM python:3.10

RUN python -m pip install \
    requests \
    psycopg2 \
    fastapi \ 
    uvicorn \
    sqlalchemy \
    fastapi.responses

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]









