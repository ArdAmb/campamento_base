# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
)
from telegram.parsemode import ParseMode

from base.models import Seta, Sensor, ValueSensorSeta
from base.remote.models import RemoteChat

logger = logging.getLogger('remote_control')

PAG_SIZE = 10


class Command(BaseCommand):
    help = _('Allow consume data using telegram')
    stack_keypads = {}

    def add_arguments(self, parser):
        parser.add_argument('token', nargs='?', type=str, default='')

    def handle(self, *args, **options):
        token = options['token']
        if not token:
            if hasattr(settings, 'TELEGRAM_TOKEN') and settings.TELEGRAM_TOKEN:
                token = settings.TELEGRAM_TOKEN
            else:
                raise CommandError('Token required on settings or as parameter')

        updater = Updater(token)

        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start_callback))
        dp.add_handler(CommandHandler("help", self.help_callback))
        dp.add_handler(CommandHandler("setas", self.list_callback))
        dp.add_handler(CommandHandler("sensors", self.list_callback))
        dp.add_handler(CallbackQueryHandler(self.keypad_callback))
        dp.add_error_handler(self.error_callback)

        updater.start_polling()
        self.stdout.write("Started\n")
        logging.info("Started")
        updater.idle()

    def error_callback(self, bot, update, error):
        logger.exception(error)
        try:
            self.stderr.write(str(error))
            self.stderr.write("\n")
        except:
            pass

    def start_callback(self, bot, update):
        user = update.effective_user
        chat = update.effective_chat

        msg = 'Start for {name}'.format(name=user.first_name)
        if logger.isEnabledFor(logging.INFO):
            logger.info(msg)
        self.stdout.write(msg)
        self.stdout.write("\n")

        message = _('Hi *{name}* this chat is not registered\n').format(name=user.first_name)
        message += _('Chat "{type}" code: "*{id}*"\n\n').format(id=chat.id, type=chat.type)
        if RemoteChat.objects.allowed(chat):
            message = _('Hi *{name}* you are registered').format(name=user.first_name)
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    def help_callback(self, bot, update):
        user = update.effective_user
        msg = 'Help for {name}'.format(name=user.first_name)
        if logger.isEnabledFor(logging.INFO):
            logger.info(msg)
        self.stdout.write(msg)
        self.stdout.write("\n")
        message = _("/help -> _This message_\n")
        message += _("/start -> _Check if the chat are registered_\n")
        message += _("/setas -> _KeyPad for get data from some seta_\n")
        message += _("/sensors -> _KeyPad for get data from all sensors_")
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    def list_callback(self, bot, update):
        chat = update.effective_chat
        command = update.effective_message.text
        user = update.effective_user
        msg = 'List {cmd} for {name}'.format(cmd=command, name=user.first_name)
        if logger.isEnabledFor(logging.INFO):
            logger.info(msg)
        self.stdout.write(msg)
        self.stdout.write("\n")
        if not RemoteChat.objects.allowed(chat):
            bot.send_message(chat.id, _('Not registered'))
        else:
            if command.startswith('/seta'):
                clase = 'seta'
            elif command.startswith('/sensor'):
                clase = 'sensor'
            else:
                msg = 'Invalid command {command}'.format(command=command)
                if logger.isEnabledFor(logging.ERROR):
                    logger.error(msg)
                self.stderr.write(msg)
                self.stderr.write("\n")
                return

            if str(chat.id) in self.stack_keypads:
                message = self.stack_keypads[str(chat.id)]
                bot.delete_message(chat.id, message.message_id)
                del self.stack_keypads[str(chat.id)]
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('Clean old message')

            self.stack_keypads[str(chat.id)] = bot.send_message(
                chat.id,
                _('Choose option:'),
                reply_markup=self.get_pad(clase, 0, chat)
            )

    def keypad_callback(self, bot, update):
        chat = update.effective_chat
        if not RemoteChat.objects.allowed(chat):
            return
        message = ''
        query = update.callback_query.data
        params = query.count(':')
        if params == 1:
            clase, pk = query.split(':', 1)
            data = []
            if clase == 'seta':
                seta = Seta.objects.get(pk=pk)
                message = _('No data available for {name}').format(name=seta.name)
                full_data = ValueSensorSeta.objects.filter(seta=seta)
                try:
                    data = list(full_data.distinct('sensor_id'))
                except NotImplementedError:
                    sensor_ids = []
                    iterator = full_data.exclude(sensor_id__in=sensor_ids)
                    while iterator.exists():
                        item = iterator.first()
                        sensor_ids.append(item.sensor_id)
                        data.append(item)
                        iterator = full_data.exclude(sensor_id__in=sensor_ids)
            elif clase == 'sensor':
                sensor = Sensor.objects.get(pk=pk)
                message = _('No data available for {name}').format(name=sensor.name)
                full_data = ValueSensorSeta.objects.filter(sensor=sensor)
                try:
                    data = list(full_data.distinct('seta_id'))
                except NotImplementedError:
                    seta_ids = []
                    iterator = full_data.exclude(seta_id__in=seta_ids)
                    while iterator.exists():
                        item = iterator.first()
                        seta_ids.append(item.seta_id)
                        data.append(item)
                        iterator = full_data.exclude(seta_id__in=seta_ids)

            if data:
                message = ''
            for values in data:
                message += _('{date}: {seta} {sensor}={value}\n').format(
                    date=values.date.strftime('%Y/%m/%d %H-%M-%S'),
                    seta=values.seta.name,
                    sensor=values.sensor.name,
                    value=values.value
                )
        elif params == 2:
            if str(chat.id) in self.stack_keypads:
                msg = self.stack_keypads[str(chat.id)]
            else:
                msg = update.effective_message
            clase, action, page = query.split(':', 2)
            if action not in ['cancel', 'prev', 'next']:
                return
            elif action == 'cancel':
                bot.delete_message(chat.id, msg.message_id)
                if str(chat.id) in self.stack_keypads:
                    del self.stack_keypads[str(chat.id)]
                return
            msg.edit_reply_markup(reply_markup=self.get_pad(clase, int(page), chat))

        if message:
            logger.info(message)
            self.stdout.write(message)
            self.stdout.write("\n")
            bot.send_message(chat.id, message)

    def get_pad(self, clase, page, chat):
        button_list = []
        if RemoteChat.objects.by_chat(chat).count() != 1:
            return
        remote_chat = RemoteChat.objects.by_chat(chat).get()
        pad_size = remote_chat.items_per_page
        init = page * pad_size
        end = init + pad_size

        if clase == 'seta':
            queryset = Seta.objects.all()[init:end]
            total = Seta.objects.count()
        elif clase == 'sensor':
            queryset = Sensor.objects.all()[init:end]
            total = Sensor.objects.count()
        else:
            return
        for item in queryset:
            button_list.append([
                InlineKeyboardButton(
                    item.name,
                    callback_data='{clase}:{pk}'.format(
                        clase=clase,
                        pk=item.pk
                    )
                )
            ])
        pags = []
        page_actions = False
        if page > 0:
            pags.append(InlineKeyboardButton(
                _('<<'),
                callback_data='{clase}:prev:{page}'.format(clase=clase, page=page - 1)
            ))
            page_actions = True
        else:
            pags.append(InlineKeyboardButton(' ', callback_data='disable'))

        if total > end:
            pags.append(InlineKeyboardButton(
                _('>>'),
                callback_data='{clase}:next:{page}'.format(clase=clase, page=page + 1)
            ))
            page_actions = True
        else:
            pags.append(InlineKeyboardButton(' ', callback_data='disable'))
        if page_actions:
            button_list.append(pags)

        button_list.append([
            InlineKeyboardButton(_('cancel'), callback_data='{clase}:cancel:'.format(clase=clase)),
        ])
        return InlineKeyboardMarkup(button_list)
