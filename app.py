from flask import (Flask, render_template, make_response, url_for, 
                    request, redirect, flash)
import sys,os,random
import lookup

app = Flask(__name__)

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('index.html', page_title = "Movie CRUD")

@app.route('/insert/', methods=["GET","POST"])
def insert():
    if request.method == "GET":
        return render_template('insert.html', page_title="Movie Insert")
    elif request.method == "POST":
        conn = lookup.getConn('achan_db')
        tid = request.form['movie-tt']
        mtitle = request.form['movie-title']
        year = request.form['movie-release']

        #Error checking
        
        redirect = True #initialize to say whether to redirect or not
        if not tid.isdigit():
            flash('error: tt must be numeric')
            redirect = False #will go back to the same page
        elif not year.isdigit():
            flash('error: release year must be numeric')
            redirect = False
        elif lookup.checkMovie(tid) is not None:
            flash('error: Movie already exists. Movie with tt=%s is already in database', 
                    [tid])
            redirect = False
        elif mtitle == "":
            flash('error: Missing title')
            redirect = False
        elif tid == "":
            flash('error: Missing tt')
            redirect = False
        elif year == "":
            flash('error: Missing year')
            redirect = False

        if redirect == False: #go back to the same page
            return redirect(url_for('insert', page_title="Movie Insert"))

        #Go to the update page
        lookup.insertMovie(conn, tid, mtitle, year)
        return redirect(url_for('update', tt = tid))

@app.route('/search/', methods=["GET","POST"])
def search():
    if request.method == "GET":
        return render_template('search.html', page_title="Movie Search")
    elif request.method == "POST":
        conn = lookup.getConn('achan_db')
        ask = request.form['search-title']
        id = lookup.searchMovie(conn, ask)
        if id == None:
            flash("No movie matches. Please try again.")
            return render_template('search.html', page_title="Movie Search")
        return redirect(url_for('update', tt=id))

@app.route('/update/<tt>', methods=["GET","POST"])
def update(tt):
    conn = lookup.getConn('achan_db')
    
    if request.method == "GET":
        movie = lookup.getMovie(conn, tt)
        return render_template('update.html', page_title="Update Movie", defaultform = movie)
    
    #POST update
    elif request.method == "POST" and request.form['submit'] == 'update':
        title = request.form['movie-title']
        newtt = request.form['movie-tt']
        release = request.form['movie-release']
        director = request.form['movie-director']
        addedby = request.form['movie-addedby']

        #Error checking
        works = True #initialize the boolean
        if not newtt.isdigit():
            flash('error: tt must be numeric')
            works = False #the form won't work
        elif newtt != tt:
            isThere = lookup.checkMovie(conn, newtt)
            if isThere:
                flash("Movie already exists")
                works = False 
        elif not release.isdigit():
            flash('error: release year must be numeric')
            works = False
        elif not addedby.isdigit():
            flash('error: addedby must be numeric')
            works = False
        #Redirects        
        if works == False: #if the form doesn't work
            i = lookup.getMovie(conn, tt)
            return render_template('update.html', page_title="Update Movie", defaultform = i)
        
        #if the form works, then we update
        lookup.updateMovie(conn, tt, newtt, title, release, addedby, director)
        flash('Movie was updated successfully')
        i = lookup.getMovie(conn, newtt)
        return render_template('update.html', page_title="Update Movie", defaultform = i)

    #POST delete
    elif request.method == "POST" and request.form['submit'] == 'delete':
        lookup.deleteMovie(conn, tt)
        flash('Movie was successfully deleted')
        return redirect(url_for('index'))


@app.route('/select/', methods=["GET","POST"])
def select():
    if request.method == "GET":
        conn = lookup.getConn('achan_db')
        incompleteList = lookup.selectIncomplete(conn)
        return render_template('select.html', page_title="Movie Select", movies = incompleteList)
    elif request.method == "POST":
        tid = request.form['menu-tt']
        return redirect(url_for('update', tt=tid))

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)