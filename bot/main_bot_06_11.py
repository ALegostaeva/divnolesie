from flask import Flask, request
import requests
import logging
import json
import os
import random
import openpyxl
from bs4 import BeautifulSoup

app = Flask(__name__)

# логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting the application")

token = 'vk1.a.RHm8hyD06K3WmntXjWXX2x1O3k1Xw2UhAgLpnvyHH8qMYZkmWGcza5pGUImYPCzBzHMgf5iChY59O_w4kLVHZexguBJ5yDc4XhxDbxBW-50Li7vLRjNKFOJPIFb4RQKUDpBlDJ6i1W0Y6bE7oLK_9DIBiBq_pwrJ7mk-mce0oQ6svNN-oHcWnoNO8bpmJmkyu2lieLsoVsWujJT1n_btDA'

# URL к удаленному JSON-файлу
JSON_PATH = os.path.join(os.path.dirname(__file__), 'data', 'db.json')
USERS_FILE = 'users.json'
ARTEFACTS_FILE = 'artefacts.json'
INFO_MARATHON_FILE = 'info-marathon.json'
UNICORNS_FILE = 'unicorns.json'

def load_local_data():
    try:
        with open(JSON_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("32 Local BD JSON file not found.")
        return None

# Загрузка данных из локального JSON
cells_data = load_local_data()

# Функция для загрузки данных пользователей из файла
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

# Функция для загрузки данных артефактов из файла
def load_artefacts():
    if os.path.exists(ARTEFACTS_FILE):
        with open(ARTEFACTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

# Функция для загрузки данных единорогов из файла
def load_unicorns():
    if os.path.exists(UNICORNS_FILE):
        with open(UNICORNS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

# Функция для загрузки данных марафона из файла
def load_info_marathon():
    if os.path.exists(INFO_MARATHON_FILE):
        with open(INFO_MARATHON_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

# ПАГИНАЦИЯ Универсальная функция для получения данных по страницам.
def get_page(data, page=0, page_size=8):
    start = page * page_size
    end = start + page_size
    return data[start:end], len(data) > end # items, has_more

# Функция для сохранения данных пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

# Функция для получения пользователя по vk_id
def get_user(vk_id):
    users = load_users()
    for user in users:
        if user['vk_id'] == vk_id:
            return user
    return None

# Функция для добавления нового пользователя
def add_user(vk_id, first_name='Неизвестно', last_name='', is_participant=False, current_cell="", kurator = None):
    users = load_users()
    info_marathon = load_info_marathon()
    current_season = str(info_marathon.get('current_season', "1"))

    user = {
        "vk_id": vk_id,
        "first_name": first_name,
        "last_name": last_name,
        "is_participant": is_participant,
        "kurator": kurator,
        "current_cell": current_cell,
        "visited_cells": {current_season: [current_cell]},
        "admin": False,
        "artefacts": [],
        "coins": 0,
        "eggs":[],
        "unicorns_baby":[],
        "unicorns":[],
        "exp_egg": 0,
        "exp_boloto": 0,
        "exp_snow": 0,
        "exp_les": 0,
        "exp_kamen": 0,
        "exp_pustyn": 0,
        "won_seasons": []
    }
    users.append(user)
    save_users(users)

# Функция для обновления данных пользователя
def update_user(vk_id, first_name=None, last_name=None, is_participant=None, current_cell=None, coins=None, kurator=None, exp_egg=None, exp_boloto=None, exp_snow=None, exp_les=None, exp_kamen=None, exp_pustyn=None, won_season=None):
    users = load_users()
    info_marathon = load_info_marathon()
    current_season = str(info_marathon.get('current_season', "1"))

    for user in users:
        if user['vk_id'] == int(vk_id):
            if first_name is not None:
                user['first_name'] = first_name
            if last_name is not None:
                user['last_name'] = last_name
            if current_cell is not None:
                if 'visited_cells' not in user:
                    user['visited_cells'] = {}
                if current_season not in user['visited_cells']:
                    user['visited_cells'][current_season] = []
                user['visited_cells'][current_season].append(user['current_cell'])
                user['current_cell'] = current_cell
            if is_participant is not None:
                user['is_participant'] = is_participant
            if coins is not None:
                user['coins'] = coins
            if kurator is not None:
                user['kurator'] = kurator
            if exp_egg is not None:
                user['exp_egg'] = exp_egg
            if exp_boloto is not None:
                user['exp_boloto'] = exp_boloto
            if exp_snow is not None:
                user['exp_snow'] = exp_snow
            if exp_les is not None:
                user['exp_les'] = exp_les
            if exp_kamen is not None:
                user['exp_kamen'] = exp_kamen
            if exp_pustyn is not None:
                user['exp_pustyn'] = exp_pustyn
            if won_season is not None:
                if 'won_seasons' not in user:
                    user['won_seasons'] = []
                if current_cell not in user['won_seasons']:
                    user['won_seasons'].append(int(current_season))
            break
    save_users(users)

def get_info_message_about_user_admin(selected_user):
    users = load_users()
    if selected_user['is_participant']:
        participant = 'Участвует в текущем сезоне'
    else:
        participant = 'Не участвует в текущем сезоне'

    current_season = str(load_info_marathon()['current_season'])

    # Получить имя и фамилию куратора
    kurator = next((u for u in users if u.get('vk_id') == selected_user.get('kurator')), None)
    if kurator:
        kurator_name = f"{kurator['first_name']} {kurator['last_name']}"
    else:
        kurator_name = "не назначен"

    visited_cells = selected_user['visited_cells'].get(current_season, [])
    if visited_cells:
        visited_cells_str = ', '.join(visited_cells)
    else:
        visited_cells_str = 'В этом сезоне еще нет посещенных сот'
    current_cell = selected_user.get('current_cell', "Нет")

    visited_cells_all_seasons = selected_user.get('visited_cells', {})
    visited_cells_message = ""

    # Скрыли от пользователей Посещенные соты за все сезоны "Посещенные соты за все сезоны: {visited_cells_message}"
    for season, cells in visited_cells_all_seasons.items():
        season_cells_str = ', '.join(cells)
        visited_cells_message += f"\nСезон {season}: {season_cells_str}"

    won_seasons = selected_user.get('won_seasons',[])
    if won_seasons:
        won_seasons_str = ', '.join(str(season) for season in won_seasons)
    else:
        won_seasons_str = 'Нет завершенных сезонов'

    unicoins = selected_user['coins']

    if len(selected_user.get('artefacts', [])) < 1:
        artefacts = "Нет артефактов"
    else:
        all_artefacts = load_artefacts()
        # Создаем словарь для быстрого поиска артефактов по ID
        artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}

        # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
        artefact_names = [artefact_dict[artefact_id] for artefact_id in selected_user.get('artefacts', []) if artefact_id in artefact_dict]
        artefacts = ', '.join(artefact_names)

    # Для отбражения яйц, 1 стадии и 2 стадии
    all_unicorns = load_unicorns()
    # Создаем словарь для быстрого поиска единорогов по ID
    unicorn_dict = {unicorn['id']: unicorn['name'] for unicorn in all_unicorns}
    if len(selected_user.get('eggs', [])) < 1:
        eggs = "Нет яиц"
    else:
    # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
        unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in selected_user.get('eggs', []) if unicorn_id in unicorn_dict]
        eggs = ', '.join(unicorns_names)
    if len(selected_user.get('unicorns_baby', [])) < 1:
        unicorns_baby = "Нет единорогов 2 стадии"
    else:
    # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
        unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in selected_user.get('unicorns_baby', []) if unicorn_id in unicorn_dict]
        unicorns_baby = ', '.join(unicorns_names)
    if len(selected_user.get('unicorns', [])) < 1:
        unicorns = "Нет взрослых единорогов 3 стадии"
    else:
    # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
        unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in selected_user.get('unicorns', []) if unicorn_id in unicorn_dict]
        unicorns = ', '.join(unicorns_names)

    user_info_message = (f"Участник: {selected_user['first_name']} {selected_user['last_name']} (ID: {selected_user['vk_id']}),\n"
                        f"Текущий сезон №{current_season}: {participant} \n"
                        f"Куратор: {kurator_name},\n"
                        f"Находится на соте {current_cell}. \n"
                        f"Посещенные соты в этом сезоне: {visited_cells_str}.\n"
                        f"Артефакты: {artefacts}.\n "
                        f"На счету: {unicoins} юникоинов.\n"
                        f"____Единороги_____\n"
                        f"Яйца: {eggs},\n"
                        f"Единороги (2 стадия): {unicorns_baby},\n"
                        f"Взрослые единороги (3 стадия): {unicorns},\n"
                        f"______Опыт_______\n"
                        f"Опыт для яиц: {selected_user['exp_egg']},\n"
                        f"Уникальный опыт для Каменного единорога: {selected_user['exp_kamen']},\n"
                        f"Уникальный опыт для Лесного единорога: {selected_user['exp_les']},\n"
                        f"Уникальный опыт для Болотного единорога: {selected_user['exp_boloto']},\n"
                        f"Уникальный опыт для Пустынного единорога: {selected_user['exp_pustyn']},\n"
                        f"Уникальный опыт для Снежного единорога: {selected_user['exp_snow']}\n"
                        f"__________________\n"
                        f"Завершенные сезоны: {won_seasons_str}")
    return(user_info_message)


def get_users_unicorns(selected_user_id, stage='eggs'):
    users = load_users()
    user_unicorns = []

    for user in users:
        if user['vk_id'] == selected_user_id:
            if stage == 'eggs':
                user_unicorns = user['eggs']
            elif stage == 'unicorns':
                user_unicorns = user['unicorns']
            elif stage == 'unicorns_baby':
                user_unicorns = user['unicorns_baby']
            break

    return user_unicorns

# Функция админов для сброса участников
def reset_participants():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        for user in users:
            user['is_participant'] = False
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return True
    except FileNotFoundError:
        return False

# Функция для получения списка всех участников
def get_all_participants():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
            participants = [user for user in users if user.get('is_participant')]
        return participants
    except FileNotFoundError:
        logger.error("Файл users.json не найден.")
        return []

def save_participants_to_xlsx(filename='участники.xlsx'):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Участники"

    headers = ['vk_id',
                'Имя',
                'Фамилия',
                'Куратор',
                'Текущая сота',
                'Посещенные соты в этот сезон',
                'Юникоины',
                'Артефакты',
                'Яйца',
                'Единороги (2 стадия)',
                'Взрослые единороги (3 стадия)',
                'Опыт для яиц',
                'Уникальный опыт для Каменного единорога',
                'Уникальный опыт для Лесного единорога',
                'Уникальный опыт для Болотного единорога',
                'Уникальный опыт для Пустынного единорога',
                'Уникальный опыт для Снежного единорога',
                'Завершенные сезоны']
    sheet.append(headers)

    participants = get_all_participants()
    users = load_users() # Получить имя куратора
    all_artefacts = load_artefacts()
    all_unicorns = load_unicorns()
    # Создаем словарь для быстрого поиска артефактов по ID
    artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}
    # Создаем словарь для быстрого поиска единорогов по ID
    unicorn_dict = {unicorn['id']: unicorn['name'] for unicorn in all_unicorns}

    for participant in participants:
        kurator = next((u for u in users if u.get('vk_id') == participant.get('kurator')), None)
        if kurator:
            kurator_name = f"{kurator['first_name']} {kurator['last_name']}"
        else:
            kurator_name = "не назначен"

        current_season = str(load_info_marathon()['current_season'])

        if len(participant['visited_cells'].get(current_season, [])) < 1:
            visited_cells = "Нет"
        else:
            visited_cells = ', '.join(participant['visited_cells'].get(current_season, []))

        if len(participant.get('won_seasons', [])) < 1:
            won_seasons = "Нет"
        else:
            won_seasons = ', '.join(map(str, participant.get('won_seasons', [])))

        if len(participant.get('artefacts', [])) < 1:
            artefacts = "Нет"
        else:
            # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
            artefact_names = [artefact_dict[artefact_id] for artefact_id in participant.get('artefacts', []) if artefact_id in artefact_dict]
            artefacts = ', '.join(artefact_names)

        # Для отбражения яйц, 1 стадии и 2 стадии
        if len(participant.get('eggs', [])) < 1:
            eggs = "Нет"
        else:
            # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
            unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in participant.get('eggs', []) if unicorn_id in unicorn_dict]
            eggs = ', '.join(unicorns_names)
        if len(participant.get('unicorns_baby', [])) < 1:
            unicorns_baby = "Нет"
        else:
            # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
            unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in participant.get('unicorns_baby', []) if unicorn_id in unicorn_dict]
            unicorns_baby = ', '.join(unicorns_names)
        if len(participant.get('unicorns', [])) < 1:
            unicorns = "Нет"
        else:
            # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
            unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in participant.get('unicorns', []) if unicorn_id in unicorn_dict]
            unicorns = ', '.join(unicorns_names)

        row = [
            participant['vk_id'],
            participant['first_name'],
            participant['last_name'],
            kurator_name,
            participant['current_cell'],
            visited_cells,
            participant['coins'],
            artefacts,
            eggs,
            unicorns_baby,
            unicorns,
            participant['exp_egg'],
            participant['exp_kamen'],
            participant['exp_les'],
            participant['exp_boloto'],
            participant['exp_pustyn'],
            participant['exp_snow'],
            won_seasons
            ]
        sheet.append(row)
    workbook.save(filename)

