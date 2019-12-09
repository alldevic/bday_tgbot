from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)
from telegram.utils.request import Request

from bday_admin.models import Message, Profile

import datetime
import telegram

def log_errors(f):

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        },
        is_sub=False
    )
    m = Message(
        profile=p,
        text=text,
    )
    m.save()

    reply_text = f'Ваш ID = {chat_id}\nMessage ID = {m.pk}\n{text}'
    update.message.reply_text(
        text=reply_text,
    )


@log_errors
def check_bdays(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        },
        is_sub=False
    )
    count = Message.objects.filter(profile=p).count()

    update.message.reply_text(
        text=f'У вас {count} сообщений',
    )


@log_errors
def go_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )


    # Оформить флаг подписки, добавить handler?
    p.is_sub = True
    p.save()

    update.message.reply_text(
        text='Вы подписаны',
    )


@log_errors
def go_stop(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )

    # УБрать флаг подписки, отвязать hsndler?
    p.is_sub = False
    p.save()


    update.message.reply_text(
        text='Подписка отменена',
    )



@log_errors
def check_bdays(context: telegram.ext.CallbackContext):
    subs = Profile.objects.filter(is_sub=True)

    for sub in subs:
         context.bot.send_message(chat_id=sub.external_id, 
                             text='Hello, world!')


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TG_TOKEN,
            base_url=settings.TG_PROXY_URL,
        )
        print(bot.get_me())

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(message_handler)

        message_handler2 = CommandHandler('check', check_bdays)
        updater.dispatcher.add_handler(message_handler2)

        message_handler3 = CommandHandler('start', go_start)
        updater.dispatcher.add_handler(message_handler3)

        message_handler4 = CommandHandler('stop', go_stop)
        updater.dispatcher.add_handler(message_handler4)
        
        updater.job_queue.run_daily(check_bdays,
                                    datetime.time(hour=2, minute=45))

        updater.start_polling()
        updater.idle()