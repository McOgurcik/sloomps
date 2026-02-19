# save_load.rpy — автосохранение прогресса магазина и коллекции

init python:
    def save_persistent_progress():
        try:
            renpy.save_persistent()
        except Exception:
            pass

    def on_shop_bought():
        save_persistent_progress()

    def on_collection_changed():
        save_persistent_progress()
