## Adding a New Model

1. Add folder to ```services/backend/app/src/modules```

    `.../models/my_model/models.py`         for the Piccolo database model(s)

    `.../models/my_model/dtos.py`           for the Pydantic validators

    `.../models/my_model/controller.py`     for the controller. See `src.base.controllers.base.generate_crud_controller`, which can generates a basic CRUD controller for ease of use.

2. Add the controller to `src.base.controllers.all.get_all_controllers`

3. Create migration:

    TODO

4. Run migration:

    TODO
