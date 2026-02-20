# save_load.rpy — сохранение/загрузка без хранения объектов Sloomp в persistent
# Коллекция хранится как persistent.sloomp_data (список dict), current_sloomp_index (int).
# В игре используются store.sloomp_collection и store.current_sloomp (восстанавливаются при загрузке).

init python:
    def load_sloomp_from_persistent():
        data = getattr(persistent, "sloomp_data", None)
        if data is None:
            data = []
        try:
            store.sloomp_collection = [store.Sloomp.from_dict(d) for d in data]
        except Exception:
            store.sloomp_collection = []
        idx = getattr(persistent, "current_sloomp_index", None)
        if idx is not None and 0 <= idx < len(store.sloomp_collection):
            store.current_sloomp = store.sloomp_collection[idx]
        else:
            store.current_sloomp = store.sloomp_collection[0] if store.sloomp_collection else None

    def sync_sloomp_to_persistent():
        try:
            persistent.sloomp_data = [s.to_dict() for s in store.sloomp_collection]
            if store.current_sloomp is not None and store.current_sloomp in store.sloomp_collection:
                persistent.current_sloomp_index = store.sloomp_collection.index(store.current_sloomp)
            else:
                persistent.current_sloomp_index = 0 if store.sloomp_collection else None
        except Exception:
            pass

    def save_game():
        sync_sloomp_to_persistent()
        try:
            renpy.save_persistent()
            renpy.notify("Игра сохранена")
        except Exception as e:
            renpy.notify("Ошибка сохранения: " + str(e))

    def on_shop_bought():
        try:
            renpy.save_persistent()
        except Exception:
            pass

    def on_collection_changed():
        sync_sloomp_to_persistent()
        try:
            renpy.save_persistent()
        except Exception:
            pass
