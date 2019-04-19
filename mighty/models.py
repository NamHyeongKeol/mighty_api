from django.db import models
from model_utils.models import *
from model_utils import Choices


class Base(TimeFramedModel, StatusModel, TimeStampedModel, SoftDeletableModel):
    class Meta:
        abstract = True


class Game(Base):
    STATUS = Choices('ongoing', 'finished')


class Player(Base):
    STATUS = Choices('ongoing', 'finished')

