class DatabaseWrapper(object):
    sql_create_table = 'CREATE TABLE {name}'
    sql_drop_table = 'DROP TABLE {name}'

    def create_table(self, name):
        name = self.escape_string(name)
        return self.sql_create_table.format(name=name)

    def drop_table(self, name):
        name = self.escape_string(name)
        return self.sql_drop_table.format(name=name)

    def escape_string(self, text):
        return text
