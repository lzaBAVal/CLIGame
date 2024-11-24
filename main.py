# Игра в виде текстового RPG
# Events:
#   нашел врага
#   нашел предмет
#   попал в ловушку
#   попал на развилку (дать выбор куда идти)
#   нашел место отдыха

# Возможности использования
# Вывод информации о герое
# Вывод информации о враге
# Шаг вперед
# Выбор пути (налево, направо)


import random
from enum import Enum
from typing import Any

from utils import _input, _input_get_answer, custom_print


EVENTS = {
    'enemy': [
        {
            'name': 'Крыса',
            'description': 'Маленькое, не приятное существо.',
            'health': 10,
            'damage': 1,
            'armor': 0,
        },
        {
            'name': 'Огр',
            'description': 'Большой. Толстый. Пахнет плохо.',
            'health': 50,
            'damage': 7,
            'armor': 2,
        },
        {
            'name': 'Скелет',
            'description': 'Сбежал из кабинета учителя биологии.',
            'health': 25,
            'damage': 3,
            'armor': 1,
        },
    ],
    'trap': [
        {
            'name': 'Шипы',
            'damage': 2,
        },
        {
            'name': 'Ядовитый плющ',
            'damage': 4,
        }
    ],
    'rest_place': [
        {
            'name': 'Костер',
            'healing': 3,
        }
    ],
    'item': [
        {
            'name': 'Шлем',
            'description': 'Шлем',
            'damage': 0,
            'armor': 1,
        },
        {
            'name': 'Броня',
            'description': 'Броня',
            'damage': 0,
            'armor': 3,
        },
        {
            'name': 'Нож',
            'description': 'Нож',
            'damage': 3,
            'armor': 0,
        },
        {
            'name': 'Меч',
            'description': 'Меч',
            'damage': 5,
            'armor': 1,
        },
    ],
}
LEVELS = 40


class EventType(Enum):
    TRAP = 'Ловушка'
    ENEMY = 'Враг'
    ITEM = 'Вещь'
    REST_PLACE = 'Место отдыха'


class BaseObject:
    @classmethod
    def from_dict(cls, data: dict) -> 'Any':
        return cls(**data)

    def to_dict(self) -> dict:
        return self.__dict__


class Trap(BaseObject):
    def __init__(self, name: str, damage: int):
        self.name = name
        self.damage = damage


class RestPlace(BaseObject):
    def __init__(self, name: str, healing: int):
        self.name = name
        self.heailing = healing


class Item(BaseObject):
    def __init__(self, name: str, description: str, damage: int, armor: int):
        self.name = name
        self.description = description
        self.damage = damage
        self.armor = armor

    @property
    def info(self):
        return f'Урон: {self.damage}, Защита: {self.armor}'


class HealingItem(BaseObject):
    def __init__(self, name: str, description: str, heal: int):
        self.name = name
        self.description = description
        self.heal = heal


class Creature(BaseObject):
    def __init__(self, name: str, health: int, armor: int, damage: int):
        self.name = name
        self.current_health = health
        self.max_health = health
        self.base_health = health
        self.armor = armor
        self.base_damage = damage

    def take_damage(self, damage: int):
        """Принять урон от врага"""
        self.current_health -= damage - self.armor

    def take_heal(self, healing: int):
        self.current_health += healing

        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def is_alive(self) -> bool:
        return self.current_health > 0


class Enemy(Creature):
    def __init__(self, name: str, description: str, damage: int, health: int, armor: int):
        super().__init__(name, health, armor, damage)
        self.description = description

    def create(self) -> 'Enemy':
        return Enemy(self.name, self.description, self.base_damage, self.base_health, self.armor)