# Функция возвращает пагинированный список пользователей в inline-кнопках
def get_users_inline_buttons(users, page=0, action_call=''):
    items_for_page, has_more = get_page(users, page, 4)
    users_keyboard = {
            "inline": True,
            "buttons": []
        }
    for u in items_for_page:
        users_keyboard['buttons'].append([{"action": {
            "type": "callback",
            "label": f"{u['first_name']} {u['last_name']}",
            "payload": json.dumps({"action":action_call,"selected_user_id":u['vk_id'],"page":page})}}])
    if has_more:
        users_keyboard['buttons'].append([{"action": {"type": "callback", "label": "Ещё", "payload": json.dumps({"action": "more","list":"users","page": page+1,"action_call":action_call })}}])

    return users_keyboard

# Артефакты
# Функция для добавления артефакта пользователю
def add_artefact_to_user(user_id, artefact_id):
    users = load_users()
    for user in users:
        if user['vk_id'] == user_id:
            if 'artefacts' not in user:
                user['artefacts'] = []
            user['artefacts'].append(artefact_id)
            break
    save_users(users)

# Удаление артефакта у пользователя
def remove_artefact_from_user(user_id, artefact_id):
    users = load_users()
    for user in users:
        if user['vk_id'] == user_id:
            if artefact_id in user['artefacts']:
                user['artefacts'].remove(artefact_id)
            break
    save_users(users)

# удалить единорога у пользователя
def remove_unicorn_from_user(user_id, stage = None, id_for_remove = None):
    users = load_users()
    if id_for_remove is None:
        logger.info("447 remove_unicorn_from_user -  id_for_remove is None")
        return False
    for user in users:
        if user['vk_id'] == user_id:
            if id_for_remove in user[stage]:
                user[stage].remove(id_for_remove)
                break
            else:
                logger.info("455 remove_unicorn_from_user - no user id")
                return False
    save_users(users)
    return True

# добавить единорога
def add_unicorn_to_user(user_id, stage = None, unicorn_id = None):
    users = load_users()
    if unicorn_id is None:
        return
    if stage is None:
        return
    for user in users:
        if user['vk_id'] == user_id:
            if stage not in user:
                user[stage] = []
            user[stage].append(unicorn_id)
            break
    save_users(users)

# Откат перемещения на 1 соту
def revert_last_move(user_id):
    user_data = get_user(int(user_id))
    
    if not user_data or 'current_cell' not in user_data or 'visited_cells' not in user_data:
        logger.info(f'Не удалось откатить соту, так как пользователь c ID {user_id} не найден')
        return None
    
    current_season = str(load_info_marathon().get('current_season', "1"))
    visited_cells = user_data['visited_cells'].get(current_season, [])
    
    if len(visited_cells) < 2:
        logger.info(f"Не получилось откатить соту, так как путник {user_data['first_name']} {user_data['last_name']} еще не двигался по сотам в этом сезоне.")
        return None

    previous_cell = visited_cells[-2]
    users = load_users()

    for user in users:
        if user['vk_id'] == int(user_id):
            user['current_cell'] = previous_cell
            user['visited_cells'][current_season].pop()
            break
    
    save_users(users)
    return previous_cell



# Функция для обновления текущего сезона
def update_season(new_season_number):
    info = load_info_marathon()
    info['current_season'] = new_season_number
    with open(INFO_MARATHON_FILE, 'w') as file:
        json.dump(info, file)

# Функция для отправки уведомлений администраторам о заявке в марафоне
def notify_admins(vk_id, first_name = "", last_name = "", user_exists = ""):
    users = load_users()
    admins = [user for user in users if user.get('admin', False)]
    for admin in admins:
        keyboard = {
            "inline": True,
            "buttons": [
                [{"action": {"type": "callback", "label": "Принять", "payload": json.dumps({"action": "accept", "user_id": vk_id})}},
                {"action": {"type": "callback", "label": "Отклонить", "payload": json.dumps({"action": "reject", "user_id": vk_id})}}]
            ]
        }
        message = f"Пользователь {first_name} {last_name} (ID: {vk_id}) хочет участвовать в марафоне.\n" \
                  f"Пользователь уже участвовал в марафоне: {'Да' if user_exists else 'Нет'}"
        send_message(admin['vk_id'], message, keyboard)


# Функция для отправки уведомлений администраторам любое
def notify_admins_info(vk_id, message):
    users = load_users()
    admins = [user for user in users if user.get('admin', False)]
    for admin in admins:
        message = message
        send_message(admin['vk_id'], message)



def accept_marathon_request(vk_id, admin_id):
    # Получаем данные о пользователе
    user_info = get_user_info(vk_id)
    first_name = user_info.get('first_name', 'Неизвестно')
    last_name = user_info.get('last_name', '')

    # Проверяем, есть ли пользователь в users.json
    user = get_user(vk_id)

    marathon_info = load_info_marathon()

    link = marathon_info['link']
    login = marathon_info['login']
    password = marathon_info['password']

    if user:
        # Обновляем информацию о пользователе
        update_user(vk_id, first_name, last_name, is_participant=True)
        send_message(vk_id, f"Вы успешно зарегистрированы в марафоне Дивнолесье! Удачи! \n Ссылка на карту: {link} \n Логин: {login}\n Пароль: {password}. \n Вы находитесь здесь:{user.get('current_cell', '')}")
    else:
        # Выбираем случайное значение для current_cell из cells_data
        current_cell = random.choice([cell['name'] for cell in cells_data])

        # Добавляем нового пользователя
        add_user(vk_id, first_name, last_name, is_participant=True, kurator = admin_id)
        send_message(vk_id, f"Вы успешно зарегистрированы в марафоне Дивнолесье! Удачи! \n Ссылка на карту: {link} \n Логин: {login}\n Пароль: {password}. \n Ваше путешествие начинается здесь:{current_cell}")

def reject_marathon_request(vk_id):
    send_message(vk_id, "Упс, что-то случилось и мы не смогли зарегистрировать вас в марафоне Дивнолесье. Свяжитесь с кураторами марафона.")

def split_message(text, max_length=1000):
    """Разбивает текст на части, каждая из которых не превышает max_length символов."""
    parts = []
    while len(text) > max_length:
        # Найти последний \n в пределах max_length символов
        split_index = text[:max_length].rfind('\n')
        if split_index == -1:
            # Если \n не найден, искать последний пробел
            split_index = text[:max_length].rfind(' ')
        if split_index == -1:
            split_index = max_length
        parts.append(text[:split_index].strip())
        text = text[split_index:].strip()
    parts.append(text)
    return parts

