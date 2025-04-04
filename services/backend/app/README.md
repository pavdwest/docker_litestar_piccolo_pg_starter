## Adding a New Model

1. Add folder to ```services/backend/app/src/modules/new_model```

    `.../new_model/models.py`         for the Piccolo database model(s). See `src.models.base.generate_model`, which can generates a Model base class for ease of use.

    `.../new_model/dtos.py`           for the MsgSpec validators. See `src.dtos`, for base types.

    `.../new_model/controllers.py`    for the controller. See `src.controllers.crud.generate_crud_controller`, which can generates a basic CRUD controller for ease of use.

2. Add the controller to `src.controllers.all.CONTROLLERS`

3. Add the model to `src.models.all.MODELS`

4. Create migration:

    TODO

5. Run migration:

    TODO