class Hero(Creature):
    def __init__(self, name: str, damage: int, health: int):
        super().__init__(name, health, 0, damage)
        self.backpack = Backpack()

    def add_backpack(self, item: Item):
        self.backpack.add_item(item)

    def drop_backpack(self, item: Item):
        self.backpack.drop_item(item)

    @property
    def damage(self):
        return self.base_damage + self.backpack.calculate_damage()

    def calculate_max_health(self):
        self.max_health = self.base_health + self.backpack.calculate_armor()

    @property
    def info(self) -> str:
        return (f'Имя: {self.name}\n'
            f'Здоровье: {self.current_health}/{self.max_health}\n')

    @property
    def backpack_info(self) -> str:
        return f'Вещи в рюкзаке: {self.backpack}'


class Backpack(BaseObject):
    def __init__(self):
        self.items: list[Item] = list()

    def __str__(self) -> str:
        return '\n'.join([f'{i.name}: {i.info}' for i in self.items])

    def add_item(self, item: Item):
        is_item_in_backpack = self._find_item(item.name)

        if not is_item_in_backpack:
            self.items.append(item)
            custom_print(f'Предмет {item.name} был помещен в рюкзак')
            return

        custom_print(f'Предмет {item.name} уже есть в рюкзаке, зачем вам второй?')

    def drop_item(self, item: Item):
        item = self._find_item(item.name)

        if item:
            self.items.remove(item)
            custom_print(f'Предмет {item.name} выброшен на землю')
            return

        custom_print(f'Предмета {item.name} нет в рюкзаке')

    def _find_item(self, name: str):
        for item in self.items:
            if item.name == name:
                return item

    def calculate_damage(self) -> int:
        return sum([i.damage for i in self.items])

    def calculate_armor(self) -> int:
        return sum([i.armor for i in self.items])


class Battle:
    def __init__(self, hero: Hero, enemy: Enemy):
        self.hero = hero
        self.enemy = enemy

    def start(self):
        while True:
            input('Нажмите ENTER что начать раунд битвы...')

            custom_print(f'{self.hero.name} атакует {self.enemy.name} и наносит {self.hero.damage}')
            self.enemy.take_damage(self.hero.damage)
            custom_print(f'Вы нанесли {self.enemy.name} урон - {self.hero.damage}.')
            custom_print(f'Очков здоровья у {self.enemy.name} - {self.enemy.max_health}/{self.enemy.current_health}')

            if not self.enemy.is_alive():
                custom_print(f'Поздравляю, {self.enemy.name} повержен!')
                # self.hero.current_health = self.hero.max_health
                # custom_print(f'Ваше здоровье восполнено - {self.hero.current_health}/{self.hero.current_health}')
                break

            self.hero.take_damage(self.enemy.base_damage)
            custom_print(f'Вам нанесли {self.enemy.base_damage} урона.')
            custom_print(f'У вас {self.hero.max_health}/{self.hero.current_health} очков здоровья')

            if not self.hero.is_alive():
                custom_print(f'К сожалению вы проиграли битву. {self.enemy.name} убил вас!')
                exit('Конец игры')


class Event:
    def __init__(self, name: str, type: EventType):
        self.name = name
        self.type = type

    def __str__(self) -> str:
        return self.name

    def apply(self, hero: Hero):
        pass


class EventFoundItem(Event):
    def __init__(self, event_object: Item):
        super().__init__('Найден предмет', EventType.ITEM)
        self.item: Item = event_object

    def apply(self, hero: Hero):
        custom_print(f'Вы нашли предмет - {self.item.name}')
        custom_print(f'Его характеристики \n{self.item.info}')
        custom_print(f'Хотите ли вы взять предмет - {self.item.name}?')

        answer = _input_get_answer()
        if answer:
            custom_print('Предмет взят')
            hero.add_backpack(self.item)
        else:
            custom_print('Предмет остался лежат на своем месте')


class EventFoundEnemy(Event):
    def __init__(self, event_object: Enemy):
        super().__init__('Столкновение с врагом', EventType.ENEMY)
        self.enemy = event_object

    def apply(self, hero: Hero):
        custom_print(f'Начало битвы с {self.enemy.name}')
        Battle(hero, self.enemy).start()


