import dbi

DSN = None

def getConn(db):
    '''returns a database connection to the given database'''
    global DSN
    if DSN is None:
        DSN = dbi.read_cnf()
    conn = dbi.connect(DSN)
    conn.select_db(db)
    return conn

def searchMovie(conn, ask):
    '''Returns the tt of the first movie that matches the search query'''
    curs = dbi.cursor(conn)
    curs.execute('''select tt from movie where title like %s''',['%'+ask+'%'])
    s = curs.fetchone()
    if s is None:
        return s
    else:
        return s[0]

def selectIncomplete(conn):
    '''Returns a list of titles of movies where either the director or release year is null'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select title, tt from movie where director is null or `release` is null''')
    return curs.fetchall()

def insertMovie(conn, tt, title, year):
    '''Given the movie's tt, title, and release year, 
    it inserts the movie to the database'''
    curs = dbi.cursor(conn)
    addedby = 1380
    curs.execute('''insert into movies(tt, title, `release`, addedby) values (%s, %s, %s, %s)''',
                                [tt, title, year, addedby])

def checkMovie(conn, tt):
    '''Given the tt of a movie, it checks if it's in the database 
    and returns null or the title'''
    curs = dbi.cursor(conn)
    curs.execute('''select title from movie where tt=%s''', [tt])
    s = curs.fetchone()
    if s is None:
        return s
    else:
        return s[0]

def getMovie(conn, tt):
    '''Given the tt of a movie, it gets title, tt, release year, 
    addedby, director id, and the director'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select tt, title, `release`, movie.addedby, 
            director, p.name from movie left join person as p on(director=nm) where tt = %s''', [tt])
    forminfo = curs.fetchone()
    return forminfo

def deleteMovie(conn, tt):
    '''Deletes a movie with the given tt from the database'''
    curs = dbi.cursor(conn)
    curs.execute('''delete from movie where tt = %s''', [tt])

def updateMovie(conn, tt, newtt, title, release, addedby, director):
    '''Updates movie with the given tt from the database with given values'''
    curs = dbi.cursor(conn)
    curs.execute('''update movie 
                    set tt=%s, title=%s, `release`=%s, addedby=%s, director=%s 
                    where tt=%s''',
    [newtt, title, release, addedby, director, tt])