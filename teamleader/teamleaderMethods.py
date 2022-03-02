import json
import os
import pickle
import time
from itertools import count

from .teamleaderStores import Webhook


class TeamleaderFileHandler:
    file = {}

    def __init__(self, object_name, refresh_function):
        if not os.path.exists("object_cache"):
            os.makedirs("object_cache")
        self.file_path = "object_cache/" + object_name
        file_exists = os.path.isfile(self.file_path)
        time_elapsed = -1
        if file_exists:
            self.file = self.file_loader()
            time_elapsed = time.time() - self.file["time"]

        if not file_exists or time_elapsed > 60 * 60 * 24:
            self.file["time"] = time.time()
            self.file["file"] = refresh_function()
            self.file_saver(self.file)
            print(f"File '{object_name}' refreshed")

    def file_saver(self, json_file):
        with open(self.file_path, "wb+") as output:
            pickle.dump(json_file, output, pickle.HIGHEST_PROTOCOL)

    def file_loader(self):
        with open(self.file_path, "rb") as input:
            return pickle.load(input)


class TeamleaderTag:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def tag(self, object_id, tags):
        if not isinstance(tags, list):
            tags = [tags]
        data = {"id": object_id, "tags": tags}
        return self.post(self.url + ".tag", data=json.dumps(data))


class TeamleaderUntag:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def untag(self, object_id, tags):
        if not isinstance(tags, list):
            tags = [tags]
        data = {"id": object_id, "tags": tags}
        return self.post(self.url + ".untag", data=json.dumps(data))


class TeamleaderPagesList:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def list(self, data={}, feedback=False, sideloading=""):
        if sideloading:
            data.update({"include": sideloading})
        there_are_more_pages = True
        c = count(1)
        size = 50
        while there_are_more_pages:
            number = next(c)
            if feedback:
                print(f"page: {number}, size:{size}, total:{number * size}")
            page_data = {"page": {"size": size, "number": number}}
            data.update(page_data)
            respons = self.post(self.url + ".list", data=json.dumps(data))
            object_lists = respons.json().get("data")
            included = respons.json().get("included", {})
            if not object_lists:
                return
            there_are_more_pages = len(object_lists) == size
            for object_element in object_lists:
                if included:
                    for key, value in included.items():
                        current_value = object_element.get(key)
                        if current_value:
                            replacement_value = self.get_right_element(
                                value, current_value
                            )
                            object_element[key] = replacement_value
                yield object_element

    def get_right_element(self, value, current_value):
        for element in value:
            if current_value["id"] == element["id"]:
                return element


class TeamleaderSimpleList:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def list(self, data={}):
        return self.get(self.url + ".list", data=json.dumps(data)).json()


class TeamleaderCustomField:
    value: str
    object_id: str
    type: str
    label: str

    def __init__(self, value: str, object_id: str, type: str, label: str):
        self.type = type
        self.object_id = object_id
        self.value = value
        self.label = label

    def __str__(self):
        return f"TeamleaderCustomField label is {self.label} and value is {self.value}"

    def __repr__(self):
        return (
            f"{type(self).__name__}(type= {self.type}, "
            f"value= {self.value}, label= {self.label})"
        )


class TeamleaderCustomFields(dict):
    # custom_fields: Mapping[str, TeamleaderCustomField]

    def __init__(self, custom_fields, get_teamleader, *arg, **kw):
        super(TeamleaderCustomFields, self).__init__(*arg, **kw)
        self._get_teamleader = get_teamleader
        self._make_custom_fiels_readable(custom_fields)

    def _make_custom_fiels_readable(self, custom_fields_local):
        custom_field_file_handler = TeamleaderFileHandler(
            "Custom_fields",
            self._refresh_function,
        )
        custom_fields_info = custom_field_file_handler.file["file"]
        custom_field_id_dict = {
            custom_field_info["id"]: custom_field_info["label"]
            for custom_field_info in custom_fields_info
        }
        self.custom_fields = {}
        for custom_field in custom_fields_local:
            self.custom_fields.update(
                self._make_custom_field_dict_object(custom_field, custom_field_id_dict)
            )

    def _make_custom_field_dict_object(self, custom_field, custom_field_id_dict):
        object_id = custom_field["definition"]["id"]
        label = custom_field_id_dict[object_id]
        return {
            label: TeamleaderCustomField(
                type=custom_field["definition"]["type"],
                object_id=object_id,
                value=custom_field["value"],
                label=label,
            )
        }

    def _refresh_function(self):
        return self._get_teamleader("customFieldDefinitions.list").json()["data"]

    def get(self, custom_field_id):
        return self.custom_fields.get(custom_field_id)