# Убирает ссылки из текста о соте в методе info
def clean_text_from_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    for link in soup.find_all('a', class_='linkToVk'):
        url = link['href']
        link.replace_with(f' {url} ')
    return soup.get_text()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logger.info("WEBHOOK")

    if data['type'] == 'confirmation':
        return '5537e3e0'

    elif data['type'] == 'wall_reply_new' or data['type'] == 'message_new' or data['type'] == 'wall_post_new':
        # Извлекаем текст сообщения
        if data['type'] == 'wall_reply_new':
            message = data['object'].get('text', '')
            peer_id = data['object']['from_id']
            user_id = data['object']['from_id']
            logger.info("240 wall_reply_new: %s", message)
        elif data['type'] == 'message_new':
            message = data['object']['message'].get('text', '')
            peer_id = data['object']['message']['peer_id']
            user_id = data['object']['message']['from_id']
            logger.info("243 message_new: %s", message)
        elif data['type'] == 'wall_post_new':
            message = data['object'].get('text', '')
            peer_id = data['object']['from_id']
            user_id = data['object']['from_id']
            logger.info("246 wall_post_new: %s", message)

        user_info_vk = get_user_info(user_id)
        user = get_user(user_id)

        first_name = user_info_vk.get('first_name', '')
        last_name = user_info_vk.get('last_name', '')

         # Обработка команды, убрать лишнее
        if message.startswith('[') and ']' in message:
            command = message.split(']', 1)[1].strip()
        else:
            command = message.strip()

        logger.info(f"630 Processed command: {command}")

        # список команд простых смертых
        if command.lower() == 'старт' or not message:
            if user_info_vk:
                user_name = first_name + ' ' + last_name
                mention = f"[id{user_id}|{user_name}]"
                welcome_message = f"Привет, {mention}! Я бот Дивнолесья. Я могу помочь тебе в твоем путешествии и расскажу о каждой соте. \n" \
                            "Доступные команды:\n" \
                               "- 'info [номер соты]': я расскажу тебе об этой соте. Например: 'info A1'.\n" \
                               "- 'профиль': я расскажу тебе на какой соте ты находишься и какие соты уже прошел (только для участников).\n" \
                                "- 'карта': напоминание о логине и пароле от карты Дивнолесья(только для участников).\n" \
                               "- 'about': информация о марафоне Дивнолесье. Так же, если ты участник марафона, то найдешь там напоминание о логине и пароле от карты.\n" \
                               "- 'участвую': заявка на участие в марафоне. \n" \
                               "- 'старт': Если ты потеряешься, напиши старт и я тебе расскажу подробнее о всех командах, которые я понимаю."
                keyboard = {
                        "inline": True,
                        "buttons": [
                            [{"action": {"type": "text", "label": "старт"}}, {"action": {"type": "text", "label": "about"}}],
                            [{"action": {"type": "text", "label": "info A1"}}],
                            [{"action": {"type": "text", "label": "профиль"}},{"action": {"type": "text", "label": "карта"}}],
                            [{"action": {"type": "text", "label": "участвую"}}],
                            [{"action": {"type": "open_link","link": "https://vk.com/polkasknigami","label": "Написать Кураторам"}}]
                        ]
                    }
                response = send_message(peer_id, welcome_message,keyboard)
                if 'error' in response:
                    error_code = response['error']['error_code']
                    error_msg = response['error']['error_msg']
                    logger.error(f"659 Error {error_code}: {error_msg}")
                    # Обработка ошибки отправки сообщения
                    if error_code == 901:
                        send_message(peer_id, "Пожалуйста, подпишитесь на сообщения от нашего сообщества, чтобы получать уведомления.")
                else:
                    logger.info(f"664 Sent message: {response}")
            else:
                send_message(peer_id, "Упс, что-то пошло не так.")
                logger.error("Failed to get user info from VK")

        # заявка на участие в марафоне
        elif command.lower().startswith('участвую'):
            user = get_user(user_id)
            admin_message = ""
            if user:
                if user.get('is_participant', True):
                    user_message = "Вы уже участвуете в марафоне."
                else:
                    info_marathon = load_info_marathon()
                    previous_season = int(info_marathon['current_season']) - 1
                    if previous_season in user.get('won_seasons', []):
                        link = info_marathon['link']
                        login = info_marathon['login']
                        password = info_marathon['password']
                        update_user(user_id, first_name=first_name, last_name=last_name, is_participant=True)
                        user_message = f"Вы успешно зарегистрированы в марафоне Дивнолесье! Удачи! \n Ссылка на карту: {link} \n Логин: {login}\n Пароль: {password}. \n Вы находитесь здесь:{user.get('current_cell', '')}"
                        admin_message = f"Путник {user.get('first_name', '')} {user.get('last_name', '')}(ID {user.get('vk_id', '')}) был добавлен участником в текущий сезон автоматически, так как успешно завершил предыдущий сезон."
                    else:
                        user_exists = True
                        notify_admins(user_id, first_name, last_name, user_exists)
                        user_message = "Ваша заявка на участие в марафоне отправлена на рассмотрение. Не забудь забежать в личные сообщения к Ксении и выдать звенящую монету за участие в марафоне!"
            else:
                user_exists = False
                notify_admins(user_id, first_name, last_name, user_exists)
                user_message = "Ваша заявка на участие в марафоне отправлена на рассмотрение. Не забудь забежать в личные сообщения к Ксении и выдать звенящую монету за участие в марафоне!"

            if len(admin_message) > 0:
                notify_admins_info(peer_id, admin_message)
            send_message(peer_id,user_message)

        # команда для получения информации о соте
        elif command.lower().startswith('info'):
            user = get_user(user_id)
            if user:
                if not(cells_data and len(cells_data) > 0):
                    # Если JSON не загружен
                    fog_message = ("Все дивнолесье заволокло туманом и дороги не видно. "
                                   "Оставайся на месте путник, туман рассеется и ты сможешь продолжить свой путь. "
                                   "А пока, чтобы не было так одиноко, подходи поближе к костерку с Кураторами Дивнолесья "
                                   "и рассказывай, что волнует тебя и как быть дальше.")
                    keyboard = {
                        "inline": True,
                        "buttons": [
                            [{
                                "action": {
                                    "type": "open_link",
                                    "link": "https://vk.com/polkasknigami",
                                    "label": "Написать Кураторам"
                                }
                            }]
                        ]
                    }
                    response = send_message(peer_id, fog_message, keyboard)
                else:
                    parts = command.split()
                    if len(parts) > 1:
                        query = parts[1].upper()  # Преобразуем к верхнему регистру для поиска
                        matched_cell = next((item for item in cells_data if item['name'].upper() == query), None)
                        if matched_cell:
                            cell_name = f"Сота: {matched_cell['name']}"  # Название соты жирным шрифтом
                            loc = f"Локация: {matched_cell['loc']}"  # Локация курсивом
                            task = matched_cell['task'].replace('</br>', '')  # Удаление символов </br> из текста задания
                            task = clean_text_from_html(task) # Удаление html из ссылок
                            on_map = f"https://divnolesie.ru/pages/info.html?id={matched_cell['name']}"

                            next_moves = matched_cell.get('next', [])
                            keyboard = {
                                "inline": True,
                                "buttons": []
                            }
                            for move in next_moves:
                                keyboard['buttons'].append([{"action": {"type": "text", "label": f"info {move}"}}])

                            message = f"{cell_name}\n{loc}\n\n{task}\n\n Посмотреть соту на карте {on_map}\n\nСледующий ход возможен на:"

                            messages = split_message(message)

                            for i, part in enumerate(messages):
                                if i == len(messages) - 1:
                                    send_message(peer_id, part, keyboard=keyboard)
                                else:
                                    send_message(peer_id, part)

                        else:
                            not_found_message = ("Путник, кажется ты сбился с пути. То место, о котором ты просишь информацию "
                                                 "не существует на наших картах. Попробуй поискать что-то другое или приходи "
                                                 "за помощью к Кураторам Дивнолесья.")
                            keyboard = {
                                "inline": True,
                                "buttons": [
                                    [{
                                        "action": {
                                            "type": "open_link",
                                            "link": "https://vk.com/polkasknigami",
                                            "label": "Написать Кураторам"
                                        }
                                    }]
                                ]
                            }
                            send_message(peer_id, not_found_message, keyboard)
                    else:
                        send_message(peer_id, "Пожалуйста, укажи номер соты в формате [латинская буква][число]. Например, 'сота A1'.")
            else:
                send_message(peer_id, "Карта выдается только путникам Дивнолесья. Если ты хочешь путешествовать с нами по Дивнолесью, то подай заявку на участие.")

        # напоминание логина и пароля от карты
        elif command.lower() == 'карта':
            user_message = ''
            if user_info_vk:
                if user['is_participant']:
                    if user:
                        user_name = first_name + ' ' + last_name
                        mention = f"[id{user_id}|{user_name}]"
                    else:
                        mention = "путник"

                    marathon_info = load_info_marathon()

                    link = marathon_info['link']
                    login = marathon_info['login']
                    password = marathon_info['password']

                    user_message += (f'Привет, {mention}!\n\n Ссылка на карту: {link} \n Логин: {login} \n Пароль: {password}')
                
                else:
                    user_message = 'Вы еще не вступили на тропинки Дивнолесья. Подайте заявку на участие в марафоне и получите доступ к карте Дивнолесья.'
            else:
                user_message = 'Упс, что-то пошло не так и мы не можем найти вас. Возможно вы еще не вступили на тропинки Дивнолесья. Подайте заявку на участие в марафоне и получите доступ к карте Дивнолесья.'
            response = send_message(peer_id, user_message)

        # команда о получении информации о марафоне
        elif command.lower() == 'about':
            if user_info_vk:
                if user:
                    user_name = first_name + ' ' + last_name
                    mention = f"[id{user_id}|{user_name}]"
                else:
                    mention = "путник"

                welcome_message = f"Привет, {mention}! Марафон Дивнолесье был создан много лет назад, чтобы вдохновить людей больше читать и делиться прочитанным."\
                "Кураторами проекта являются Ксения и Анна. Ты найдешь их в группе https://vk.com/polkasknigami.\n"
                
            response = send_message(peer_id, welcome_message)
            if 'error' in response:
                    error_code = response['error']['error_code']
                    error_msg = response['error']['error_msg']
                    logger.error(f"Error {error_code}: {error_msg}")
                    # Обработка ошибки отправки сообщения
                    if error_code == 901:
                        send_message(peer_id, "Пожалуйста, подпишитесь на сообщения от нашего сообщества, чтобы получать уведомления.")

        # Узнать на какой соте находишься и где уже был
        elif command.lower() == 'профиль':

            if not user:
                return send_message(peer_id, "Хм, кажется мы тебя потеряли? Или ты еще не вступил на путь Дивнолесья? Напиши Кураторам и они помогут.")

            if user['is_participant']:
                participant = 'Вы участвуете в текущем сезоне'
            else:
                participant = 'Вы не участвуете в текущем сезоне'

            current_season = str(load_info_marathon()['current_season'])

            # Получить имя и фамилию куратора
            users = load_users()
            kurator = next((u for u in users if u.get('vk_id') == user.get('kurator')), None)
            if kurator:
                kurator_name = f"{kurator['first_name']} {kurator['last_name']}"
            else:
                kurator_name = "не назначен"

            visited_cells = user['visited_cells'].get(current_season, [])
            if visited_cells:
                visited_cells_str = ', '.join(visited_cells)
            else:
                visited_cells_str = 'В этом сезоне еще нет посещенных сот'
            current_cell = user.get('current_cell', "Нет")

            visited_cells_all_seasons = user.get('visited_cells', {})
            visited_cells_message = ""

            # Скрыли от пользователей Посещенные соты за все сезоны "Посещенные соты за все сезоны: {visited_cells_message}"
            for season, cells in visited_cells_all_seasons.items():
                season_cells_str = ', '.join(cells)
                visited_cells_message += f"\nСезон {season}: {season_cells_str}"


            unicoins = user['coins']

            if len(user.get('artefacts', [])) < 1:
                artefacts = "У вас нет артефактов"
            else:
                all_artefacts = load_artefacts()
                # Создаем словарь для быстрого поиска артефактов по ID
                artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}

                # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
                artefact_names = [artefact_dict[artefact_id] for artefact_id in user.get('artefacts', []) if artefact_id in artefact_dict]

                artefacts = ', '.join(artefact_names)

            # Для отбражения яйц, 1 стадии и 2 стадии
            all_unicorns = load_unicorns()
            # Создаем словарь для быстрого поиска единорогов по ID
            unicorn_dict = {unicorn['id']: unicorn['name'] for unicorn in all_unicorns}
            if len(user.get('eggs', [])) < 1:
                eggs = "У вас нет яиц"
            else:
                # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in user.get('eggs', []) if unicorn_id in unicorn_dict]
                eggs = ', '.join(unicorns_names)
            if len(user.get('unicorns_baby', [])) < 1:
                unicorns_baby = "У вас нет единорогов 2 стадии"
            else:
                # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in user.get('unicorns_baby', []) if unicorn_id in unicorn_dict]
                unicorns_baby = ', '.join(unicorns_names)
            if len(user.get('unicorns', [])) < 1:
                unicorns = "У вас нет взрослых единорогов 3 стадии"
            else:
                # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in user.get('unicorns', []) if unicorn_id in unicorn_dict]
                unicorns = ', '.join(unicorns_names)

            user_name = first_name + ' ' + last_name
            mention = f"[id{user_id}|{user_name}]"

            user_info_message = (f"Привет, {mention}!\n Текущий сезон №{current_season}: {participant} \n"
                                    f"Куратор: {kurator_name},\n"
                                    f"Вы находитесь на соте {current_cell}. \n"
                                    f"Посещенные соты в этом сезоне: {visited_cells_str}.\n"
                                    f"Ваши артефакты: {artefacts}.\n "
                                    f"У вас на счету: {unicoins} юникоинов.\n"
                                    f"____Единороги_____\n"
                                    f"Яйца: {eggs},\n"
                                    f"Единороги (2 стадия): {unicorns_baby},\n"
                                    f"Взрослые единороги (3 стадия): {unicorns},\n"
                                    f"______Опыт_______\n"
                                    f"Опыт для яиц: {user['exp_egg']},\n"
                                    f"Уникальный опыт для Каменного единорога: {user['exp_kamen']},\n"
                                    f"Уникальный опыт для Лесного единорога: {user['exp_les']},\n"
                                    f"Уникальный опыт для Болотного единорога: {user['exp_boloto']},\n"
                                    f"Уникальный опыт для Пустынного единорога: {user['exp_pustyn']},\n"
                                    f"Уникальный опыт для Снежного единорога: {user['exp_snow']}")
            messages = split_message(user_info_message)

            for i, part in enumerate(messages):
                send_message(peer_id, part)



        # ADMIN секция
        # Получить команды, доступные админам
        elif command.lower() == 'админ':
            if user and user.get('admin'):
                admin_message = (
                            "Привет, администратор! Вот доступные команды:\n"
                            "- move [ID_пользователя] [Сота (латинские буквы)] - Переместит пользователя на указанную соту. Например: move 1234567 D1.\n"
                            "- revert_move [ID_пользователя] - Откатит ход пользователя на 1 последнюю соту. Например: move 1234567.\n"
                            "- profile [ID_пользователя] - Покажет полный профиль пользователя, со всей имеющейся информацией. Например: profile 123456.\n"
                            "- участники - Покажет список всех участников с короткой информацией по каждому. Не покажет тех, кто не участвует в сезоне.\n"
                            "- участники список - Отправит файл с информацией по всем участникам со всей информацией по каждому. Не покажет тех, кто не участвует в сезоне.\n"
                            "- добавить/удалить артефакт - Позволит добавить/удалить артефакт выбранному пользователю. Сначала выберите пользователя из списка, потом выберите артефакт.\n"
                            "- добавить/удалить единорога - Позволит добавить/удалить единорога или яйцо выбранному пользователю. Сначала выберите пользователя из списка, потом выберите единорога или яйцо.\n"
                            "- выбрать победителей - Позволит выбрать участников, которые успешно завершили сезон и смогут начать следующий сезон автоматически без оплаты и подтверждения. ВАЖНО! Определить победителей ДО команды старта нового сезона.\n"
                            "- начать сезон - Сбросит у всех участников признак, что они участвуют в марафоне (чтобы они смогли подать заявки на новый сезон). И обновит номер сезона.\n"
                            "- add_coins|remove_coins|update_coins [ID_пользователя] [Целое число] - Для добавления юникоинов. Пример: add_coins 5649984 10\n"
                            "- add_exp|update_exp [Тип опыта] [ID_пользователя] [Целое число] - Добавит указанный опыт у пользователя. Типы опыта: eggs (яйца), les (уникальный лесной опыт), kamen (уникальный каменный опыт), boloto (уникальный болотный опыт), pustyn (уникальный пустынный опыт), snow (уникальный снежный опыт). Пример: add_exp boloto 5649984 10\n"
                            "ID пользователя можно взять из команды -участники-. Вот еще доступные команды:"
                        )

                keyboard = {
                        "inline": True,
                        "buttons": [
                            [{"action": {"type": "text", "label": "участники"}},{"action": {"type": "text", "label": "участники список"}}],
                            [{"action": {"type": "text", "label": "добавить артефакт"}}, {"action": {"type": "text", "label": "удалить артефакт"}}],
                            [{"action": {"type": "text", "label": "добавить единорога"}}, {"action": {"type": "text", "label": "удалить единорога"}}],
                            [{"action": {"type": "text", "label": "выбрать победителей"}}, {"action": {"type": "text", "label": "начать сезон"}}]
                        ]
                    }

                messages = split_message(admin_message)

                for i, part in enumerate(messages):
                    if i == len(messages) - 1:
                        send_message(peer_id, part, keyboard=keyboard)
                    else:
                        send_message(peer_id, part)

            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Переместить на соту
        elif command.lower().startswith('move'):
            admin_message = ""
            user_message = ""
            if user and user.get('admin'):
                _, selected_user_id, next_cell = message.split()

                users = load_users()
                selected_user = next((u for u in users if u['vk_id'] == int(selected_user_id)), None)

                if next_cell:
                    next_cell = next_cell.upper()
                    matched_cell = next((item for item in cells_data if item['name'] == next_cell), None)
                    if matched_cell:
                        if selected_user:
                            current_cell = selected_user.get('current_cell', '')
                            first_name = selected_user['first_name']
                            last_name = selected_user['last_name']
                            update_user(selected_user_id, current_cell = next_cell)
                            admin_message = f"Пользователь {first_name} {last_name} успешно перемещен с соты {current_cell} на соту {next_cell}."
                            if current_cell == next_cell:
                                user_message = f"Ваш путь продолжается на соте {next_cell}. Подробнее про соту можно посмотреть здесь https://divnolesie.ru/pages/info.html?id={next_cell}."
                            else:
                                user_message = f"Ваш путь продолжается! Добро пожаловать на соту {next_cell}. Подробнее про соту можно посмотреть здесь https://divnolesie.ru/pages/info.html?id={next_cell}."
                            user_keyboard = {
                                "inline": True,
                                "buttons": [
                                    [{
                                        "action": {
                                            "type": "text",
                                            "label": f"info {next_cell}"
                                        }
                                    }]
                                ]
                            }
                        else:
                            admin_message = "Пользователь с таким ID не найден."
                    else:
                        admin_message = "Такая сота не найдена."
                else:
                    admin_message = "Отправьте команду в формате move [ID путника] [сота]. Например:'move 301836 A1'."
            else:
                admin_message = "У вас нет прав на выполнение этой команды"

            send_message(peer_id, admin_message)

            if len(user_message) > 0:
                send_message(selected_user_id, user_message, user_keyboard)

        # Сброс участников марафона перед стартом сезона
        elif command.lower() == 'начать сезон':
            if user and user.get('admin'):
                info_marathon = load_info_marathon()
                new_season = int(info_marathon['current_season']) + 1
                update_season(new_season)
                reset_success = reset_participants()
                response = send_message(peer_id, f"Начат новый сезон {new_season}.")
                if reset_success:
                    send_message(peer_id, "Произошла ошибка при сбросе участников.")
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Основной код для команды "участники"
        elif command.lower().strip() == 'участники список':
            if user and user.get('admin'):
                save_participants_to_xlsx()
                send_file(peer_id, 'участники.xlsx')
                os.remove('участники.xlsx')
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Чужой id для админа
        elif command.lower().startswith('id'):
            if not user.get('admin'):
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")
                return

            try:
                _, name = message.split(maxsplit=1)
                last_name = name.lower().replace('ё', 'е')
                users = load_users()
                selected_user = None
                for user in users:
                    if user.get('last_name', '').lower() == last_name:
                        selected_user = user

                if not selected_user:
                    send_message(peer_id, f"Пользователь с фамилией {last_name} не найден.")
                else:
                    user_info_message = selected_user.get('vk_id', 'Нет ID')
                    send_message(peer_id, user_info_message)
            except ValueError:
                send_message(peer_id, "Неверный формат команды. Используйте: id [фамилия]")

        # Чужой профиль для админа
        elif command.lower().startswith('profile'):

            if user and user.get('admin'):
                _, selected_user_id = message.split()

                users = load_users()
                selected_user = next((u for u in users if u['vk_id'] == int(selected_user_id)), None)

                if selected_user:

                    if selected_user['is_participant']:
                        participant = 'Участвует в текущем сезоне'
                    else:
                        participant = 'Не участвует в текущем сезоне'

                    current_season = str(load_info_marathon()['current_season'])

                    # Получить имя и фамилию куратора
                    kurator = next((u for u in users if u.get('vk_id') == selected_user.get('kurator')), None)
                    if kurator:
                        kurator_name = f"{kurator['first_name']} {kurator['last_name']}"
                    else:
                        kurator_name = "не назначен"

                    visited_cells = selected_user['visited_cells'].get(current_season, [])
                    if visited_cells:
                        visited_cells_str = ', '.join(visited_cells)
                    else:
                        visited_cells_str = 'В этом сезоне еще нет посещенных сот'
                    current_cell = selected_user.get('current_cell', "Нет")

                    visited_cells_all_seasons = selected_user.get('visited_cells', {})
                    visited_cells_message = ""

                    # Скрыли от пользователей Посещенные соты за все сезоны "Посещенные соты за все сезоны: {visited_cells_message}"
                    for season, cells in visited_cells_all_seasons.items():
                        season_cells_str = ', '.join(cells)
                        visited_cells_message += f"\nСезон {season}: {season_cells_str}"

                    won_seasons = selected_user.get('won_seasons',[])
                    if won_seasons:
                        won_seasons_str = ', '.join(str(season) for season in won_seasons)
                    else:
                        won_seasons_str = 'Нет завершенных сезонов'

                    unicoins = selected_user['coins']

                    if len(selected_user.get('artefacts', [])) < 1:
                        artefacts = "Нет артефактов"
                    else:
                        all_artefacts = load_artefacts()
                        # Создаем словарь для быстрого поиска артефактов по ID
                        artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}

                        # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
                        artefact_names = [artefact_dict[artefact_id] for artefact_id in selected_user.get('artefacts', []) if artefact_id in artefact_dict]

                        artefacts = ', '.join(artefact_names)

                    # Для отбражения яйц, 1 стадии и 2 стадии
                    all_unicorns = load_unicorns()
                    # Создаем словарь для быстрого поиска единорогов по ID
                    unicorn_dict = {unicorn['id']: unicorn['name'] for unicorn in all_unicorns}
                    if len(selected_user.get('eggs', [])) < 1:
                        eggs = "Нет яиц"
                    else:
                        # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                        unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in selected_user.get('eggs', []) if unicorn_id in unicorn_dict]
                        eggs = ', '.join(unicorns_names)
                    if len(selected_user.get('unicorns_baby', [])) < 1:
                        unicorns_baby = "Нет единорогов 2 стадии"
                    else:
                        # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                        unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in selected_user.get('unicorns_baby', []) if unicorn_id in unicorn_dict]
                        unicorns_baby = ', '.join(unicorns_names)
                    if len(selected_user.get('unicorns', [])) < 1:
                        unicorns = "Нет взрослых единорогов 3 стадии"
                    else:
                        # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                        unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in selected_user.get('unicorns', []) if unicorn_id in unicorn_dict]
                        unicorns = ', '.join(unicorns_names)

                    user_name = first_name + ' ' + last_name

                    user_info_message = (f"Участник: {selected_user['first_name']} {selected_user['last_name']} (ID: {selected_user['vk_id']}),\n"
                                            f"Текущий сезон №{current_season}: {participant} \n"
                                            f"Куратор: {kurator_name},\n"
                                            f"Находится на соте {current_cell}. \n"
                                            f"Посещенные соты в этом сезоне: {visited_cells_str}.\n"
                                            f"Артефакты: {artefacts}.\n "
                                            f"На счету: {unicoins} юникоинов.\n"
                                            f"____Единороги_____\n"
                                            f"Яйца: {eggs},\n"
                                            f"Единороги (2 стадия): {unicorns_baby},\n"
                                            f"Взрослые единороги (3 стадия): {unicorns},\n"
                                            f"______Опыт_______\n"
                                            f"Опыт для яиц: {selected_user['exp_egg']},\n"
                                            f"Уникальный опыт для Каменного единорога: {selected_user['exp_kamen']},\n"
                                            f"Уникальный опыт для Лесного единорога: {selected_user['exp_les']},\n"
                                            f"Уникальный опыт для Болотного единорога: {selected_user['exp_boloto']},\n"
                                            f"Уникальный опыт для Пустынного единорога: {selected_user['exp_pustyn']},\n"
                                            f"Уникальный опыт для Снежного единорога: {selected_user['exp_snow']}\n"
                                            f"__________________\n"
                                            f"Завершенные сезоны: {won_seasons_str}")

                    messages = split_message(user_info_message)

                    for i, part in enumerate(messages):
                        send_message(peer_id, part)
                else:
                    send_message(peer_id, f"Не удалось найти пользователя с ID {selected_user_id}")

            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Получение списка всех участников марафона (is_participant=true). Без пагинации (проверить ограничение вк)
        elif command.lower() == 'участники':
            if user and user.get('admin'):
                participants = get_all_participants()
                if participants:

                    all_artefacts = load_artefacts()
                    all_unicorns = load_unicorns()
                    # Создаем словарь для быстрого поиска артефактов по ID
                    artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}
                    # Создаем словарь для быстрого поиска единорогов по ID
                    unicorn_dict = {unicorn['id']: unicorn['name'] for unicorn in all_unicorns}

                    users = load_users()

                    messages = []
                    messages.append(f"Всего участников {len(participants)}")

                    for participant in participants:
                        kurator = next((u for u in users if u.get('vk_id') == participant.get('kurator')), None)
                        if len(participant.get('artefacts', [])) < 1:
                            artefacts = "Нет артефактов"
                        else:
                            # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
                            artefact_names = [artefact_dict[artefact_id] for artefact_id in participant.get('artefacts', []) if artefact_id in artefact_dict]
                            artefacts = ', '.join(artefact_names)

                        # Для отбражения яйц, 1 стадии и 2 стадии
                        if len(participant.get('eggs', [])) < 1:
                            eggs = "У вас нет яиц"
                        else:
                            # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                            unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in participant.get('eggs', []) if unicorn_id in unicorn_dict]
                            eggs = ', '.join(unicorns_names)
                        if len(participant.get('unicorns_baby', [])) < 1:
                            unicorns_baby = "У вас нет единорогов 2 стадии"
                        else:
                            # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                            unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in participant.get('unicorns_baby', []) if unicorn_id in unicorn_dict]
                            unicorns_baby = ', '.join(unicorns_names)
                        if len(participant.get('unicorns', [])) < 1:
                            unicorns = "У вас нет взрослых единорогов 3 стадии"
                        else:
                            # Получаем список названий единорогов, соответствующих ID, которые хранятся у пользователя
                            unicorns_names = [unicorn_dict[unicorn_id] for unicorn_id in participant.get('unicorns', []) if unicorn_id in unicorn_dict]
                            unicorns = ', '.join(unicorns_names)

                        current_season = str(load_info_marathon()['current_season'])
                        visited_cells = participant['visited_cells'].get(current_season, [])
                        current_cell = participant.get('current_cell', '')

                        participant_info = (f"\n \n Имя: {participant['first_name']} {participant['last_name']} (ID {participant['vk_id']}),\n"
                                                f"Текущая сота: {current_cell},\n"
                                                f"Посещенные в этом сезоне соты: {visited_cells},\n")
                        if len(message) + len(participant_info) > 1000:
                            # If it does, store the current message and start a new one
                            messages.append(message)
                            message = participant_info
                        else:
                            message += participant_info

                    if message:
                        messages.append(message)

                    for message in messages:
                        send_message(peer_id, message)
                else:
                    message = "Нет участников в марафоне."
                    send_message(peer_id, message)
            else:
                message = "У вас нет прав для выполнения этой команды."
                send_message(peer_id, message)

        # Добавить единорога. С пагинацией по 9 пользователей (ограничение vk 10. +кнопка "еще").
        # Сначала пользователю показывается список участников марафона (с пагинацией) - кнопки с пользователями формируются в функции def get_users_inline_buttons и пагинация callback "more".
        # Потом пользователь должен выбрать тип единорога из списка (без пагинации) - callback 'select_type_unicorn'
        # Дальше пользователь выбирает какую стадию единорога из списка - callback 'select_stage_unicorn' здесь возвращается id единорога для добавления
        # Потом callback 'add_unicorn' для добавления единорога и удаления юникоинов если нужно (coins) и опыта соответствующего типа(exp)
        elif command.lower().startswith('добавить единорога'):
            if user.get('admin', False):
                users = get_all_participants()
                page=0
                users_keyboard = get_users_inline_buttons(users, page,'select_type_unicorn')
                send_message(peer_id, "Выберите пользователя для добавления единорога (или яйца):", users_keyboard)
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Удалить единорога. С пагинацией по 4 пользователей (ограничение vk 10. +кнопка "еще").
        # Сначала пользователю показывается список участников марафона (с пагинацией) - кнопки с пользователями формируются в функции def get_users_inline_buttons и пагинация callback "more".
        # Потом пользователь должен выбрать стадия единорога из списка (без пагинации) - callback 'select_stage_uni_for_delete'
        # Дальше пользователь выбирает какую стадию единорога из списка - callback 'select_unicorn_for_delete' здесь возвращается id единорога для добавления
        # Потом callback 'delete_unicorn' для удаления единорога
        elif command.lower() == 'удалить единорога':
            if user.get('admin', False):
                users = get_all_participants()
                page = 0
                users_keyboard = get_users_inline_buttons(users, page, 'select_stage_uni_for_delete')
                response = send_message(peer_id, "Выберите пользователя для удаления единорога:", users_keyboard)
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")


        # Добавить артефакт. С пагинацией по 9 пользователей (ограничение vk 10. +кнопка "еще").
        # Сначала пользователю показывается список участников марафона (с пагинацией) - кнопки с пользователями формируются в функции def get_users_inline_buttons и пагинация callback "more".
        # Потом пользователь должен выбрать артефакт из списка (с пагинацией) - callback 'select_artefact_for_user' (пагинация callback "more")
        elif command.lower().startswith('добавить артефакт'):
            if user.get('admin', False):
                users = get_all_participants()
                page=0
                users_keyboard = get_users_inline_buttons(users, page,'select_artefact_for_user')
                send_message(peer_id, "Выберите пользователя для добавления артефакта:", users_keyboard)
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Удалить артефакт. С пагинацией по 9 пользователей (ограничение vk 10. +кнопка "еще").
        # Обработка команды удаления артефакта
        elif command.lower() == 'удалить артефакт':
            if user.get('admin', False):
                users = get_all_participants()
                page = 0
                users_keyboard = get_users_inline_buttons(users, page, 'select_user_for_deletion_art')
                response = send_message(peer_id, "Выберите пользователя для удаления артефакта:", users_keyboard)
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # пользователям добавляется отметка, что текущий сезон они завершили.
        # Следующий сезон такие пользователи могут начать без оплаты.
        elif command.lower().startswith('выбрать победителей'):
            if user.get('admin', False):
                users = get_all_participants()
                page=0
                users_keyboard = get_users_inline_buttons(users, page,'won_season')
                send_message(peer_id, "Выберите пользователей, которые завершили успешно сезон. Они смогут начать следующий сезон автоматически, без оплаты:", users_keyboard)
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")


        # Добавить юникоины
        elif command.lower().startswith('add_coins'):
            if user.get('admin', False):
                try:
                    _, user_id, coins = message.split()
                    add_coins = int(coins)

                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_id} не найден.")
                    else:
                        selected_user['coins'] += int(add_coins)
                        update_user(user_id, coins = selected_user['coins'])
                        response = send_message(peer_id, f"Пользователю ID: {user_id} добавлено {add_coins} юникоинов. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['coins']} юникоинов.")
                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'add_coins [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Вычесть юникоины
        elif command.lower().startswith('remove_coins'):
            if user.get('admin', False):
                try:
                    _, user_id, coins = message.split()
                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_id} не найден.")
                    elif selected_user['coins'] < int(coins):
                        response = send_message(peer_id, f"У пользователя с ID: {user_id} {selected_user['first_name']} не достаточно средств для выполнения операции. Текущий баланс юникоинов: {selected_user['coins']}.")
                    else:
                        selected_user['coins'] -= int(coins)
                        update_user(user_id, coins = selected_user['coins'])
                        response = send_message(peer_id, f"Пользователю ID: {user_id} удалено {coins} юникоинов. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['coins']} юникоинов.")
                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'remove_coins [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Задать новое значение для юникоинов
        elif command.lower().startswith('update_coins'):
            if user.get('admin', False):
                try:
                    _, user_id, coins = message.split()
                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_id} не найден.")
                    else:
                        selected_user['coins'] = int(coins)
                        update_user(user_id, coins = selected_user['coins'])
                        response = send_message(peer_id, f"Пользователю ID: {user_id} обновлен баланс юникоинов. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['coins']} юникоинов.")
                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'update_coins [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Задать опыт
        elif command.lower().startswith('add_exp'):
            if user.get('admin', False):
                try:
                    _, type_exp, user_exp_id, amount = message.split()

                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_exp_id)), None)

                    success_message = ''
                    notification_message = ''
                    nonsuccess_message = ''

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_exp_id} не найден.")
                    else:
                        if type_exp == 'eggs':
                            i = selected_user['exp_egg'] + int(amount)
                            selected_user['exp_egg'] += int(amount)
                            update_user(int(user_exp_id), exp_egg = i)
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {i} опыта для яиц."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} опыта для яиц. \n Теперь у вас есть {i} опыта для яиц."
                        if type_exp == 'boloto':
                            selected_user['exp_boloto'] += int(amount)
                            update_user(int(user_exp_id), exp_boloto = selected_user['exp_boloto'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального болотного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_boloto']} опыта для болотного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для болотного единорога. \n Теперь у вас есть {selected_user['exp_boloto']} уникального опыта для болотного единорога."
                        if type_exp == 'snow':
                            selected_user['exp_snow'] += int(amount)
                            update_user(int(user_exp_id), exp_snow = selected_user['exp_snow'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального снежного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_snow']} опыта для снежного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для снежного единорога. \n Теперь у вас есть {selected_user['exp_snow']} уникального опыта для снежного единорога."
                        if type_exp == 'les':
                            selected_user['exp_les'] += int(amount)
                            update_user(int(user_exp_id), exp_les = selected_user['exp_les'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального лесного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_les']} опыта для лесного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для лесного единорога. \n Теперь у вас есть {selected_user['exp_les']} уникального опыта для лесного единорога."
                        if type_exp == 'kamen':
                            selected_user['exp_kamen'] += int(amount)
                            update_user(int(user_exp_id), exp_kamen = selected_user['exp_kamen'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального каменного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_kamen']} опыта для каменного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для каменного единорога. Теперь у вас есть {selected_user['exp_kamen']} уникального опыта для каменного единорога."
                        if type_exp == 'pustyn':
                            selected_user['exp_pustyn'] += int(amount)
                            update_user(int(user_exp_id), exp_pustyn = selected_user['exp_pustyn'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального пустынного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_pustyn']} опыта для пустынного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для пустынного единорога. \n Теперь у вас есть {selected_user['exp_pustyn']} уникального опыта для пустынного единорога."
                        else:
                            nonsuccess_message = f"Пользователю ID: {user_exp_id} не удалось добавить опыт. Проверь, правильно ли указан тип опыта: egg, boloto, snow, les, kamen, pustyn."

                        if len(success_message) > 0:
                            response = send_message(peer_id, success_message)
                            send_message(user_exp_id, notification_message)
                        else:
                            response = send_message(peer_id, nonsuccess_message)

                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'add_exp [тип опыта] [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Обновить опыт
        elif command.lower().startswith('update_exp'):
            if user.get('admin', False):
                try:
                    _, type_exp, user_exp_id, amount = message.split()

                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_exp_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_exp_id} не найден.")
                    else:
                        if type_exp == 'egg':
                            selected_user['exp_egg'] = int(amount)
                            update_user(user_id, exp_egg = selected_user['exp_egg'])
                            success_message = f"Пользователю ID: {user_exp_id} обновлен уникальный опыт для яиц. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_egg']} опыта для яиц."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для яиц обновлен, теперь он равен {selected_user['exp_egg']}."
                        if type_exp == 'boloto':
                            selected_user['exp_boloto'] = int(amount)
                            update_user(user_id, exp_boloto = selected_user['exp_boloto'])
                            success_message = f"Пользователю ID: {user_exp_id} обновлен уникальный опыт для болотного единорога. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_boloto']} опыта для болотного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для болотного единорога обновлен, теперь он равен {selected_user['exp_boloto']}."
                        if type_exp == 'snow':
                            selected_user['exp_snow'] = int(amount)
                            update_user(user_id, exp_snow = selected_user['exp_snow'])
                            success_message = f"Пользователю ID: {user_exp_id} обновлен уникальный опыт для снежного единорога. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_snow']} опыта для снежного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для снежного единорога обновлен, теперь он равен {selected_user['exp_snow']}."
                        if type_exp == 'les':
                            selected_user['exp_les'] = int(amount)
                            update_user(user_id, exp_les = selected_user['exp_les'])
                            success_message = f"Пользователю ID: {user_exp_id} обновлен уникальный опыт для лесного единорога. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_les']} опыта для лесного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для лесного единорога обновлен, теперь он равен {selected_user['exp_les']}."
                        if type_exp == 'kamen':
                            selected_user['exp_kamen'] = int(amount)
                            update_user(user_id, exp_kamen = selected_user['exp_kamen'])
                            success_message = f"Пользователю ID: {user_exp_id} обновлен уникальный опыт для каменного единорога. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_kamen']} опыта для каменного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для каменного единорога обновлен, теперь он равен {selected_user['exp_kamen']}."
                        if type_exp == 'pustyn':
                            selected_user['exp_pustyn'] = int(amount)
                            update_user(user_id, exp_pustyn = selected_user['exp_pustyn'])
                            success_message = f"Пользователю ID: {user_exp_id} обновлен уникальный опыт для пустынного единорога. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_pustyn']} опыта для пустынного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для пустынного единорога обновлен, теперь он равен {selected_user['exp_pustyn']}."
                        else:
                            nonsuccess_message = f"Пользователю ID: {user_exp_id} не удалось обновить опыт. Проверь, правильно ли указан тип опыта: egg, boloto, snow, les, kamen, pustyn."

                        if success_message:
                            response = send_message(peer_id, success_message)
                            send_message(user_exp_id, notification_message)
                        else:
                            response = send_message(peer_id, nonsuccess_message)

                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'add_exp [тип опыта] [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")
            
        # Отменить последний ход на 1 соту
        elif message.startswith('revert_move'):
            admin_message = "Что-то пошло не так"
            if user.get('admin', False):
                try:
                    _, user_id = message.split()
                    previous_cell = revert_last_move(user_id)
                    
                    if previous_cell:
                        admin_message = f"Перемещение пользователя {user_id} отменено. Пользователь перемещен обратно на соту {previous_cell}."
                        user_message = f"Дивнолесье - это очень коварное место! Какой то злой дух переместил вас на другую соту, но наши защитники-кураторы вернули тебя в безопасное место на соту {previous_cell}."
                        send_message(user_id, user_message)
                    else:
                        admin_message = "Не удалось откатить перемещение. Путик еще не перемещался в этом сезоне."
                except Exception as e:
                    admin_message = "Произошла ошибка при обработке команды."
                    
            else:
                admin_message ="У вас нет прав для выполнения этой команды."
            
            response = send_message(peer_id, admin_message)



        # Любой другой случай
        else:
            keyboard = {
                    "inline": True,
                    "buttons": [
                        [{
                            "action": {
                                "type": "text",
                                "label": "старт"
                            }
                        }]
                    ]
                }
            if user:
                user_name = first_name + ' ' + last_name
                mention = f"[id{user_id}|{user_name}]"
            else:
                mention = "путник"
            response = send_message(peer_id, f"Привет, {mention}!  Напиши старт и я тебе помогу.", keyboard)


        return 'ok'

    elif data['type'] == 'message_event':
        payload = data['object']['payload']
        peer_id = data['object']['peer_id']
        user_id = data['object']['user_id']

        # команда принять участника в марафон
        if payload['action'] == 'accept':
            vk_id = payload['user_id']
            accept_marathon_request(vk_id, admin_id = peer_id)
            notify_admins_info(vk_id, f"Запрос на участие в марафоне от {vk_id} принят.")

        # команда отклонить участника в марафоне
        elif payload['action'] == 'reject':
            vk_id = payload['user_id']
            reject_marathon_request(vk_id)
            notify_admins_info(vk_id, f"Запрос на участие в марафоне от {vk_id} отклонен.")

        # Выбрать пользователя для артефакта
        elif payload['action'].lower().startswith('select_artefact_for_user'):
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                page = 0
                artefacts = load_artefacts()
                items_for_page, has_more = get_page(artefacts, page, 4)
                artefacts_keyboard = {
                    "inline": True,
                    "buttons": []
                }

                for artefact in items_for_page:
                    button = {"action": {"type":"callback",
                            "label":f"{artefact['name']}",
                            "payload": json.dumps({"action":"add_artefact","selected_user_id": selected_user_id,"artefact_id":artefact['id']})
                        }
                    }
                    artefacts_keyboard['buttons'].append([button])
                if has_more:
                    artefacts_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more","selected_user_id": selected_user_id,"list": "artefacts","page": page+1})}}])
                response = send_message(peer_id, "Выберите артефакт для добавления:", artefacts_keyboard)
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Выбор артефакта у пользователя, чтобы удалить артефакт
        elif payload['action'].lower() == 'select_user_for_deletion_art':
            selected_user_id = payload['selected_user_id']
            page = 0
            participants = get_all_participants()
            selected_user = next((u for u in participants if u['vk_id'] == selected_user_id), None)
            if selected_user:
                all_artefacts = load_artefacts()
                user_artefacts_ids = selected_user.get('artefacts', [])
                user_artefacts = []
                for artefact_id in user_artefacts_ids:
                    artefact = next((u for u in all_artefacts if u['id'] == artefact_id), None)
                    if artefact:
                        user_artefacts.append(artefact)
                items_for_page, has_more = get_page(user_artefacts, page, 4)
                artefacts_keyboard = {
                    "inline": True,
                    "buttons": []
                }

                for artefact in items_for_page:
                    button = {"action": {"type":"callback",
                            "label":f"{artefact['name']}",
                            "payload": json.dumps({"action":"delete_artefact","selected_user_id": selected_user_id,"artefact_id":artefact['id']})
                        }
                    }
                    artefacts_keyboard['buttons'].append([button])
                if has_more:
                    artefacts_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more", "selected_user_id": selected_user_id, "list": "artefacts", "page": page+1})}}])

                response = send_message(peer_id, f"Выберите артефакт для удаления у пользователя ID: {selected_user_id}:", artefacts_keyboard)

        # Выбрать тип единорога для добавления пользователю
        elif payload['action'].lower().startswith('select_type_unicorn'):
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                unicorn_keyboard = {
                    "inline": True,
                    "buttons":[
                        [{"action":{"type":"callback","label":"Каменный","payload": json.dumps({"action":"select_stage_unicorn","selected_user_id": selected_user_id,"unicorn_type": "kamen"})}},
                        {"action":{"type":"callback","label":"Снежный","payload": json.dumps({"action":"select_stage_unicorn","selected_user_id": selected_user_id,"unicorn_type": "snow"})}}],
                        [{"action":{"type":"callback","label":"Пустынный","payload": json.dumps({"action":"select_stage_unicorn","selected_user_id": selected_user_id,"unicorn_type": "pustyn"})}},
                        {"action":{"type":"callback","label":"Лесной","payload": json.dumps({"action":"select_stage_unicorn","selected_user_id": selected_user_id,"unicorn_type": "les"})}}],
                        [{"action":{"type":"callback","label":"Болотный","payload": json.dumps({"action":"select_stage_unicorn","selected_user_id": selected_user_id,"unicorn_type": "boloto"})}},
                        {"action":{"type":"callback","label":"Королевский","payload": json.dumps({"action":"select_stage_unicorn","selected_user_id": selected_user_id,"unicorn_type": "king"})}}]
                        ]
                }

                response = send_message(peer_id, "Выберите тип единорога( или яйца) для добавления:", unicorn_keyboard)
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Выбрать стадию единорога (дальше вызывается функция добавления и подтверждения добавления)
        elif payload['action'].lower().startswith('select_stage_unicorn'):
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                unicorn_type = payload['unicorn_type']
                unicorns = load_unicorns()
                filtered_unicorns = [unicorn for unicorn in unicorns if unicorn['type'] == unicorn_type]
                unicorn_keyboard = {
                    "inline": True,
                    "buttons": []
                }
                for unicorn in filtered_unicorns:
                    button = {
                        "action": {
                            "type": "callback",
                            "label": f"{unicorn['name']}",
                            "payload": json.dumps({
                                "action": "add_unicorn",
                                "selected_user_id": selected_user_id,
                                "unicorn_id": unicorn['id']
                            })
                        }
                    }
                    unicorn_keyboard['buttons'].append([button])
                response = send_message(peer_id, "Выберите тип единорога( или яйца) для добавления:", unicorn_keyboard)
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # отобразить больше пользователей или артефактов
        elif payload['action'].lower().startswith('more'):
            if payload['list'] == "users":
                users = get_all_participants()
                page = int(payload['page'])
                action_call = payload['action_call']
                users_keyboard = get_users_inline_buttons(users, page, action_call)
                if action_call == "select_artefact_for_user":
                    response = send_message(peer_id, "Выберите пользователя для добавления артефакта:", users_keyboard)
                elif action_call == "select_user_for_deletion_art":
                    response = send_message(peer_id, "Выберите пользователя для удаления артефакта:", users_keyboard)
                elif action_call == "select_stage_uni_for_delete":
                    response = send_message(peer_id, "Выберите пользователя для удаления единорога (или яйца):", users_keyboard)
                elif action_call == "select_type_unicorn":
                    response = send_message(peer_id, "Выберите пользователя для добавления единорога (или яйца):", users_keyboard)
                elif action_call == "won_season":
                    response = send_message(peer_id, "Выберите пользователей, кто завершил успешно текущий сезон:", users_keyboard)
                else:
                    response = send_message(peer_id, "Выберите пользователя:", users_keyboard)
            elif payload['list'] == "artefacts":
                selected_user_id = payload['selected_user_id']
                page = payload['page']
                artefacts = load_artefacts()
                items_for_page, has_more = get_page(artefacts, page, 4)
                artefacts_keyboard = {
                    "inline": True,
                    "buttons": []
                }

                for artefact in items_for_page:
                    button = {"action": {"type":"callback",
                            "label":f"{artefact['name']}",
                            "payload": json.dumps({"action":"add_artefact","selected_user_id": selected_user_id,"artefact_id":artefact['id']})
                        }
                    }
                    artefacts_keyboard['buttons'].append([button])
                if has_more:
                    artefacts_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more", "selected_user_id": selected_user_id,"list": "artefacts", "page": page+1})}}])
                response = send_message(peer_id, "Выберите артефакт для добавления:", artefacts_keyboard)
            elif payload['list'] == "users_add_artefact":
                users = get_all_participants()
                page=payload['page']
                users_keyboard = get_users_inline_buttons(users, page,'select_artefact_for_user')
                response = send_message(peer_id, "Выберите пользователя для добавления артефакта:", users_keyboard)
            elif payload['list'] == "users_delete_artefact":
                users = get_all_participants()
                page=payload['page']
                users_keyboard = get_users_inline_buttons(users, page,'select_user_for_deletion_art')
                response = send_message(peer_id, "Выберите пользователя для добавления артефакта:", users_keyboard)
            elif payload['list'] == "artefacts_delete":
                selected_user_id = payload['selected_user_id']
                participants = get_all_participants()
                selected_user = next((u for u in participants if u['vk_id'] == selected_user_id), None)
                page = payload['page']
                artefacts = load_artefacts()
                if selected_user:
                    all_artefacts = load_artefacts()
                    user_artefacts = [a for a in all_artefacts if a['id'] in selected_user.get('artefacts', [])]
                    items_for_page, has_more = get_page(user_artefacts, page, 4)
                    page = int(payload['page'])
                    artefacts_keyboard = {
                        "inline": True,
                        "buttons": []
                    }

                    for artefact in items_for_page:
                        button = {"action": {"type":"callback",
                                "label":f"{artefact['name']}",
                                "payload": json.dumps({"action":"delete_artefact","selected_user_id": selected_user_id,"artefact_id":artefact['id']})
                            }
                        }
                        artefacts_keyboard['buttons'].append([button])
                    if has_more:
                        artefacts_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more", "selected_user_id": selected_user_id, "list": "artefacts_delete", "page": page+1})}}])

                response = send_message(peer_id, f"Выберите артефакт для удаления у пользователя {selected_user['first_name']} {selected_user['last_name']}:", artefacts_keyboard)
            elif payload['list'] == "unicorns_delete":
                selected_user_id = payload['selected_user_id']
                stage = payload['stage']
                participants = get_all_participants()
                selected_user = next((u for u in participants if u['vk_id'] == selected_user_id), None)
                if selected_user:
                    all_unicorns = load_unicorns()
                    user_unicorns_ids = selected_user.get(stage, [])
                    user_unicorns = []
                    for unicorn_id in user_unicorns_ids:
                        unicorn = next((u for u in all_unicorns if u['id'] == unicorn_id), None)
                        if unicorn:
                            user_unicorns.append(unicorn)
                    page = int(payload['page'])
                    items_for_page, has_more = get_page(user_unicorns, page, 4)
                    unicorns_keyboard = {
                        "inline": True,
                        "buttons": []
                    }

                    for unicorn in items_for_page:
                        button = {"action": {"type":"callback",
                                "label":f"{unicorn['name']}",
                                "payload": json.dumps({"action":"delete_unicorn","selected_user_id": selected_user_id,"unicorn_id":unicorn['id']})
                            }
                        }
                        unicorns_keyboard['buttons'].append([button])
                    if has_more:
                        unicorns_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more", "selected_user_id": selected_user_id, "list": "unicorns_delete", "page": page+1, "stage": stage})}}])

                response = send_message(peer_id, f"Выберите единорога для удаления у пользователя {selected_user['first_name']} {selected_user['last_name']}:", unicorns_keyboard)
            else:
                response = send_message(peer_id, "Что-то пошло не так. (Данные об ошибке elif payload['action'].lower().startswith('more'))")
                logger.info("В функции возврата инлайн кнопок не удалось определить какой список надо вернуть")
            


        # Добавить выбранный артефакт выбранному пользователю
        elif payload['action'].lower().startswith('add_artefact'):
            user = get_user(user_id)
            message = ""
            user_message = ""
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                artefact_id = payload['artefact_id']

                all_artefacts = load_artefacts()
                artefact = next((a for a in all_artefacts if a['id'] == artefact_id), None)
                if artefact:
                    artefact_price = artefact['price']
                    selected_user = next((u for u in get_all_participants() if u['vk_id'] == selected_user_id), None)

                    if selected_user['coins'] >= artefact_price:
                        selected_user['coins'] -= artefact_price
                        add_artefact_to_user(selected_user_id, artefact_id)
                        update_user(selected_user_id, coins=selected_user['coins'])
                        message = f"Артефакт '{artefact['name']}' успешно добавлен пользователю {selected_user['last_name']}. Осталось юникоинов: {selected_user['coins']}."
                        user_message = f"Вы стали обладателем артефакта: '{artefact['name']}'. Пришлось отдать {artefact_price} юникоинов, но оно того стоило! Осталось юникоинов: {selected_user['coins']}."
                    else:
                        message = f"У пользователя {selected_user['first_name']} {selected_user['last_name']} недостаточно средств для покупки артефакта '{artefact['name']}'. Необходимо: {artefact_price}, доступно: {selected_user['coins']}."
                else:
                    message = "Что-то пошло не так и мы потеряли артефакт. Пора обратиться к Саше."

            else:
                message = "У вас нет прав для выполнения этой команды."

            send_message(peer_id, message)
            if len(user_message) > 0:
                send_message(selected_user_id, user_message)

        # удалить артефакт у пользователя
        elif payload['action'].lower().startswith('delete_artefact'):
            user = get_user(user_id)
            selected_user_id = payload['selected_user_id']
            message = ""
            user_message = ""
            if user.get('admin', False):
                artefact_id = payload['artefact_id']

                selected_user = next((u for u in get_all_participants() if u['vk_id'] == selected_user_id), None)
                all_artefacts = load_artefacts()
                artefact = next((a for a in all_artefacts if a['id'] == artefact_id), None)
                if artefact:
                    remove_artefact_from_user(selected_user_id, artefact_id)
                    message = f"Артефакт '{artefact['name']}' успешно удален у пользователя {selected_user['first_name']} {selected_user['last_name']}."
                    user_message = f"Вы использовали артефакт '{artefact['name']}' и он был удален из вашего инвентаря."

            else:
                message = "У вас нет прав для выполнения этой команды."

            send_message(peer_id, message)
            if len(user_message) > 0:
                send_message(selected_user_id, user_message)

        # Добавить выбранного единорога выбранному пользователю
        elif payload['action'].lower().startswith('add_unicorn'):
            user = get_user(user_id)
            message = 'enter'
            selected_user_id = payload['selected_user_id']
            user_message = ''
            if user.get('admin', False):
                unicorn_id = payload['unicorn_id']

                selected_user = next((u for u in get_all_participants() if u['vk_id'] == selected_user_id), None)

                all_unicorns = load_unicorns()
                unicorn = next((a for a in all_unicorns if a['id'] == unicorn_id), None)
                if unicorn:
                    unicorn_stage = unicorn['stage']
                    unicorn_type = unicorn['type']

                    if unicorn_stage == 'eggs':
                        add_unicorn_to_user(selected_user_id, 'eggs', unicorn_id)
                        message =  f"{unicorn['name']} было успешно добавлено {selected_user['first_name']} {selected_user['last_name']}."
                        user_message =  f"Вам в руки попала редкая находка {unicorn['name']}. Если правильно за ней ухаживать и оберегать, то можно получить верного друга - Дивнолестного Единорога! Удачного путешествия с вашим новым питомцем!"

                    elif unicorn_stage == 'unicorns_baby':
                        if unicorn['type'] == 'king':
                            add_unicorn_to_user(selected_user_id, 'unicorns_baby', unicorn_id) # добавляем единорога
                            message =  f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}."
                            user_message =  f"Поздравляем с пополнением! У вас появился {unicorn['name']}. Это очень редкий зверь! Удачного путешествия с вашим новым питомцем!"
                        else:
                            if selected_user['exp_egg'] >= unicorn['price_exp']:
                                selected_user['exp_egg'] -= unicorn['price_exp']
                                update_user(selected_user_id, exp_egg=selected_user['exp_egg']) # Удаляем опыт для яиц у пользователя
                                all_users_eggs = get_users_unicorns(selected_user_id, stage = 'eggs') # Получаем список всех яиц у пользователя
                                egg_id_for_remove = next((u for u in all_users_eggs if all_unicorns[u-1]['type'] == unicorn_type), None) # Выбираем любое первое яйцо с типом как у добавляемого единорога у пользователя
                                unicorn_removed = remove_unicorn_from_user(selected_user_id, 'eggs', egg_id_for_remove) # удаляем выбранное яйцо в замен добавляемому единорогу
                                add_unicorn_to_user(selected_user_id, 'unicorns_baby', unicorn_id) # добавляем единорога
                                message =  f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}. Был снят опыт в размере {unicorn['price_exp']}."
                                if unicorn_removed:
                                    message += f" Так же у пользователя было изъято одно яйцо единорога {unicorn['type']}."
                                else: 
                                    message += f" Не удалось удалить яйцо."
                                user_message =  f"Поздравляем с пополнением! У вас появился {unicorn['name']}. Теперь ваш новый друг будет путешествовать с вам по Дивнолесью и позволять брать 2-ую тему соты. Вам пришлось заплатить опытом в размере {unicorn['price_exp']}, но не печальтесь, ведь новый друг того стоит. Удачного путешествия с вашим новым питомцем!"
                            else:
                                message = f"У пользователя недостаточно опыта для вылупления единорога. Сейчас у пользователя имеется {selected_user['exp_egg']} опыта, а стоимость единорога {unicorn['price_exp']}."

                    elif unicorn_stage == 'unicorns':
                        if unicorn['type'] == 'king':
                            add_unicorn_to_user(selected_user_id, 'unicorns', unicorn_id) # добавляем единорога
                            message = f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}."
                            user_message = f"ОГО! Поздравляем, ваш лучший друг {unicorn['name']} совсем взрослый и готов к путешествию!"
                        else:
                            if selected_user['coins'] >= unicorn['price_coins']:

                                if unicorn_type == 'kamen':
                                    if selected_user['exp_kamen'] >= unicorn['price_exp']:
                                        selected_user['coins'] -= unicorn['price_coins']
                                        selected_user['exp_kamen'] -= unicorn['price_exp']
                                        update_user(selected_user_id, coins=selected_user['coins'], exp_kamen = selected_user['exp_kamen']) # Удаляем юникоины за взрослого единорога у пользователя

                                        all_users_baby_u = get_users_unicorns(selected_user_id, stage = 'unicorns_baby') # Получаем список всех яиц у пользователя
                                        baby_id_for_remove = next((u for u in all_users_baby_u if all_unicorns[u-1]['type'] == unicorn_type), None)# Выбираем любого первого единорога 1 стадии с типом как у добавляемого единорога у пользователя
                                        remove_unicorn_from_user(selected_user_id, 'unicorns_baby', baby_id_for_remove) # удаляем выбранное яйцо в замен добавляемому единорогу

                                        add_unicorn_to_user(selected_user_id, 'unicorns', unicorn_id) # добавляем единорога

                                        message = f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}. Так же у пользователя было изъят единорог 1 стадии {unicorn['type']}, 50 юникоинов и был снят опыт в размере {unicorn['price_exp']}."
                                        user_message = f"Поздравляем, ваш {unicorn['name']} вырос! Теперь вы сможете брать 3-юю тему соты. За транспортировку было отдано - 50 юникоинов, а также был снят уникальный опыт в размере {unicorn['price_exp']}. Удачного путешествия с подросшим другом!"
                                    else:
                                        message = f"У {selected_user['first_name']} {selected_user['last_name']} недостаточно опыта для добавления единорога. Сейчас у пользователя - {selected_user[exp_kameen]} каменного уникального опыта , а требуется  15 уникального опыта."
                                elif unicorn_type == 'boloto':
                                    if selected_user['exp_boloto'] >= unicorn['price_exp']:
                                        selected_user['coins'] -= unicorn['price_coins']
                                        selected_user['exp_boloto'] -= unicorn['price_exp']
                                        update_user(selected_user_id, coins=selected_user['coins'], exp_boloto = selected_user['exp_boloto']) # Удаляем юникоины за взрослого единорога у пользователя

                                        all_users_baby_u = get_users_unicorns(selected_user_id, stage = 'unicorns_baby') # Получаем список всех яиц у пользователя
                                        baby_id_for_remove = next((u for u in all_users_baby_u if all_unicorns[u-1]['type'] == unicorn_type), None)# Выбираем любого первого единорога 1 стадии с типом как у добавляемого единорога у пользователя
                                        remove_unicorn_from_user(selected_user_id, 'unicorns_baby', baby_id_for_remove) # удаляем выбранное яйцо в замен добавляемому единорогу

                                        add_unicorn_to_user(selected_user_id, 'unicorns', unicorn_id) # добавляем единорога

                                        message = f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}. Так же у пользователя было изъят единорог 1 стадии {unicorn['type']}, 50 юникоинов и был снят опыт в размере {unicorn['price_exp']}."
                                        user_message = f"Поздравляем, ваш {unicorn['name']} вырос! Теперь вы сможете брать 3-юю тему соты. За транспортировку было отдано - 50 юникоинов, а также был снят уникальный опыт в размере {unicorn['price_exp']}. Удачного путешествия с подросшим другом!"
                                    else:
                                        message = f"У {selected_user['first_name']} {selected_user['last_name']} недостаточно опыта для добавления единорога. Сейчас у пользователя - {selected_user[exp_boloto]} болотного уникального опыта , а требуется 15 уникального опыта."
                                elif unicorn_type == 'pustyn':
                                    if selected_user['exp_pustyn'] >= unicorn['price_exp']:
                                        selected_user['coins'] -= unicorn['price_coins']
                                        selected_user['exp_pustyn'] -= unicorn['price_exp']
                                        update_user(selected_user_id, coins=selected_user['coins'], exp_pustyn = selected_user['exp_pustyn']) # Удаляем юникоины за взрослого единорога у пользователя

                                        all_users_baby_u = get_users_unicorns(selected_user_id, stage = 'unicorns_baby') # Получаем список всех яиц у пользователя
                                        baby_id_for_remove = next((u for u in all_users_baby_u if all_unicorns[u-1]['type'] == unicorn_type), None)# Выбираем любого первого единорога 1 стадии с типом как у добавляемого единорога у пользователя
                                        remove_unicorn_from_user(selected_user_id, 'unicorns_baby', baby_id_for_remove) # удаляем выбранное яйцо в замен добавляемому единорогу

                                        add_unicorn_to_user(selected_user_id, 'unicorns', unicorn_id) # добавляем единорога

                                        message = f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}. Так же у пользователя было изъят единорог 1 стадии {unicorn['type']}, 50 юникоинов и был снят опыт в размере {unicorn['price_exp']}."
                                        user_message = f"Поздравляем, ваш {unicorn['name']} вырос! Теперь вы сможете брать 3-юю тему соты. За транспортировку было отдано - 50 юникоинов, а также был снят уникальный опыт в размере {unicorn['price_exp']}. Удачного путешествия с подросшим другом!"
                                    else:
                                        message = f"У {selected_user['first_name']} {selected_user['last_name']} недостаточно опыта для добавления единорога. Сейчас у пользователя - {selected_user[exp_pustyn]} пустынного уникального опыта , а требуется  15 уникального опыта."
                                elif unicorn_type == 'les':
                                    if selected_user['exp_les'] >= unicorn['price_exp']:
                                        selected_user['coins'] -= unicorn['price_coins']
                                        selected_user['exp_les'] -= unicorn['price_exp']
                                        update_user(selected_user_id, coins=selected_user['coins'], exp_les = selected_user['exp_les']) # Удаляем юникоины за взрослого единорога у пользователя

                                        all_users_baby_u = get_users_unicorns(selected_user_id, stage = 'unicorns_baby') # Получаем список всех яиц у пользователя
                                        baby_id_for_remove = next((u for u in all_users_baby_u if all_unicorns[u-1]['type'] == unicorn_type), None)# Выбираем любого первого единорога 1 стадии с типом как у добавляемого единорога у пользователя
                                        remove_unicorn_from_user(selected_user_id, 'unicorns_baby', baby_id_for_remove) # удаляем выбранное яйцо в замен добавляемому единорогу

                                        add_unicorn_to_user(selected_user_id, 'unicorns', unicorn_id) # добавляем единорога

                                        message = f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}. Так же у пользователя было изъят единорог 1 стадии {unicorn['type']}, 50 юникоинов и был снят опыт в размере {unicorn['price_exp']}."
                                        user_message = f"Поздравляем, ваш {unicorn['name']} вырос! Теперь вы сможете брать 3-юю тему соты. За транспортировку было отдано - 50 юникоинов, а также был снят уникальный опыт в размере {unicorn['price_exp']}. Удачного путешествия с подросшим другом!"
                                    else:
                                        message = f"У {selected_user['first_name']} {selected_user['last_name']} недостаточно опыта для добавления единорога. Сейчас у пользователя - {selected_user['exp_les']} лесного уникального опыта , а требуется  15 уникального опыта."
                                elif unicorn_type == 'snow':
                                    if selected_user['exp_snow'] >= unicorn['price_exp']:
                                        selected_user['coins'] -= unicorn['price_coins']
                                        selected_user['exp_snow'] -= unicorn['price_exp']
                                        update_user(selected_user_id, coins=selected_user['coins'], exp_snow = selected_user['exp_snow']) # Удаляем юникоины за взрослого единорога у пользователя

                                        all_users_baby_u = get_users_unicorns(selected_user_id, stage = 'unicorns_baby') # Получаем список всех яиц у пользователя
                                        baby_id_for_remove = next((u for u in all_users_baby_u if all_unicorns[u-1]['type'] == unicorn_type), None)# Выбираем любого первого единорога 1 стадии с типом как у добавляемого единорога у пользователя
                                        remove_unicorn_from_user(selected_user_id, 'unicorns_baby', baby_id_for_remove) # удаляем выбранное яйцо в замен добавляемому единорогу

                                        add_unicorn_to_user(selected_user_id, 'unicorns', unicorn_id) # добавляем единорога

                                        message = f"Единорог {unicorn['name']} был успешно добавлен {selected_user['first_name']} {selected_user['last_name']}. Так же у пользователя было изъят единорог 1 стадии {unicorn['type']}, 50 юникоинов и был снят опыт в размере {unicorn['price_exp']}."
                                        user_message = f"Поздравляем, ваш {unicorn['name']} вырос! Теперь вы сможете брать 3-юю тему соты. За транспортировку было отдано - 50 юникоинов, а также был снят уникальный опыт в размере {unicorn['price_exp']}. Удачного путешествия с подросшим другом!"
                                    else:
                                        message = f"У {selected_user['first_name']} {selected_user['last_name']} недостаточно опыта для добавления единорога. Сейчас у пользователя - {selected_user[exp_snow]} снежного уникального опыта , а требуется  15 уникального опыта."
                                else:
                                    message = 'Упс, ошибка, не удалось определить тип единорога. Обратись к Саше, пусть исправляет.'
                            else:
                                message = f"У пользователя недостаточно юникоинов для взросления единорога. Сейчас у пользователя имеется {selected_user['coins']} юникоинов, а стоимость единорога {unicorn['price_coins']}."
                    else:
                        message =  "Стадия единорога не определена."
                else:
                    message =  "Тип единорога не определен."
            else:
                message =  "У вас нет прав для выполнения этой команды."

            send_message(peer_id, message)
            if len(user_message) > 0:
                send_message(selected_user_id, user_message)

        # Выбор стадии единорога для удаления
        elif payload['action'].lower() == 'select_stage_uni_for_delete':
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                stage_keyboard = {
                    "inline": True,
                    "buttons":[
                        [{"action":{"type":"callback","label":"Яйцо","payload": json.dumps({"action":"select_unicorn_for_delete","selected_user_id": selected_user_id,"page": 0,"stage": "eggs"})}}],
                        [{"action":{"type":"callback","label":"2 стадия","payload": json.dumps({"action":"select_unicorn_for_delete","selected_user_id": selected_user_id,"page": 0,"stage": "unicorns_baby"})}}],
                        [{"action":{"type":"callback","label":"Взрослый - 3 стадия","payload": json.dumps({"action":"select_unicorn_for_delete","selected_user_id": selected_user_id,"page": 0,"stage": "unicorns"})}}]
                        ]
                }

                send_message(peer_id, "Выберите тип единорога( или яйца) для удаления:", stage_keyboard)
            else:
                send_message(peer_id, "У вас недостаточно прав для этого действия.")


        # Выбор единорога у пользователя, чтобы удалить
        elif payload['action'].lower() == 'select_unicorn_for_delete':
            selected_user_id = payload['selected_user_id']
            page = int(payload['page'])
            stage = payload['stage']
            participants = get_all_participants()
            selected_user = next((u for u in participants if u['vk_id'] == selected_user_id), None)
            if selected_user:
                all_unicorns = load_unicorns()
                user_unicorns_ids = selected_user.get(stage, [])
                user_unicorns = []
                for unicorn_id in user_unicorns_ids:
                    unicorn = next((u for u in all_unicorns if u['id'] == unicorn_id), None)
                    if unicorn:
                        user_unicorns.append(unicorn)
                items_for_page, has_more = get_page(user_unicorns, page, 4)
                unicorns_keyboard = {
                    "inline": True,
                    "buttons": []
                }

                for unicorn in items_for_page:
                    button = {"action": {"type":"callback",
                            "label":f"{unicorn['name']}",
                            "payload": json.dumps({"action":"delete_unicorn","selected_user_id": selected_user_id,"unicorn_id":unicorn['id']})
                        }
                    }
                    unicorns_keyboard['buttons'].append([button])
                if has_more:
                    unicorns_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more", "selected_user_id": selected_user_id, "list": "unicorns_delete", "page": 1, "stage": stage})}}])

                response = send_message(peer_id, f"Выберите единорога для удаления у пользователя {selected_user['first_name']} {selected_user['last_name']}:", unicorns_keyboard)

        # удалить единорога у пользователя
        elif payload['action'].lower().startswith('delete_unicorn'):
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                unicorn_id = payload['unicorn_id']

                selected_user = next((u for u in get_all_participants() if u['vk_id'] == selected_user_id), None)
                all_unicorns = load_unicorns()
                unicorn = next((a for a in all_unicorns if a['id'] == unicorn_id), None)
                stage = unicorn['stage']
                if unicorn:
                    remove_unicorn_from_user(selected_user_id, stage, unicorn_id)
                    send_message(peer_id, f"{unicorn['name']} успешно удален у пользователя {selected_user['first_name']} {selected_user['last_name']}.")

            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # добавить пользователю сезон как успешно завершенный
        elif payload['action'].lower().startswith('won_season'):
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                selected_user = next((u for u in get_all_participants() if u['vk_id'] == selected_user_id), None)
                update_user(selected_user_id, won_season = True)

                message = f"Путник {selected_user['first_name']} {selected_user['last_name']} успешно завершил(-а) текущий сезон!"
                user_message = f"Поздравляем! Вы успешно завершили текущий сезон! Вы примите участие в разыгрыше Дивнолесных даров! А также совершенно бесплатно сможете продолжить свое путешествие в следующем сезоне! Очень ждем от вас новых отчетов! Удачи, дорогой путник!"
            else:
                message = "У вас нет прав для выполнения этой команды."

            send_message(peer_id, message)
            if user_message:
                send_message(selected_user_id, user_message)

        return 'ok'

    else:
        return 'ok'

    return 'not found', 404

# Инфа о пользователе от вк
def get_user_info(user_id):
    api_url = 'https://api.vk.com/method/users.get'
    params = {
        'user_ids': user_id,
        'access_token': token,
        'v': '5.131'
    }
    response = requests.get(api_url, params=params)
    response_data = response.json()
    if 'response' in response_data:
        return response_data['response'][0]
    return None

# Отправка сообщения в ВК
def send_message(peer_id, message, keyboard = None):
    api_url = 'https://api.vk.com/method/messages.send'
    params = {
        'peer_id': peer_id,
        'random_id': 0,
        'message': message,
        'access_token': token,
        'v': '5.131'
    }
    if keyboard:
        params['keyboard'] = json.dumps(keyboard, ensure_ascii=False)
    response = requests.post(api_url, params=params)
    return response.json()

# Функция для отправки файла через VK API
def send_file(peer_id, file_path):
    url = 'https://api.vk.com/method/docs.getMessagesUploadServer'
    params = {
        'peer_id': peer_id,
        'type': 'doc',
        'access_token': token,
        'v': '5.131'
    }

    response = requests.get(url, params=params).json()
    upload_url = response['response']['upload_url']

    with open(file_path, 'rb') as file:
        response = requests.post(upload_url, files={'file': file}).json()

    file_info = response['file']

    save_url = 'https://api.vk.com/method/docs.save'
    save_params = {
        'file': file_info,
        'title': os.path.basename(file_path),
        'access_token': token,
        'v': '5.131'
    }

    save_response = requests.get(save_url, params=save_params).json()
    doc = save_response['response']['doc']
    attachment = f"doc{doc['owner_id']}_{doc['id']}"

    message_params = {
        'peer_id': peer_id,
        'random_id': 0,
        'message': 'Список участников:',
        'attachment': attachment,
        'access_token': token,
        'v': '5.131'
    }

    message_response = requests.get('https://api.vk.com/method/messages.send', params=message_params).json()
    logger.info(f"Sent file: {message_response}")


if __name__ == '__main__':
    app.run()
