# import json

# from polyfactory.factories.pydantic_factory import ModelFactory

# # This file is in services/backend/app/src/modules/_misc/generate_notes.py
# # Import note model from services/backend/app/src/models.py



# class NoteFactory(ModelFactory[Note]):
#     ...


# n = 1000

# # Generate n notes to file as json array
# notes = NoteFactory.batch(n)

# # Write to file
# with open('notes.json', 'w') as f:
#     json.dump(notes, f)
