from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from app import app, db
from datetime import datetime
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_sqlalchemy import SQLAlchemy, inspect
from sqlalchemy import func
import os
import psycopg2 as psy
import urllib.parse
import json

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

conn = psy.connect(
  database=url.path[1:],
  user=url.username,
  password=url.password,
  host=url.hostname,
  port=url.port
)

GoogleMaps(app, key="AIzaSyBqD70ZYt3164PpO6e89gQGzt9vGTOzbTw")

from .models import Board, Entry

# I use this function to unpack a list of tuples returned by the sql_alchemy query attribute, and convert each into a dictionary.

def object_as_dict(obj):
  return {c.key: getattr(obj, c.key)
    for c in inspect(obj).mapper.column_attrs}

# Use this to convert a list of dictionaries into a list of tuples, stripping out the keys and leaving only the values to be fed into Jinja2.

def get_values_as_tuple(dict_list, keys):
  return [tuple(d[k] for k in keys) for d in dict_list]

# this is the code that shows the login page.

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('session_count'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('session_count'))

@app.route('/')
def session_count():
   if not session.get('logged_in'):
      abort(401)

   cur = conn.cursor()
   cur.execute("select * from entries")
   
   session_count = len(cur.fetchall());
   return render_template("home2.html", count = session_count)


@app.route('/enternew')
def new_entry():
    if not session.get('logged_in'):
       abort(401)

    def make_list(self):
       return list(self)

    cur = conn.cursor()
    cur.execute("select beach_name from beaches")

    beach_names = cur.fetchall()

    # the results of the cursor are a tuple. need to unpack each item in the tuple and load it into a list. Create the empty list.

    beach_list = []

    # for loop to unpack each item, then append it to the new list. 

    for name in beach_names:
      beach_list.append(*name)

    sorted_beaches = sorted(beach_list)

    # send the new list to the template.

    return render_template('journal_form3.html', beach_names = sorted_beaches)

@app.route('/add_entry',methods = ['POST', 'GET'])
def add_entry():
   if request.method == 'POST':
      try:

# pull the following data out of the form fields.

         beach_name = request.form['beach_name']
         board = request.form['board']
         time_in = request.form['time_in']
         time_out = request.form['time_out']
         swell = request.form['swell']
         wind = request.form['wind']
         score = request.form['score']
         notes = request.form['notes']

#convert the time_in and time_out string values into integers so that they can be subtracted to yield a duration for the session in terms of number of seconds. 

         t_i = datetime.strptime(time_in, '%Y-%m-%dT%H:%M')
         t_o = datetime.strptime(time_out,'%Y-%m-%dT%H:%M')
         delta = t_o - t_i
         duration = delta.total_seconds() 

# define the parameters for the query that will insert a new row into the entries table. 

         query = "INSERT INTO entries (beach_name, board, swell, wind, score, notes, time_in, time_out, duration) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
         session_data = (beach_name, board, swell, wind, score, notes, time_in, time_out, duration)

# execute the query and close the connection.
         
         cur = conn.cursor()
         cur.execute(query, session_data)
         conn.commit()
         msg = "Record successfully added"

         # take the message and show it in the confirmation dialog.

         return render_template("result2.html",msg = msg)

# if the query fails, print the error message on the confirmation page. 

      except psy.Error as e:
         conn.rollback()
         msg = e.pgerror

         # take the message and show it in the confirmation dialog.

         return render_template("result2.html",msg = msg)

@app.route('/list')
def list():
   if not session.get('logged_in'):
      abort(401)

   cur = conn.cursor()
   cur.execute("select * from entries where deleted != true ORDER BY time_out DESC")
   
   rows = cur.fetchall()
   return render_template("list2.html",rows = rows)

@app.route('/random')
def random():
   if not session.get('logged_in'):
      abort(401)
      
   cur = conn.cursor()
   cur.execute("select * from entries where score = 3 and deleted != true ORDER BY RANDOM() LIMIT 1")

   rows = cur.fetchall()
   return render_template("random2.html",rows = rows)

