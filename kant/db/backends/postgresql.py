class DatabaseWrapper(object):
    sql_create_table = 'CREATE TABLE {name}'

    def create_table(self, name):
        name = self.escape_string(name)
        return self.sql_create_table.format(name=name)

    def escape_string(self, text):
        return text
