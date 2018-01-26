from kant.core.datamapper.base import ModelMeta, FieldMapping


class SchemaModel(FieldMapping, metaclass=ModelMeta):

    @classmethod
    def loads(self, obj, cls):
        Event = cls
        json_columns = {}
        for name, field in Event.concrete_fields.items():
            json_column = field.json_column or name
            json_columns[json_column] = name
        args = {json_columns[name]: value for name, value in obj.items()}
        return Event(**args)

    def decode(self):
        event = {key: value for key, value in self.serializeditems()}
        return event