@app.route('/atlas')
def get_beaches():
    if not session.get('logged_in'):
      abort(401)

    cur = conn.cursor()
    cur.execute("SELECT beaches.*, (SELECT COUNT(*) FROM entries WHERE entries.beach_name = beaches.beach_name) AS TOTAL FROM beaches")

    rows = cur.fetchall()
    columns = ('id', 'beach_name', 'lat', 'long', 'beach_description', 'TOTAL')
    zipped_data = []

    # zip the records that I pulled out of the database with the column names that I defined above. This zip object is called zipped_data. 

    for row in rows:
        zipped_data.append(zip(columns, row))

    # Convert the awkward zip object into a more easily used dictionary called raw_markers

    raw_markers = []

    for each_zip in zipped_data:
        raw_markers.append(dict(each_zip))

    # iterate over the dictionaries in raw_markers. Drop id and beach_description. Change long -> lng and beach_name -> infobox.

    black_list = {"id", "TOTAL"}
    rename ={"long":"lng", "beach_name":"infobox"}
    markers = []

    for each_dict in raw_markers:
        markers.append({rename.get(key, key) : val for key, val in each_dict.items() if key not in black_list})

    # iterate over the new dictionaries in markers, and add in the needed value for icon. 

    for marker in markers:
        marker.update({'icon':'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'})

    # Pass the markers dictionary to the google maps integration.

    beach_map = Map(
          identifier="beach_map",
          lat=33.1103,
          lng=-117.2326,
          markers = markers,
          zoom = 10,
          style = "height:450px;width:600px;margin:0;"
      )
    return render_template("atlas2.html", beach_map = beach_map, rows = rows)

@app.route('/hide', methods=['POST'])
def hide_entry():

   if request.method == 'POST':
      try:

# pull the row id out of the list2 hide button.

         entry_ids = request.form.get('entry_to_hide')

         # entry_ids2 = []

         # for entry_id in entry_ids:
         #    entry_ids2.append(int(entry_id))

# execute the query and close the connection.
         
         cur = conn.cursor()
         cur.execute("UPDATE entries SET deleted = true WHERE id = (%s);", (entry_ids,))
         updated_entries = cur.rowcount
         conn.commit()

         # take the message and show it in the confirmation dialog.

         return render_template("result2.html",msg = updated_entries)

# if the query fails, print the error message on the confirmation page. 

      except psy.Error as e:
         conn.rollback()
         msg = e.pgerror

         # take the message and show it in the confirmation dialog.

         return render_template("result2.html",msg = msg)

@app.route('/boards')
def list_boards():
   if not session.get('logged_in'):
      abort(401)

# Query the DB to get the list of boards and also a count of entries per board.

   boards_queried = (
      db.session.query(Board.id, Board.name, Board.length, Board.volume, Board.shaper, Board.display_name, Board.description, func.count(Entry.id).label('entry_count'), func.avg(Entry.score).label('avg_score'))
      .join(Entry, Board.name == Entry.board)
      .group_by(Board.id, Board.name, Board.length, Board.volume, Board.shaper, Board.display_name, Board.description)
)


# This is last-surfed dates for the other table at the bottom of the page. 

   boards_last_used = db.session.query((func.max(Entry.time_out)).label('time_out'), Entry.board).group_by(Entry.board)

   boards_last_used_dict_list = []

   boards_queried_dict_list = []

   boards_for_template_list = []

   # The results of the SQLAlchemy query above are returned as keyed-tuples. Need to begin by converting each of these to a dictionary. 

   for row in boards_queried.all():
        queried_row = row._asdict()
        boards_queried_dict_list.append(queried_row)


   for row in boards_last_used.all():
        last_used_row = row._asdict()
        boards_last_used_dict_list.append(last_used_row)
  
   # Now that I have a dictionary for each value, strip the HH:MM out of the "time_out" label. 

   for last_used_row in boards_last_used_dict_list:
        last_used_row['time_out'] = (last_used_row['time_out'].date())

   # Merge the boards_last_used and the boards_queried based on whether board_name and name match. 

   for queried_row in boards_queried_dict_list:
        for last_used_row in boards_last_used_dict_list:
            if queried_row['name'] == last_used_row['board']:
                queried_row.update(last_used_row)
                boards_for_template_list.append(queried_row)

# Pass the results into the template

   return render_template("boards.html",rows = boards_for_template_list)

@app.route('/beachform')
def render_beach_form():

   # Check to make sure that the user is logged in. 

   if not session.get('logged_in'):
      abort(401)

   # Show the add_beach form

   return render_template("add_beach_form.html")

@app.route('/add_beach',methods = ['POST'])
def add_beach():

# pull the following data out of the form fields on add_beach_form.html

   if request.method == 'POST':
      try:
   
         form_b_name = request.form['beach_name']
         form_lat = request.form['latitude']
         form_long = request.form['longitude']
         form_b_desc = request.form['beach_description']

      # Add the record to the db.

         new_beach = (beach_name = form_b_name, lat = form_lat, long = form_long, beach_description = form_b_desc)
         db.session.add(Beach.new_beach)
         db.session.commit()

      # take the message and show it in the confirmation dialog.

         return render_template("result2.html",msg = msg)

      except:

         msg = "Failed to add the beach."

         # take the message and show it in the confirmation dialog.

         return render_template("result2.html",msg = msg)
