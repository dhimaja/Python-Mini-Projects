"""
Database Model interface for the COMP249 Web Application assignment

@author: steve cassidy
"""


def position_list(db, limit=10):
    """Return a list of positions ordered by date
    db is a database connection
    return at most limit positions (default 10)

    Returns a list of tuples  (id, timestamp, owner, title, location, company, description)
    """
    cursor = db.cursor()
    query = """SELECT id, timestamp, owner, title, location, company, description FROM positions ORDER BY timestamp desc LIMIT ?"""
    cursor.execute(query, [limit])
    return cursor.fetchall()


def position_get(db, id):
    """Return the details of the position with the given id
    or None if there is no position with this id

    Returns a tuple (id, timestamp, owner, title, location, company, description)

    """

    cursor = db.cursor()
    query = """SELECT id, timestamp, owner, title, location, company, description FROM positions WHERE id = ?"""
    position_set = cursor.execute(query, [id])
    if position_set:
        return cursor.fetchone()
    else:
        return None


def position_add(db, usernick, title, location, company, description):
    """Add a new post to the database.
    The date of the post will be the current time and date.
    Only add the record if usernick matches an existing user

    Return True if the record was added, False if not."""
    cur = db.cursor()
    cur.execute("SELECT nick from users where nick=?", [usernick])
    name = cur.fetchone()
    if not name:
        return False
    cur.execute("INSERT INTO positions(owner, title, location, company, description) VALUES (?,?,?,?,?)",[usernick,title,location,company,description])
    db.commit
    return True



