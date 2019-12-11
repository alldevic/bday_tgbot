from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)
from telegram.utils.request import Request

from bday_admin.models import Message, Profile
from bday.models import Bday
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
        }
    )
    
    if p.is_sub:
        cur_month = datetime.datetime.now().month
        cur_day = datetime.datetime.now().day
        bdays = Bday.objects.filter(bday__day=cur_day, bday__month=cur_month)

        str = ""
        if len(bdays) == 0:
            str = "Сегодня никто не празднует день рождения"
        else:
            for x in bdays:
                str += f"Сегодня день рожкдения праднует {x.man}\n"
    
        update.message.reply_text(
            text=str,
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
def ch_bdays(context: telegram.ext.CallbackContext):
    subs = Profile.objects.filter(is_sub=True)
    cur_month = datetime.datetime.now().month
    cur_day = datetime.datetime.now().day
    bdays = Bday.objects.filter(bday__day=cur_day, bday__month=cur_month)

    str = ""
    if len(bdays) == 0:
        str = "Сегодня никто не празднует день рождения"
    else:
        for x in bdays:
            str += f"Сегодня день рожкдения праднует {x.man}\n"

    for sub in subs:
         context.bot.send_message(chat_id=sub.external_id, 
                             text=str)


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
        
        updater.job_queue.run_daily(ch_bdays,
                                    datetime.time(hour=settings.TG_HOUR, minute=settings.TG_MINUTE))

        updater.start_polling()
        updater.idle()