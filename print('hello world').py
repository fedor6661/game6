import random


MAX_HEALTH = 100
PLAYER_DAMAGE = {
    "1": ("Джеб", 4),
    "2": ("Хук", 6),
    "3": ("Апперкот", 8),
}
ENEMY_DAMAGE = {
    "Лёгкий удар": 3,
    "Средний удар": 5,
    "Сильный удар": 7,
}


def print_rules():
    """Печатает правила игры."""
    print("=== Игра про бокс ===")
    print("Ты выходишь на ринг против компьютерного бойца.")
    print("Каждый раунд ты выбираешь действие:")
    print("1 - Джеб (точный, слабее)")
    print("2 - Хук (сбалансированный)")
    print("3 - Апперкот (сильный, но рискованный)")
    print("4 - Блок (урон в этом раунде снижается вдвое)")
    print("Побеждает тот, кто первым обнулит здоровье соперника.")
    print("-" * 36)


def ask_player_action():
    
    while True:
        print("\nВыбери действие: 1) Джеб  2) Хук  3) Апперкот  4) Блок")
        action = input("Твой выбор: ").strip()
        if action in ("1", "2", "3", "4"):
            return action
        print("Некорректный ввод. Введи 1, 2, 3 или 4.")


def enemy_action():
    """Случайно выбирает действие соперника."""
    actions = list(ENEMY_DAMAGE.keys()) + ["Блок"]
    return random.choice(actions)


def process_round(player_action, enemy_move):
    
    player_damage = 0
    enemy_damage = 0

    if player_action in PLAYER_DAMAGE:
        _, dmg = PLAYER_DAMAGE[player_action]
        player_damage = dmg

    if enemy_move in ENEMY_DAMAGE:
        enemy_damage = ENEMY_DAMAGE[enemy_move]

    if player_action == "4":
        enemy_damage = enemy_damage // 2
    if enemy_move == "Блок":
        player_damage = player_damage // 2

    return player_damage, enemy_damage


def print_round_result(round_number, player_action, enemy_move, player_damage, enemy_damage):
    """Печатает итоги раунда."""
    print("\nРаунд {}:".format(round_number))
    if player_action == "4":
        print("Ты выбрал: Блок")
    else:
        print("Ты выбрал: {} (урон {})".format(PLAYER_DAMAGE[player_action][0], player_damage))

    if enemy_move == "Блок":
        print("Соперник выбрал: Блок")
    else:
        print("Соперник выбрал: {} (урон {})".format(enemy_move, enemy_damage))


def main():
    print_rules()
    player_hp = MAX_HEALTH
    enemy_hp = MAX_HEALTH
    round_number = 1

    while player_hp > 0 and enemy_hp > 0:
        print("\nТвоё здоровье: {} | Здоровье соперника: {}".format(player_hp, enemy_hp))
        player_action = ask_player_action()
        enemy_move = enemy_action()

        player_damage, enemy_damage = process_round(player_action, enemy_move)
        enemy_hp -= player_damage
        player_hp -= enemy_damage

        if enemy_hp < 0:
            enemy_hp = 0
        if player_hp < 0:
            player_hp = 0

        print_round_result(round_number, player_action, enemy_move, player_damage, enemy_damage)
        print("Итог: ты нанёс {} урона, получил {} урона.".format(player_damage, enemy_damage))
        round_number += 1

    print("\n" + "=" * 36)
    if player_hp > enemy_hp:
        print("Победа! Ты выиграл бой по боксу!")
    elif enemy_hp > player_hp:
        print("Поражение. Соперник оказался сильнее.")
    else:
        print("Ничья! Оба бойца выдохлись одновременно.")


if __name__ == "__main__":
    main()  