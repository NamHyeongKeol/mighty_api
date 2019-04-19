from django.db import models as django_models
from model_utils.models import *
from model_utils import *


class Base(TimeFramedModel, StatusModel, TimeStampedModel, SoftDeletableModel):
    class Meta:
        abstract = True


class Game(Base):
    tracker = FieldTracker()

    STATUS = Choices('ongoing', 'finished',)


class Player(Base):
    STATUS = Choices('in_election', 'declarer', 'friend', 'defenders', 'finished',)
    name = django_models.CharField(max_length=200, default='bot')

    POSITION_CHOICES = Choices(1,2,3,4,5,)
    position = django_models.IntegerField(default=0, choices=POSITION_CHOICES) 

    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True)


class Card(Base):
    tracker = FieldTracker()

    STATUS = Choices('on_hand_declarer', 'flipped_by_declarer', 'score', 'opened', 'on_hand', 'flipped', 'flipped_but_score',)

    CARD_VALUE_CHOICES = Choices('A','K','Q','J','10','9','8','7','6','5','4','3','2',)
    value = django_models.CharField(max_length=1, choices=CARD_VALUE_CHOICES)

    CARD_INT_VALUE_CHOICES = Choices(14,13,12,11,10,9,8,7,6,5,4,3,2,)
    int_value = django_models.IntegerField(default=0, choices=CARD_INT_VALUE_CHOICES)

    CARD_SUIT_CHOICES = Choices('spade', 'diamond', 'clover', 'heart',)
    suit = django_models.IntegerField(default=0, choices=CARD_SUIT_CHOICES)

    player = django_models.ForeignKey('Player', on_delete=django_models.CASCADE, null=True)
    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True)


class Cycle(Base):
    tracker = FieldTracker()

    STATUS = Choices('s0','s1','s2','s3','s4','s5','over',)

    POSITION_CHOICES = Choices(1,2,3,4,5,)
    first = django_models.IntegerField(default=0, choices=POSITION_CHOICES) 

    NUMBER_CHOICES = Choices(1,2,3,4,5,6,7,8,9,10,)
    number = django_models.IntegerField(default=0, choices=NUMBER_CHOICES) 
 
    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True)


class Turn(Base):
    tracker = FieldTracker()

    STATUS = Choices('ready', 'thinking', 'over',)

    POSITION_CHOICES = Choices(1,2,3,4,5,)
    position = django_models.IntegerField(default=0, choices=POSITION_CHOICES) 

    cycle = django_models.ForeignKey('Cycle', on_delete=django_models.CASCADE, null=True)
    player = django_models.ForeignKey('Player', on_delete=django_models.CASCADE, null=True)
    card = django_models.ForeignKey('Card', on_delete=django_models.CASCADE, null=True)

