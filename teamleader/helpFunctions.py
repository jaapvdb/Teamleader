def get_custom_field_value(custom_fields, custom_field_id):
    return get_custom_field(custom_fields, custom_field_id)["value"]


def get_custom_field(custom_fields, custom_field_id):
    for custom_field in custom_fields:
        if custom_field["definition"]["id"] == custom_field_id:
            return custom_field
