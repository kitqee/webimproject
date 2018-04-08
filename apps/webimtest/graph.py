import vk_api


def get_graph(user, token):
    """
    Строит граф связанности друзей между собой
    :param user: id пользователя
    :param token: токен, от которого будет запрос
    :return: граф, формата {"nodes": [{"id": id, "group": group*}],
                            "links": [{"source": id, "target": id]}]}
    * - ban, друг в бане; main, проверяемый пользователь; friend, обычный друг
    """

    graph = {"nodes": [], "links": []}
    api = vk_api.VkApi(token=token, api_version='5.64').get_api()

    def get_valid_ids(friends):
        # Удаляет из всех друзей забаненых
        valid = []
        for friend in friends:
            if friend.get('deactivated', 0):
                continue
            valid.append(friend['id'])
        return valid

    def get_friends(list_ids):
        # execute method api - получает список всех друзей по списку list_ids
        with vk_api.VkRequestsPool(api) as pool:
            friends = pool.method_one_param(
                'friends.get',  # Метод
                key='user_id',  # Изменяющийся параметр
                values=list_ids,
                # Параметры, которые будут в каждом запросе
                default_values={'fields': 'deactivated'}
            )
        return friends.result

    friends_items = get_friends([user])[user]["items"]
    valid_friends = {}

    # Смотрим друзей user
    for friend in friends_items:
        # Добавляем на граф заблокированных друзей
        if friend.get('deactivated', 0):
            graph["nodes"].append({
                "id": friend["id"],
                "name": friend["first_name"] + friend["last_name"],
                "group": "ban"
            })
            graph["links"].append(
                {"source": user, "target": friend["id"]})
        # Из остальных формируем словарь {ID пользователя: "Имя"}
        else:
            valid_friends[friend["id"]] = "{0} {1}".format(
                friend["first_name"], friend["last_name"])

    friends_ids_list = list(valid_friends.keys())
    # Словарь пользователей, у каждого два атрибута - имя и список id друзкей
    # {id : {"name": "Имя пользователя", "ids": [Список id друзей]}}
    result = {user: {"name": "Current", "ids": friends_ids_list}}

    # Получаем друзей друзей user'a
    friends_of_friends = get_friends(friends_ids_list)

    # Добавляем данные в result
    for friend_id in valid_friends:
        ids = get_valid_ids(friends_of_friends[friend_id]["items"])
        result[friend_id] = {"name": valid_friends[friend_id], "ids": ids}

    # Формуруем связи между всеми узлами
    for user_id in result:
        group = "friend"
        if user_id == user:
            group = "main"
        graph["nodes"].append(
            {"id": user_id, "group": group, "name": result[user_id]["name"]})
        for j in result[user_id]["ids"]:
            # Оставляем только друзей, которые есть в друзьях у user
            if user_id != j and j in friends_ids_list:
                graph["links"].append({"source": user_id, "target": j})

    return graph