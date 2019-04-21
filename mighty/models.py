from django.db import models as django_models
from model_utils.models import *
from model_utils import *
from .utils import *


class Base(TimeFramedModel, StatusModel, TimeStampedModel, SoftDeletableModel):
    class Meta:
        abstract = True


class Turn(Base):
    tracker = FieldTracker()

    STATUS = Choices('ready', 'thinking', 'over',)

    position_list = list(range(NumUtils.players_number))
    POSITION_CHOICES = Choices(*position_list)
    position = django_models.IntegerField(default=0, choices=POSITION_CHOICES, db_index=True)

    turn_number_list = list(range(NumUtils.players_number))
    NUMBER_CHOICES = Choices(*turn_number_list)
    number = django_models.IntegerField(default=0, choices=NUMBER_CHOICES, null=True, db_index=True)

    cycle = django_models.ForeignKey('Cycle', on_delete=django_models.CASCADE, null=True, db_index=True)
    player = django_models.ForeignKey('Player', on_delete=django_models.CASCADE, null=True, db_index=True)
    card = django_models.ForeignKey('Card', on_delete=django_models.CASCADE, null=True, db_index=True)


class Card(Base):
    tracker = FieldTracker()

    STATUS = Choices('on_hand_declarer', 'flipped_by_declarer', 'score', 'opened', 'on_hand', 'flipped', 'flipped_but_score',)

    card_value_list = ['A','K','Q','J','10','9','8','7','6','5','4','3','2',]
    special_value_list = ['Mighty', 'Joker']
    CARD_VALUE_CHOICES = Choices(*(card_value_list + special_value_list))
    value = django_models.CharField(max_length=10, choices=CARD_VALUE_CHOICES, db_index=True)

    card_int_value_list = [14,13,12,11,10,9,8,7,6,5,4,3,2,]
    special_int_value_list = [16,15,1]
    CARD_INT_VALUE_CHOICES = Choices(*(card_int_value_list + special_int_value_list))
    int_value = django_models.IntegerField(default=0, choices=CARD_INT_VALUE_CHOICES, db_index=True)

    card_value_dict = dict(zip(card_int_value_list, card_value_list))

    card_suit_list = ['spade', 'diamond', 'clover', 'heart',]
    special_suit_list = ['Joker']
    CARD_SUIT_CHOICES = Choices(*(card_suit_list + special_suit_list))
    suit = django_models.CharField(max_length=10, choices=CARD_SUIT_CHOICES, db_index=True)

    player = django_models.ForeignKey('Player', on_delete=django_models.CASCADE, null=True, db_index=True)
    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True, db_index=True)

    is_mighty = django_models.BooleanField(default=False, db_index=True)
    is_joker = django_models.BooleanField(default=False, db_index=True)
    is_joker_call = django_models.BooleanField(default=False, db_index=True)
    is_kiruda = django_models.BooleanField(default=False, db_index=True)

    def player_setter(self, player):
        if player is None:
            return 'Error'

        self.player = player
        self.save()

        return self


class Player(Base):
    tracker = FieldTracker()
    STATUS = Choices('in_election', 'declarer', 'friend', 'defenders', 'finished',)
    name = django_models.CharField(max_length=200, default='bot', db_index=True)

    POSITION_CHOICES = Choices(*Turn.position_list)
    position = django_models.IntegerField(default=0, choices=POSITION_CHOICES, db_index=True)

    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True, db_index=True)

    def cards_setter(self, card_id_list):
        if self.status != self.STATUS.in_election:
            return 'Error'

        [Card.objects.get(pk=card_id).player_setter(self) for card_id in card_id_list]

        return self


