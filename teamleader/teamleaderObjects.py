from .teamleaderMethods import *
from .teamleaderStores import MigrateTypes


class Departments(TeamleaderSimpleList, TeamleaderInfo):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "departments"
        super().__init__(get_teamleader, post_teamleader)


class Users(TeamleaderPagesList, TeamleaderInfo):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "users"
        super().__init__(get_teamleader, post_teamleader)

    # def me(self):
    #     pass


class Projects(
    TeamleaderPagesList,
    TeamleaderInfo,
    TeamleaderCreate,
    TeamleaderUpdate,
    TeamleaderClose,
    TeamleaderReopen,
    TeamleaderDelete,
    TeamleaderAddParticipant,
    TeamleaderUpdateParticipant,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "projects"
        super().__init__(get_teamleader, post_teamleader)


class CustomFields(TeamleaderPagesList, TeamleaderInfo):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "customFieldDefinitions"
        super().__init__(get_teamleader, post_teamleader)


class WorkTypes(TeamleaderPagesList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "workTypes"
        super().__init__(get_teamleader, post_teamleader)


class Contacts(
    TeamleaderPagesList,
    TeamleaderInfo,
    TeamleaderAdd,
    TeamleaderDelete,
    TeamleaderUpdate,
    TeamleaderTag,
    TeamleaderUntag,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "contacts"
        super().__init__(get_teamleader, post_teamleader)
        # self.tag = TeamleaderTag(get_teamleader, post_teamleader)

    # def link_to_company(self):
    #     pass
    #
    # def unlink_from_company(self):
    #     pass


class Companies(
    TeamleaderPagesList,
    TeamleaderInfo,
    TeamleaderAdd,
    TeamleaderDelete,
    TeamleaderUpdate,
    TeamleaderTag,
    TeamleaderUntag,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "companies"
        super().__init__(get_teamleader, post_teamleader)
        # self.tag = TeamleaderTag(get_teamleader, post_teamleader)


class BusinessTypes(TeamleaderSimpleList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "businessTypes"
        super().__init__(get_teamleader, post_teamleader)


class Tags(TeamleaderPagesList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "tags"
        super().__init__(get_teamleader, post_teamleader)


class DealPhases(TeamleaderPagesList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "dealPhases"
        super().__init__(get_teamleader, post_teamleader)


class DealSources(TeamleaderPagesList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "dealSources"
        super().__init__(get_teamleader, post_teamleader)


class Tasks(
    TeamleaderPagesList,
    TeamleaderInfo,
    TeamleaderCreate,
    TeamleaderUpdate,
    TeamleaderDelete,
    TeamleaderComplete,
    TeamleaderSchedule,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "tasks"
        super().__init__(get_teamleader, post_teamleader)

    #
    # def reopen(self):
    #     pass
    #
    # def schedule(self):
    #     pass


class Invoices(TeamleaderPagesList, TeamleaderInfo):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "invoices"
        super().__init__(get_teamleader, post_teamleader)


class Events(
    TeamleaderPagesList,
    TeamleaderInfo,
    TeamleaderCreate,
    TeamleaderUpdate,
    TeamleaderCancel,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "events"
        super().__init__(get_teamleader, post_teamleader)


class Webhooks(TeamleaderSimpleList, TeamleaderRegister, TeamleaderUnregister):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "webhooks"
        super().__init__(get_teamleader, post_teamleader)


class TimeTracking(
    TeamleaderInfo,
    TeamleaderPagesList,
    TeamleaderAdd,
    TeamleaderUpdate,
    TeamleaderDelete,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "timeTracking"
        super().__init__(get_teamleader, post_teamleader)


class Migrate:
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "migrate"
        self.get = get_teamleader

    def get_id(self, old_type: MigrateTypes, old_id: int):
        data = {"type": old_type, "id": old_id}
        response = self.get(self.url + ".id", data=json.dumps(data))
        return response.json()["data"]["id"]


class Deals(
    TeamleaderPagesList,
    TeamleaderInfo,
    TeamleaderCreate,
    TeamleaderUpdate,
    TeamleaderMove,
    TeamleaderWin,
    TeamleaderLose,
    TeamleaderDelete,
):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "deals"
        self.get = get_teamleader
        super().__init__(get_teamleader, post_teamleader)


class LostReasons(TeamleaderPagesList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "lostReasons"
        self.get = get_teamleader


class Teams(TeamleaderPagesList):
    def __init__(self, get_teamleader, post_teamleader) -> None:
        self.url = "teams"
        self.get = get_teamleader
