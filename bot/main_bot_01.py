from flask import Flask, request
import requests
import logging
import json
import os
import random

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

def load_local_data():
    try:
        with open(JSON_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("25 Local JSON file not found.")
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

# ПАГИНАЦИЯ Универсальная функция для получения данных по страницам.
def get_page(data, page, page_size=8):
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
def add_user(vk_id, first_name='Неизвестно', last_name='', is_participant=False, current_cell=None, kurator = None):
    users = load_users()
    user = {
        "vk_id": vk_id,
        "first_name": first_name,
        "last_name": last_name,
        "is_participant": is_participant,
        "kurator": kurator,
        "current_cell": current_cell,
        "visited_cells": {str(load_info_marathon()['current_season']): [current_cell]},
        "admin": False,
        "artifacts": [],
        "coins": 0,
        "eggs":{},
        "unicorns-baby":{},
        "unicorns":{},
        "exp_egg": 0,
        "exp_boloto": 0,
        "exp_snow": 0,
        "exp_les": 0,
        "exp_kamen": 0,
        "exp_pustyn": 0
    }
    users.append(user)
    save_users(users)

# Функция для обновления данных пользователя
def update_user(vk_id, first_name=None, last_name=None, is_participant=None, current_cell=None, coins=None, kurator=None, exp_egg=None, exp_boloto=None, exp_snow=None, exp_les=None, exp_kamen=None, exp_pustyn=None):
    users = load_users()
    info_marathon = load_info_marathon()
    current_season = str(info_marathon.get('current_season', "1"))
    logger.info('1 Обновляем пользователя %s', current_season)

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
                if current_cell not in user['visited_cells'][current_season]:
                    user['visited_cells'][current_season].append(current_cell)
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
            break
    save_users(users)

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


# Функция возвращает пагинированный список пользователей в inline-кнопках
def get_users_inline_buttons(users, page=0, action='select_artefact_for_user'):
    items_for_page, has_more = get_page(users, page)
    users_keyboard = {
            "inline": True,
            "buttons": []
        }
    for u in items_for_page:
        users_keyboard['buttons'].append([{"action": {
            "type": "callback",
            "label": f"{u['first_name']} {u['last_name']}",
            "payload": json.dumps({"action":action,"selected_user_id":u['vk_id'],"page":page})}}])
    if has_more:
        users_keyboard['buttons'].append([{"action": {"type": "callback", "label": "Ещё", "payload": json.dumps({"action": "more","list":"users","page": page+1})}}])

    return users_keyboard

# Артефакты
# Функция для добавления артефакта пользователю
def add_artefact_to_user(user_id, artefact_id):
    users = load_users()
    for user in users:
        if user['vk_id'] == user_id:
            if 'artifacts' not in user:
                user['artifacts'] = []
            user['artifacts'].append(artefact_id)
            break
    save_users(users)

# Удаление артефакта у пользователя
def remove_artefact_from_user(user_id, artefact_id):
    users = load_users()
    for user in users:
        if user['vk_id'] == user_id:
            user['artifacts'] = [a for a in user['artifacts'] if a != artefact_id]
            break
    save_users(users)

# Функция для загрузки данных артефактов из файла
def load_artefacts():
    if os.path.exists(ARTEFACTS_FILE):
        with open(ARTEFACTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

# Функция для загрузки данных марафона из файла
def load_info_marathon():
    if os.path.exists(INFO_MARATHON_FILE):
        with open(INFO_MARATHON_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {"hi":"Обратись к Кураторам за паролем."}

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

# Подтверждение перемещения пользователя MOVE
def notify_admins_move(user_id, current_cell, cell, first_name = "", last_name = ""):
    users = load_users()
    admins = [user for user in users if user.get('admin', False)]
    confirmation_message = f"Пользователь {first_name} {last_name} ({user_id}) хочет переместиться с соты {current_cell} в соту {cell}. Подтвердите перемещение."
    keyboard = {
        "inline": True,
        "buttons": [
            [{"action": {"type": "callback", "label": "Принять", "payload": json.dumps({"action": "confirm_move", "user_id": user_id, "cell": cell})}},
            {"action": {"type": "callback", "label": "Отклонить", "payload": json.dumps({"action": "reject_move", "user_id": user_id, "cell": cell})}}]
        ]
    }
    for admin in admins:
        send_message(admin['vk_id'], confirmation_message, keyboard)

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
        # Выбираем случайное значение для current_cell из cells_data. Удалила на первый сезон
        # current_cell = random.choice([cell['name'] for cell in cells_data])

        # Добавляем нового пользователя
        add_user(vk_id, first_name, last_name, is_participant=True, kurator = admin_id)
        send_message(vk_id, f"Вы успешно зарегистрированы в марафоне Дивнолесье! Удачи! \n Ссылка на карту: {link} \n Логин: {login}\n Пароль: {password}")

def reject_marathon_request(vk_id):
    send_message(vk_id, "Упс, что-то случилось и мы не смогли зарегистрировать вас в марафоне Дивнолесье. Свяжитесь с кураторами марафона.")



@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logger.info("WEBHOOK")

    if data['type'] == 'confirmation':
        return '72551265'

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

        logger.info(f"54 Processed command: {command}")

        # список команд простых смертых
        if command.lower() == 'старт' or not message:
            if user_info_vk:
                user_name = first_name + ' ' + last_name
                mention = f"[id{user_id}|{user_name}]"
                welcome_message = f"Привет, {mention}! Я бот Дивнолесья. Я могу помочь тебе в твоем путешествии и расскажу о каждой соте. \n" \
                            "Доступные команды:\n" \
                               "- 'info [номер соты]': я расскажу тебе об этой соте. Например: 'info A1'.\n" \
                               "- 'move [номер соты]': отправлю запрос Куратору на перемещение тебя в указанную соту. Например: 'move A1'.\n" \
                               "- 'профиль': я расскажу тебе на какой соте ты находишься и какие соты уже прошел (только для участников).\n" \
                               "- 'about': информация о марафоне Дивнолесье.\n" \
                               "- 'участвую': заявка на участие в марафоне. \n" \
                               "- 'старт': Если ты потеряешься, напиши старт и я тебе расскажу подробнее о всех командах, которые я понимаю."
                keyboard = {
                        "inline": True,
                        "buttons": [
                            [{"action": {"type": "text", "label": "старт"}}, {"action": {"type": "text", "label": "about"}}],
                            [{"action": {"type": "text", "label": "info A1"}}, {"action": {"type": "text", "label": "move"}}],
                            [{"action": {"type": "text", "label": "профиль"}}],
                            [{"action": {"type": "open_link", "link": "https://divnolesie.ru/", "label": "Посмотреть карту (только для путников)"}}],
                            [{"action": {"type": "text", "label": "участвую"}}],
                            [{"action": {"type": "open_link","link": "https://vk.com/polkasknigami","label": "Написать Кураторам"}}]
                        ]
                    }
                response = send_message(peer_id, welcome_message,keyboard)
                if 'error' in response:
                    error_code = response['error']['error_code']
                    error_msg = response['error']['error_msg']
                    logger.error(f"Error {error_code}: {error_msg}")
                    # Обработка ошибки отправки сообщения
                    if error_code == 901:
                        send_message(peer_id, "Пожалуйста, подпишитесь на сообщения от нашего сообщества, чтобы получать уведомления.")
                else:
                    logger.info(f"71 Sent message: {response}")
            else:
                send_message(peer_id, "Упс, что-то пошло не так.")
                logger.error("Failed to get user info from VK")

        # заявка на участие в марафоне
        elif command.lower().startswith('участвую'):
            user = get_user(user_id)
            if user:
                if user.get('is_participant', True):
                    response = send_message(peer_id, "Вы уже участвуете в марафоне.")
                else:
                    user_exists = True
                    notify_admins(user_id, first_name, last_name, user_exists)
                    response = send_message(peer_id, "Ваша заявка на участие в марафоне отправлена на рассмотрение.")
            else:
                user_exists = False
                notify_admins(user_id, first_name, last_name, user_exists)
                response = send_message(peer_id, "Ваша заявка на участие в марафоне отправлена на рассмотрение.")

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
                            on_map = f"https://divnolesie.ru/pages/info.html?id={matched_cell['name']}"

                            next_moves = matched_cell.get('next', [])
                            keyboard = {
                                "inline": True,
                                "buttons": []
                            }
                            for move in next_moves:
                                keyboard['buttons'].append([{"action": {"type": "text", "label": f"info {move}"}}])
                            response = send_message(peer_id, f"{cell_name}\n{loc}\n\n{task}\n\n Посмотреть соту на карте {on_map}\n\nСледующий ход возможен на:", keyboard)
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
                            response = send_message(peer_id, not_found_message, keyboard)
                    else:
                        response = send_message(peer_id, "Пожалуйста, укажи номер соты в формате [латинская буква][число]. Например, 'сота A1'.")
                        logger.info(f"126 Sent message: {response}")
            else:
                send_message(peer_id, "Карта выдается только путникам Дивнолесья. Если ты хочешь путешествовать с нами по Дивнолесью, то подай заявку на участие.")

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
                if user['is_participant']:
                    marathon_info = load_info_marathon()

                    link = marathon_info['link']
                    login = marathon_info['login']
                    password = marathon_info['password']

                    welcome_message += (f'\n Ссылка на карту: {link} \n Логин: {login} \n Пароль: {password}')
            response = send_message(peer_id, welcome_message)
            if 'error' in response:
                    error_code = response['error']['error_code']
                    error_msg = response['error']['error_msg']
                    logger.error(f"Error {error_code}: {error_msg}")
                    # Обработка ошибки отправки сообщения
                    if error_code == 901:
                        send_message(peer_id, "Пожалуйста, подпишитесь на сообщения от нашего сообщества, чтобы получать уведомления.")

        # Переместиться на соту
        elif command.lower().startswith('move'):
            parts = message.split()
            if len(parts) > 1:
                next_cell = parts[1].upper()
                matched_cell = next((item for item in cells_data if item['name'] == next_cell), None)
                if matched_cell:
                    user = get_user(user_id)
                    if user:
                        if user['is_participant']:
                            current_cell = user.get('current_cell', '')
                            first_name = user['first_name']
                            last_name = user['last_name']
                            notify_admins_move(user_id, current_cell, next_cell, first_name = first_name, last_name = last_name)
                            send_message(peer_id, f"Запрос на перемещение в соту {next_cell} отправлен Кураторам. Осталось только дождатьсся их подтверждения и Вы будете перемещены на желаемую соту.")
                        else:
                            send_message(peer_id, "Ходить по тропинкам Дивнолесья может только путник. Отправляй 'участвую' и начинай участвовать в нашем марафоне!")
                    else:
                        response = send_message(peer_id, "Хм, кажется мы тебя потеряли? Или ты еще не вступил на путь Дивнолесья? Напиши Кураторам и они помогут.")
                        logger.info(f"Sent message: {response}")

                else:
                    response = send_message(peer_id, "Такая сота не найдена.")
                    logger.info(f"Sent message: {response}")
            else:
                response = send_message(peer_id, "Пожалуйста, укажите номер соты в формате 'move A1'.")
                logger.info(f"Sent message: {response}")

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
            current_cell = user['current_cell']

            visited_cells_all_seasons = user.get('visited_cells', {})
            visited_cells_message = ""

            # Скрыли от пользователей Посещенные соты за все сезоны "Посещенные соты за все сезоны: {visited_cells_message}"
            for season, cells in visited_cells_all_seasons.items():
                season_cells_str = ', '.join(cells)
                visited_cells_message += f"\nСезон {season}: {season_cells_str}"


            unicoins = user['coins']

            if len(user.get('artifacts', [])) < 1:
                artifacts = "У вас нет артефактов"
            else:
                all_artefacts = load_artefacts()
                # Создаем словарь для быстрого поиска артефактов по ID
                artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}

                # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
                artifact_names = [artefact_dict[artifact_id] for artifact_id in user.get('artifacts', []) if artifact_id in artefact_dict]

                artifacts = ', '.join(artifact_names)
            user_name = first_name + ' ' + last_name
            mention = f"[id{user_id}|{user_name}]"

            user_info_message = (f"Привет, {mention}!\n Текущий сезон: {participant} \n"
                                    f"Вы находитесь на соте {current_cell}. \n"
                                    f"Куратор: {kurator_name},\n"
                                    f"Посещенные соты в этом сезоне: {visited_cells_str}.\n"
                                    f"Ваши артефакты: {artifacts}.\n "
                                    f"У вас на счету: {unicoins} юникоинов.\n"
                                    f"Опыт для яиц: {user['exp_egg']},\n"
                                    f"Уникальный опыт для Каменного единорога: {user['exp_kamen']},\n"
                                    f"Уникальный опыт для Лесного единорога: {user['exp_les']},\n"
                                    f"Уникальный опыт для Болотного единорога: {user['exp_boloto']},\n"
                                    f"Уникальный опыт для Пустынного единорога: {user['exp_pustyn']},\n"
                                    f"Уникальный опыт для Снежного единорога: {user['exp_snow']}")

            send_message(peer_id, user_info_message)


        # ADMIN секция
        # Получить команды, доступные админам
        elif command.lower() == 'админ':
            if user and user.get('admin'):
                admin_message = (
                    "Привет, администратор! Вот доступные команды: \n"\
                                "- участники - Покажет список всех участников со всей информацией по каждому. Не покажет тех, кто не участвует в сезоне. \n"\
                                "- добавить/удалить артефакт - Похволит добавить/удалить артефакт выбранному пользователю. Сначала выберите пользователя из списка, потом выберите артефакт. \n"\
                                "- начать сезон - Сбросит у всех участников признак что они участвуют в марафоне (чтобы они смогли подать заявки на новый сезон). И обновит номер сезона.\n"
                                "- add_coins [ID_пользователя] [Целое число] - Для добавления юникоинов. Пример: add_coins 5649984 10 \n"\
                                "- remove_coins [ID_пользователя] [Целое число] - Для вычитания юникоинов. Пример: remove_coins 5649984 10 \n"\
                                "- update_coins [ID_пользователя] [Целое число] - Перезапишет текущее значение юникоинов у пользователя. Пример: update_coins 5649984 10 \n"\
                                "- add_exp [Тип опыта] [ID_пользователя] [Целое число] - Добавит указанный опыт у пользователя. Типы опыта: egg (яйца), les(уникальный лесной опыт), kamen(уникальный каменный опыт), boloto(уникальный болотный опыт), pustyn(уникальный пустынный опыт), snow(уникальный снежный опыт). Пример: add_exp boloto 5649984 10 \n"\
                                "ID пользователя можно взять из команды -список пользователей-. Вот еще доступные команды: \n"
                                )
                keyboard = {
                        "inline": True,
                        "buttons": [
                            [{"action": {"type": "text", "label": "участники"}}],
                            [{"action": {"type": "text", "label": "добавить артефакт"}}, {"action": {"type": "text", "label": "удалить артефакт"}}],
                            [{"action": {"type": "text", "label": "начать сезон"}}],
                            [{"action": {"type": "text", "label": "add_coins ID_пользователя количество"}}],
                            [{"action": {"type": "text", "label": "remove_coins ID_пользователя количество"}}],
                            [{"action": {"type": "text", "label": "update_coins ID_пользователя количество"}}]
                        ]
                    }
                send_message(peer_id, admin_message, keyboard)
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")


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

        # Получение списка всех участников марафона (is_participant=true). Без пагинации (проверить ограничение вк)
        elif command.lower() == 'участники':
            if user and user.get('admin'):
                participants = get_all_participants()
                if participants:
                    participants_info = ''
                    all_artefacts = load_artefacts()
                    # Создаем словарь для быстрого поиска артефактов по ID
                    artefact_dict = {artefact['id']: artefact['name'] for artefact in all_artefacts}

                    users = load_users()

                    for participant in participants:
                        kurator = next((u for u in users if u.get('vk_id') == participant.get('kurator')), None)
                        if len(participant.get('artifacts', [])) < 1:
                            artifacts = "Нет артефактов"
                        else:
                            # Получаем список названий артефактов, соответствующих ID, которые хранятся у пользователя
                            artifact_names = [artefact_dict[artifact_id] for artifact_id in participant.get('artifacts', []) if artifact_id in artefact_dict]

                            artifacts = ', '.join(artifact_names)

                        participants_info += (f"\n \n ID: {participant['vk_id']}, \n"
                                                f"Имя: {participant['first_name']} {participant['last_name']},\n"
                                                f"Куратор: {kurator['first_name']} {kurator['last_name']},\n"
                                                f"Текущая сота: {participant['current_cell']},\n"
                                                f"Артефакты: {artifacts}, \n"
                                                f"Юникоины: {participant['coins']}, \n"
                                                f"Опыт для яиц: {participant['exp_egg']},\n"
                                                f"Уникальный опыт для Каменного единорога: {participant['exp_kamen']},\n"
                                                f"Уникальный опыт для Лесного единорога: {participant['exp_les']},\n"
                                                f"Уникальный опыт для Болотного единорога: {participant['exp_boloto']},\n"
                                                f"Уникальный опыт для Пустынного единорога: {participant['exp_pustyn']},\n"
                                                f"Уникальный опыт для Снежного единорога: {participant['exp_snow']}.\n")

                    send_message(peer_id, f"Список всех участников:\n{participants_info}")
                else:
                    send_message(peer_id, "Нет участников в марафоне.")
            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

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

        # Добавить юникоины
        elif command.lower().startswith('add_coins'):
            if user.get('admin', False):
                try:
                    _, user_id, coins = message.split()
                    add_coins = int(coins)
                    logger.info(f"добавить: {user_id},{add_coins}")

                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_id} не найден.")
                    else:
                        selected_user['coins'] += int(add_coins)
                        logger.info("total_coins: %s for user_id: %s", selected_user['coins'], user_id)
                        update_user(user_id, coins = selected_user['coins'])
                        logger.info("total updated user: %s ", {selected_user['coins']})
                        response = send_message(peer_id, f"Пользователю ID: {user_id} добавлено {add_coins} юникоинов. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['coins']} юникоинов.")
                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'add_coins [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Вычесть юникоины
        elif command.lower().startswith('remove_coins'):
            logger.info(f"Sent message: {message.split()}")
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
                        logger.info("total_coins: %s for user_id: %s", selected_user['coins'], user_id)
                        update_user(user_id, coins = selected_user['coins'])
                        logger.info("total updated user: %s ", {selected_user['coins']})
                        response = send_message(peer_id, f"Пользователю ID: {user_id} удалено {coins} юникоинов. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['coins']} юникоинов.")
                except ValueError:
                    response = send_message(peer_id, "Используйте формат: 'remove_coins [ID пользователя] [количество]'")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # Задать новое значение для юникоинов
        elif command.lower().startswith('update_coins'):
            logger.info(f"Sent message: {message.split()}")
            if user.get('admin', False):
                try:
                    _, user_id, coins = message.split()
                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_id} не найден.")
                    else:
                        selected_user['coins'] = int(coins)
                        logger.info("total_coins: %s for user_id: %s", selected_user['coins'], user_id)
                        update_user(user_id, coins = selected_user['coins'])
                        logger.info("total updated user: %s ", {selected_user['coins']})
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
                    logger.info(f"добавить: {type_exp}, {user_exp_id},{amount}")

                    users = load_users()
                    selected_user = next((u for u in users if u['vk_id'] == int(user_exp_id)), None)

                    if selected_user is None:
                        response = send_message(peer_id, f"Пользователь с ID: {user_exp_id} не найден.")
                    else:
                        if type_exp == 'egg':
                            selected_user['exp_egg'] += int(amount)
                            update_user(user_id, exp_egg = selected_user['exp_egg'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_egg']} опыта для яиц."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} опыта для яиц. \n Теперь у вас есть {selected_user['exp_egg']} опыта для яиц."
                        if type_exp == 'boloto':
                            selected_user['exp_boloto'] += int(amount)
                            update_user(user_id, exp_boloto = selected_user['exp_boloto'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального болотного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_boloto']} опыта для болотного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для болотного единорога. \n Теперь у вас есть {selected_user['exp_boloto']} уникального опыта для болотного единорога."
                        if type_exp == 'snow':
                            selected_user['exp_snow'] += int(amount)
                            update_user(user_id, exp_snow = selected_user['exp_snow'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального снежного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_snow']} опыта для снежного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для снежного единорога. \n Теперь у вас есть {selected_user['exp_snow']} уникального опыта для снежного единорога."
                        if type_exp == 'les':
                            selected_user['exp_les'] += int(amount)
                            update_user(user_id, exp_les = selected_user['exp_les'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального лесного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_les']} опыта для лесного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для лесного единорога. \n Теперь у вас есть {selected_user['exp_les']} уникального опыта для лесного единорога."
                        if type_exp == 'kamen':
                            selected_user['exp_kamen'] += int(amount)
                            update_user(user_id, exp_kamen = selected_user['exp_kamen'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального каменного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_kamen']} опыта для каменного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для каменного единорога. Теперь у вас есть {selected_user['exp_kamen']} уникального опыта для каменного единорога."
                        if type_exp == 'pustyn':
                            selected_user['exp_pustyn'] += int(amount)
                            update_user(user_id, exp_pustyn = selected_user['exp_pustyn'])
                            success_message = f"Пользователю ID: {user_exp_id} добавлено {amount} уникального пустынного опыта. Теперь у {selected_user['first_name']} {selected_user['last_name']} есть {selected_user['exp_pustyn']} опыта для пустынного единорога."
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Вам начисленно {amount} уникального опыта для пустынного единорога. \n Теперь у вас есть {selected_user['exp_pustyn']} уникального опыта для пустынного единорога."
                        else:
                            nonsuccess_message = f"Пользователю ID: {user_exp_id} не удалось добавить опыт. Проверь, правильно ли указан тип опыта: egg, boloto, snow, les, kamen, pustyn."

                        if success_message:
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
                            notification_message = f"Дорогой путник,  {selected_user['first_name']} {selected_user['last_name']}! Ваш уникальный опыт для снежного единорога обновлен, теперь он равен {selected_user['exp_snow']}.""
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

        # команда переместить участника в соту MOVE
        if payload['action'] == 'confirm_move':
            vk_id = payload['user_id']
            cell = payload['cell']
            update_user(vk_id, current_cell = cell)
            send_message(vk_id, f"Вы успешно переместились на соту {cell}.")
            notify_admins_info(vk_id, f"Пользователь {vk_id} успешно перемещен на соту {cell}.")

        # команда не перемещать участника в соту MOVE
        elif payload['action'] == 'reject_move':
            vk_id = payload['user_id']
            cell = payload['cell']
            send_message(vk_id, f"Запрос на перемещение в соту {cell} отклонен. Если у тебя есть вопросы, обращайся к Кураторам Дивнолесья и они помогут!")
            notify_admins_info(vk_id, f"Запрос от {vk_id} на перемещение в соту {cell} отклонен.")

        # Выбрать пользователя для артефакта
        elif payload['action'].lower().startswith('select_artefact_for_user'):
            user = get_user(user_id)
            if user.get('admin', False):
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
                    artefacts_keyboard['buttons'].append([{"action": {"type":"callback", "label":"Ещё","payload":json.dumps({"action": "more","selected_user_id": selected_user_id,"list": "artefacts","page": page+1})}}])
                response = send_message(peer_id, "Выберите артефакт для добавления:", artefacts_keyboard)
                logger.info(f"Sent message: {response}")
            else:
                response = send_message(peer_id, "У вас нет прав для выполнения этой команды.")
                logger.info(f"Sent message: {response}")

        # Выбор артефакта у пользователя, чтобы удалить артефакт
        elif payload['action'].lower() == 'select_user_for_deletion_art':
            selected_user_id = payload['selected_user_id']
            page = int(payload['page'])
            participants = get_all_participants()
            selected_user = next((u for u in participants if u['vk_id'] == selected_user_id), None)
            if selected_user:
                all_artefacts = load_artefacts()
                user_artefacts = [a for a in all_artefacts if a['id'] in selected_user.get('artifacts', [])]
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
                logger.info(f"Sent message: {response}")

        # отобразить больше пользователей или артефактов
        elif payload['action'].lower().startswith('more'):
            if payload['list'] == "artefacts":
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
                    user_artefacts = [a for a in all_artefacts if a['id'] in selected_user.get('artifacts', [])]
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
                logger.info(f"Sent message: {response}")
            else:
                response = send_message(peer_id, "Что-то пошло не так. (Данные об ошибке elif payload['action'].lower().startswith('more'))")
                logger.info("В функции возврата инлайн кнопок не удалось определить какой список надо вернуть")


        # Добавить выбранный артефакт выбранному пользователю
        elif payload['action'].lower().startswith('add_artefact'):
            user = get_user(user_id)
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
                        send_message(peer_id, f"Артефакт '{artefact['name']}' успешно добавлен пользователю {selected_user['last_name']}. Осталось юникоинов: {selected_user['coins']}.")
                    else:
                        send_message(peer_id, f"У пользователя {selected_user['first_name']} {selected_user['last_name']} недостаточно средств для покупки артефакта '{artefact['name']}'. Необходимо: {artefact_price}, доступно: {selected_user['coins']}.")

            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

        # удалить артефакт у пользователя
        elif payload['action'].lower().startswith('delete_artefact'):
            user = get_user(user_id)
            if user.get('admin', False):
                selected_user_id = payload['selected_user_id']
                artefact_id = payload['artefact_id']

                selected_user = next((u for u in get_all_participants() if u['vk_id'] == selected_user_id), None)
                all_artefacts = load_artefacts()
                artefact = next((a for a in all_artefacts if a['id'] == artefact_id), None)
                if artefact:
                    remove_artefact_from_user(selected_user_id, artefact_id)
                    send_message(peer_id, f"Артефакт '{artefact['name']}' успешно удален у пользователя {selected_user['first_name']} {selected_user['last_name']}.")

            else:
                send_message(peer_id, "У вас нет прав для выполнения этой команды.")

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
    logger.info(f"141 VK API users.get response: {response_data}")
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
    logger.info(f"629 VK API response: {response.json()}")
    return response.json()


if __name__ == '__main__':
    app.run()
