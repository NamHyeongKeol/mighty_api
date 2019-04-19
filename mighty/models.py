from django.db import models
from model_utils.models import *
from model_utils import Choices


class Game(TimeFramedModel, StatusModel, TimeStampedModel, SoftDeletableModel):
    STATUS = Choices('ongoing', 'finished')

