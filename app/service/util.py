from sqlmodel import SQLModel


def check_update_needed(source: SQLModel, target: SQLModel) -> bool:
    for field_name in source.model_fields_set:
        if not hasattr(target, field_name) or getattr(source, field_name) != getattr(
            target, field_name
        ):
            return True
    return False
