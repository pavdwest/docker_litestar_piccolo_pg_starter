from typing import Type, TypeVar, Generic, Dict, List
import importlib
from functools import lru_cache


# Define a generic type variable T that represents the base class type
T = TypeVar('T')


class ClassManifest(Generic[T]):
    """
    A generic container for storing class references derived from a specific base class.

    Attributes:
        _class_paths (List[str]): List to store class paths as strings.
        _class_map (Dict[str, Type[T]]): Dictionary to store class names and class references (lazy-loaded).
    """
    def __init__(self, class_paths: List[str] = None):
        """
        Initialize the ClassManifest with an optional list of class paths.

        Args:
            class_paths (List[str], optional): A list of string paths to classes.
        """
        self._class_paths: List[str] = class_paths or []
        self._class_map: Dict[str, Type[T]] = {}
        self._classes_loaded: bool = False

    def add(self, class_path: str):
        """
        Add a class path to the manifest.

        Args:
            class_path (str): The string path to the class, e.g., "src.modules.note.models.Note".
        """
        if class_path not in self._class_paths:
            self._class_paths.append(class_path)

    def _load_classes(self):
        """
        Lazily load classes from their paths and store them in the class map.
        """
        if self._classes_loaded:
            return

        for class_path in self._class_paths:
            if class_path not in self._class_map:
                module_path, class_name = class_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
                self._class_map[class_name] = cls

    @lru_cache(maxsize=1)
    def get_map(self) -> Dict[str, Type[T]]:
        """
        Get the dictionary of stored class references. Lazily loads the classes if needed.

        Returns:
            Dict[str, Type[T]]: The dictionary of class names and references.
        """
        self._load_classes()
        return self._class_map

    def get_all(self) -> List[Type[T]]:
        """
        Get the list of stored class references. Lazily loads the classes if needed.

        Returns:
            List[Type[T]]: The list of class references.
        """
        self._load_classes()
        return list(self._class_map.values())

    def get_by_name(self, class_name: str) -> Type[T]:
        """
        Retrieve a class by its name. Lazily loads the classes if needed.

        Args:
            class_name (str): The name of the class to retrieve.

        Returns:
            Type[T]: The class reference matching the given name.

        Raises:
            KeyError: If no class with the given name exists in the manifest.
        """
        self._load_classes()
        if class_name not in self._class_map:
            raise KeyError(f"Class with name '{class_name}' not found in the manifest.")
        return self._class_map[class_name]

    def __len__(self) -> int:
        """
        Get the number of stored classes.

        Returns:
            int: The number of classes in the manifest.
        """
        return len(self._class_paths)

    def __contains__(self, class_name: str) -> bool:
        """
        Check if a class name is already in the manifest.

        Args:
            class_name (str): The class name to check.

        Returns:
            bool: True if the class name is in the manifest, False otherwise.
        """
        self._load_classes()
        return class_name in self._class_map