class EventFoundRestPlace(Event):
    def __init__(self, event_object: RestPlace):
        super().__init__('Вы нашли место чтобы отдохнуть', EventType.REST_PLACE)
        self.rest_place = event_object

    def apply(self, hero: Hero):
        hero.take_heal(self.rest_place.heailing)
        custom_print(f'Вы примостились к объекту {self.rest_place.name}. Восполнено - {self.rest_place.heailing} очков здоровья')
        custom_print(f'У вас {hero.max_health}/{hero.current_health} очков здоровья')


class EventFoundTrap(Event):
    def __init__(self, event_object: Trap):
        super().__init__('Вы напоролись на ловушку', EventType.TRAP)
        self.trap = event_object

    def apply(self, hero: Hero):
        hero.take_damage(self.trap.damage)

        if not hero.is_alive():
            custom_print('К сожалению вы погибли от ловушки')
            exit('Конец игры')


class Game:
    def __init__(
            self,
            levels: int,
            items: list[Item],
            enemies: list[Enemy],
            traps: list[Trap],
            rest_places: list[RestPlace],
    ):
        self.levels = levels
        self.hero = Hero('Странник', 10, 100)

        events_items = [EventFoundItem(i) for i in items]
        events_enemies = [EventFoundEnemy(i.create()) for i in enemies]
        events_traps = [EventFoundTrap(i) for i in traps]
        events_rest_places = [EventFoundRestPlace(i) for i in rest_places]

        self.world = World.create(
            levels=levels,
            items=events_items,
            enemies=events_enemies,
            traps=events_traps,
            rest_places=events_rest_places,
        )

    def step(self):
        pass

    def _greeting(self):
        custom_print('Добро пожаловать в этот мир странник. Как тебя зовут?')
        name = _input('Введите свое имя: ')
        self.hero.name = name
        custom_print(f'Воинственное имя, {self.hero.name}')
        custom_print(f'Сейчас начинается ваш путь, впереди вас ждет {self.levels} уровней. '
                     f'Да начнется ваше приключение')

    @staticmethod
    def _input_palyer_action() -> int:
        while True:
            text = _input('1. Показать характеристики героя\n'
                          '2. Показать что лежит в рюкзаке\n'
                          '3. Двигаться дальше\n\n')

            if text.isdigit() in [1, 2, 3]:
                return int(text)

    def player_actions(self):
        while True:
            action = self._input_palyer_action()

            if action == 1:
                custom_print(self.hero.info)
            elif action == 2:
                custom_print(self.hero.backpack_info)
            elif action == 3:
                break

    def _run_levels(self):
        for level in range(self.levels):
            level += 1
            event = self.world.pop()
            custom_print(f'Начинается ваш {level} день приключений. Сегодня вас ждет событие {event}')

            self.player_actions()

            event.apply(self.hero)

    def _end(self):
        custom_print(f'Ого! Вы прошли все {self.levels} уровней! Вы дошли до конца! Поздравляю')
        exit('Конец игры')

    def start(self):
        self._greeting()
        self._run_levels()
        self._end()


class World:
    def __init__(self):
        self.events = None

    @classmethod
    def create(cls, levels: int, items: list[EventFoundItem], enemies: list[EventFoundEnemy],
               traps: list[EventFoundTrap], rest_places: list[EventFoundRestPlace]) -> 'World':
        events = list()

        for level in range(levels):
            objects = random.choice([items, enemies, traps, rest_places])
            object_ = random.choice(objects)
            events.append(object_)

        world = World()
        world.events = events

        return world

    def pop(self) -> Event:
        return self.events.pop()


enemies = [Enemy.from_dict(e) for e in EVENTS['enemy']]
traps = [Trap.from_dict(e) for e in EVENTS['trap']]
rest_places = [RestPlace.from_dict(e) for e in EVENTS['rest_place']]
items = [Item.from_dict(e) for e in EVENTS['item']]

game = Game(
    levels=LEVELS,
    items=items,
    enemies=enemies,
    traps=traps,
    rest_places=rest_places,
)
game.start()