class Declaration(Base):
    tracker = FieldTracker()
    STATUS = Choices('pass', 'declaration',)

    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True, db_index=True)
    player = django_models.ForeignKey('Player', on_delete=django_models.CASCADE, null=True, db_index=True)

    declaration_suit_list = ['nokiru'] + Card.card_suit_list
    DECLARATION_SUIT_CHOICES = Choices(*declaration_suit_list)
    suit = django_models.CharField(max_length=10, choices=DECLARATION_SUIT_CHOICES, db_index=True)

    declaration_value_list = [20,19,18,17,16,15,14,13,]
    DECLARATION_VALUE_CHOICES = Choices(*([12,] + declaration_value_list))
    value = django_models.IntegerField(default=13, choices=DECLARATION_VALUE_CHOICES, db_index=True)

    is_successful = django_models.BooleanField(default=False, db_index=True)


class Cycle(Base):
    tracker = FieldTracker()

    STATUS = Choices('s0','s1','s2','s3','s4','s5','over',)

    POSITION_CHOICES = Choices(*Turn.position_list)
    first = django_models.IntegerField(default=0, choices=POSITION_CHOICES, null=True, db_index=True)

    cycle_number_list = list(range(53 // NumUtils.players_number))
    NUMBER_CHOICES = Choices(*cycle_number_list)
    number = django_models.IntegerField(default=0, choices=NUMBER_CHOICES, db_index=True)

    game = django_models.ForeignKey('Game', on_delete=django_models.CASCADE, null=True, db_index=True)


class Game(Base):
    tracker = FieldTracker()

    STATUS = Choices('in_election', 'in_declarer', 'in_cycle', 'finished',)

    @classmethod
    def start(cls, user_list=None):
        if user_list is None or len(user_list) != 5:
            return 'Error'

        cls_instance = cls()
        cls_instance.save()

        cls_instance.create_data(user_list)

        cls_instance.shuffle_cards()

        return cls_instance

    def create_data(self, user_list=None):
        if user_list is None or len(user_list) != 5:
            return 'Error'
        self.create_players(user_list)
        self.create_cards()
        self.create_cycles()
        self.create_turns()

    def create_players(self, user_list=None):
        if user_list is None or len(user_list) != 5:
            return 'Error'
        [Player.objects.create(name=name, position=index, game=self) for index, name in enumerate(user_list)]

        return self.player_set.all()

    def create_cards(self):
        [Card.objects.create(value=value, int_value=int_value, suit=suit, game=self) for int_value, value in Card.card_value_dict.items() for suit in Card.card_suit_list]
        Card.objects.create(value=Card.CARD_VALUE_CHOICES.Joker, int_value=15, suit=Card.CARD_SUIT_CHOICES.Joker, game=self, is_joker=True)

        return self.card_set.all()

    def create_cycles(self):
        [Cycle.objects.create(number=number, game=self) for number in Cycle.cycle_number_list]

        return self.cycle_set.all()

    def create_turns(self):
        turn_list = [Turn.objects.create(position=position, player=Player.objects.get(game=self, position=position), cycle=Cycle.objects.get(game=self, number=number)) for position in Turn.position_list for number in Cycle.cycle_number_list]

        return Turn.objects.filter(id__in=[turn.id for turn in turn_list])

    @property
    def kiruda(self):
        successful_declaration = self.declaration_set.filter(is_successful=True)
        if successful_declaration.count() == 1:
            return successful_declaration.first().suit

    def shuffle_cards_getter(self):
        if self.status != self.STATUS.in_election:
            return 'Error'

        arr = list(self.card_set.values_list('id',flat=True))
        np.random.shuffle(arr)
        arr_only_in_election = np.array(arr[:50]).reshape((5,10))

        return [list(a) for a in arr_only_in_election]

    def shuffle_cards_setter(self, list_of_card_id_list):
        if self.status != self.STATUS.in_election:
            return 'Error'

        [self.player_set.get(position=position).cards_setter(list_of_card_id_list[position]) for position in range(NumUtils.players_number)]

        return self

    def shuffle_cards(self):
        lst = self.shuffle_cards_getter()
        self.shuffle_cards_setter(lst)

        return self

