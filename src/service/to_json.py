def query_to_json_list(cursor):
    return [dict((cursor.description[i][0], value) \
            for i, value in enumerate(row)) for row in cursor.fetchall()]

def query_to_json(cursor):
    row = cursor.fetchone()
    d = {}
    if row is None:
        return None
    for i in range(len(row)):
        d[cursor.description[i][0]] = row[i]
    return d
