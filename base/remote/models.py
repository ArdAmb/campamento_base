# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _
from telegram.chat import Chat

TYPE_PRIVATE = 0
TYPE_GROUP = 1
TYPE_SUPERGROUP = 2
TYPE_CHANNEL = 3

TYPE_CHAT = (
    (TYPE_PRIVATE, _('Privado')),
    (TYPE_GROUP, _('Grupo')),
    (TYPE_SUPERGROUP, _('Supergrupo')),
    (TYPE_CHANNEL, _('Canal')),
)


class RemoteChatManager(models.Manager):
    def by_chat(self, chat):
        """
        :param chat:
        :type chat: telegram.chat.Chat
        :return:
        :rtype: QuerySet
        """
        chat_type = None
        if chat.type == Chat.PRIVATE:
            chat_type = TYPE_PRIVATE
        elif chat.type == Chat.GROUP:
            chat_type = TYPE_GROUP
        elif chat.type == Chat.SUPERGROUP:
            chat_type = TYPE_SUPERGROUP
        elif chat.type == Chat.CHANNEL:
            chat_type = TYPE_CHANNEL
        return self.get_queryset().filter(chat_id=chat.id, chat_type=chat_type)

    def allowed(self, chat):
        """
        :param chat:
        :type chat: telegram.chat.Chat
        :return:
        :rtype: bool
        """
        return self.by_chat(chat).exists()


class RemoteChat(models.Model):
    name = models.CharField(max_length=512)
    chat_id = models.CharField(max_length=64)
    chat_type = models.IntegerField(choices=TYPE_CHAT, default=TYPE_PRIVATE)
    items_per_page = models.IntegerField(default=10)

    objects = RemoteChatManager()

    class Meta:
        unique_together = ('chat_id', 'chat_type')

    def __str__(self):
        return self.name

    def get_chat(self, **kwargs):
        """
        :param kwargs: Used to create the Telegram chat
        :return: Telegram chat
        :rtype: telegram.chat.Chat
        """
        chat_type = None
        if self.chat_type == TYPE_PRIVATE:
            chat_type = Chat.PRIVATE
        elif self.chat_type == TYPE_GROUP:
            chat_type = Chat.GROUP
        elif self.chat_type == TYPE_SUPERGROUP:
            chat_type = Chat.SUPERGROUP
        elif self.chat_type == TYPE_CHANNEL:
            chat_type = Chat.CHANNEL
        return Chat(self.chat_id, chat_type, **kwargs)
