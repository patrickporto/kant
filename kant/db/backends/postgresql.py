class DatabaseWrapper(object):
    sql_create_table = 'CREATE TABLE {name} ({columns})'
    sql_drop_table = 'DROP TABLE {name}'
    sql_create_index = 'CREATE INDEX {name} ON {table} ({columns})'
    sql_drop_index = 'DROP INDEX {name}'

    def create_table(self, name, columns):
        name = self.escape_string(name)
        stmt_columns = []
        stmt_primary_keys = []
        for column in columns:
            stmt_column = '{name} {type}'.format(
                name=column.name,
                type=column.type,
            )
            if column.primary_key:
                stmt_primary_key = 'PRIMARY KEY ({name})'.format(
                    name=column.name,
                )
                stmt_primary_keys.append(stmt_primary_key)
            elif not column.null:
                stmt_column += ' NOT NULL'
            stmt_columns.append(stmt_column)
        stmt = self.sql_create_table.format(
            name=name,
            columns=','.join(stmt_columns + stmt_primary_keys)
        )
        return stmt

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

    def drop_index(self, name):
        name = self.escape_string(name)
        return self.sql_drop_index.format(name=name)

    def escape_string(self, text):
        return text
