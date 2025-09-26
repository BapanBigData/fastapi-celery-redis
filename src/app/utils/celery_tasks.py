from celery import Celery
from src.app.utils.mail import mail, create_message
from asgiref.sync import async_to_sync

app = Celery()

app.config_from_object("src.app.utils.config")


@app.task()
def send_email(recipients: list[str], subject: str, body: str):

    message = create_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)

    print("Email sent")


# To Run Celery: `celery -A src.app.utils.celery_tasks worker -P solo -l info -E` [On windows]
# Flower: `celery -A src.app.utils.celery_tasks flower --port=5555`
