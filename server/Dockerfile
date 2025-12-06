FROM python:3.12.0-slim-bookworm
ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1
ENV APP=/app

WORKDIR $APP

COPY requirements.txt $APP
RUN pip3 install -r requirements.txt

COPY . $APP

RUN chmod -R 777 /app

RUN python manage.py collectstatic --noinput
EXPOSE 8000

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/bin/bash","/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]
