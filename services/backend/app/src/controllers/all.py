from src.controllers.base import AppController


def get_all_controllers() -> list[type[AppController]]:
    controllers = []

    from src.modules.home.controllers import HomeController
    controllers.append(HomeController)

    from src.modules.note.controllers import NoteController
    controllers.append(NoteController)

    return controllers