class TeamleaderInfo:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def info(self, object_id, old=True):
        result = self.get(self.url + ".info", data={"id": object_id}).json()["data"]
        if not old:
            result["custom_fields"] = self._transform_custom_fields(result)
        return result

    def _transform_custom_fields(self, result):
        custom_fields = result.get("custom_fields")
        if not custom_fields:
            return TeamleaderCustomFields([], self.get)
        return TeamleaderCustomFields(custom_fields, self.get)


class TeamleaderAdd:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def add(self, name, data={}):
        data["name"] = name
        return self.post(self.url + ".add", data=json.dumps(data))


class TeamleaderUpdate:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def update(self, object_id, data={}):
        data["id"] = object_id
        result = self.get(self.url + ".info", data={"id": object_id}).json()["data"]
        custom_fields = result.get("custom_fields")
        custom_fiels_dict = dict(
            map(lambda item: (item["definition"]["id"], item["value"]), custom_fields)
        )
        for item in data.get("custom_fields", []):
            item_id = item["id"]
            item_value = item["value"]
            custom_fiels_dict[item_id] = item_value

        data["custom_fields"] = [
            {"id": key, "value": value}
            for key, value in custom_fiels_dict.items()
            if value is not None
        ]
        return self.post(self.url + ".update", data=json.dumps(data))


class TeamleaderDelete:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def delete(self, object_id):
        return self.post(self.url + ".delete", data={"id": object_id})


class TeamleaderCreate:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def create(self, data={}):
        return self.post(self.url + ".create", data=json.dumps(data))


class TeamleaderCancel:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def cancel(self, object_id):
        return self.post(
            self.url + ".cancel",
            data=json.dumps({"id": object_id}),
        )


class TeamleaderComplete:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def complete(self, object_id):
        return self.post(
            self.url + ".complete",
            data=json.dumps({"id": object_id}),
        )


class TeamleaderSchedule:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def schedule(self, object_id, starts_at, ends_at):
        return self.post(
            self.url + ".schedule",
            data=json.dumps(
                {"id": object_id, "starts_at": starts_at, "ends_at": ends_at}
            ),
        )


class TeamleaderRegister:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def register(self, register_url: str, types: list):
        if not isinstance(types, list):
            raise TypeError(
                f"Types should be of the type list and is of type {type(types)}"
            )
        types_not_in_webhooks = list(
            filter(lambda webhook_type: not isinstance(webhook_type, Webhook), types)
        )
        if types_not_in_webhooks:
            raise ValueError(f"{types_not_in_webhooks} not exists in the webhook")
        return self.post(
            self.url + ".register",
            data=json.dumps({"url": register_url, "types": types}),
        )


class TeamleaderUnregister:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def unregister(self, register_url: str, types: list):
        if not isinstance(types, list):
            raise TypeError(
                f"Types should be of the type list and is of type {type(types)}"
            )
        types_not_in_webhooks = list(filter(lambda x: x not in Webhook, types))
        if types_not_in_webhooks:
            raise ValueError(f"{types_not_in_webhooks} not exists in the webhook")
        return self.post(
            self.url + ".unregister",
            data=json.dumps({"url": register_url, "types": types}),
        )


class TeamleaderReopen:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def reopen(self):
        raise NotImplementedError("Reopen is not yet implementated")


class TeamleaderAddParticipant:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def add_participant(self):
        raise NotImplementedError("AddParticipant is not yet implementated")


class TeamleaderUpdateParticipant:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def update_participant(self):
        raise NotImplementedError("UpdateParticipant is not yet implementated")


class TeamleaderClose:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def close(self):
        raise NotImplementedError("Close is not yet implementated")


class TeamleaderMove:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def move(self):
        raise NotImplementedError("Move is not yet implemented")


class TeamleaderWin:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def win(self):
        raise NotImplementedError("Win is not yet implemented")


class TeamleaderLose:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.get = get_teamleader
        self.post = post_teamleader

    def lose(self):
        raise NotImplementedError("Lose is not yet implemented")
