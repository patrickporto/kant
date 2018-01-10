class DatabaseWrapper(object):
    sql_create_table = 'CREATE TABLE {name}'
    sql_drop_table = 'DROP TABLE {name}'
    sql_create_index = 'CREATE INDEX {name} ON {table} ({columns})'

    def create_table(self, name):
        name = self.escape_string(name)
        return self.sql_create_table.format(name=name)

    def drop_table(self, name):
        name = self.escape_string(name)
        return self.sql_drop_table.format(name=name)

    def create_index(self, name, table, columns):
        name = self.escape_string(name)
        table = self.escape_string(table)
        columns = [self.escape_string(column) for column in columns]
        stmt = self.sql_create_index.format(
            name=name,
            table=table,
            columns=','.join(columns)
        )
        return stmt

    def escape_string(self, text):
        return text
