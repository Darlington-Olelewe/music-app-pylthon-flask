import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database Done

#----------------------------------------------------------------------------#
# Models.     complete = db.Column(db.Boolean, nullable=False, default=False)
#----------------------------------------------------------------------------#
class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

artist_genre_table = db.Table('artist_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

venue_genre_table = db.Table('venue_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre', secondary=venue_genre_table, backref=db.backref('venues'))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(255) )
    seeking_talent = db.Column(db.Boolean(), nullable = False, default = False)
    seeking_description = db.Column(db.String(), nullable = True, default = name)
    venue_shows = db.relationship('Show', back_populates = 'venue', lazy = True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre', secondary=artist_genre_table, backref=db.backref('artists'))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(255) )
    seeking_venue = db.Column(db.Boolean(), nullable = False, default = False)
    seeking_description = db.Column(db.String(), nullable = True, default = name)
    artist_shows = db.relationship('Show', back_populates = 'artist', lazy = False)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
    artist_name = db.Column(db.String(), nullable = False)
    artist_image_link = db.Column(db.String(), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    venue_name = db.Column(db.String(), nullable = False)
    start_time = db.Column(db.DateTime, nullable = False)
    venue = db.relationship('Venue', back_populates = 'venue_shows')
    artist = db.relationship('Artist', back_populates = 'artist_shows')




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def fetch_artist(artist):
  now = datetime.now()
  past_shows = []
  upcoming_shows = []

  for show in artist.artist_shows:

    if(show.start_time < now):
      newShow = {
      "venue_id" : show.venue_id,
      "venue_name": show.venue_name,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": format_datetime(str(show.start_time))
    }
      past_shows.append(newShow)
    else:
      newShow = {
      "venue_id" : show.venue_id,
      "venue_name": show.venue_name,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": format_datetime(str(show.start_time))
    }
      upcoming_shows.append(newShow)
  data = {
     "id": artist.id,
     "name": artist.name,
     "city": artist.city,
     "genres": [ genre.name for genre in artist.genres ],
     "facebook_link": artist.facebook_link,
     "website" : artist.website_link,
     "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
     "seeking_venue" : artist.seeking_venue,
     "seeking_description" : artist.seeking_description,
     "past_shows": past_shows,
     "upcoming_shows": upcoming_shows,
     "past_shows_count":len(past_shows),
     "upcoming_shows_count": len(upcoming_shows)
   }
  return data


def fetch_artist_list(artist_list):
  now = datetime.now()
  custom_artist_list = []
  for artist in artist_list:
    past_shows = []
    upcoming_shows = []

    for show in artist.artist_shows:
      if(show.start_time < now):
        past_shows.append(show)
      else:
        upcoming_shows.append(show)


    data = {
     "id": artist.id,
     "name": artist.name,
     "city": artist.city,
     "genres": artist.genres,
     "facebook_link": artist.facebook_link,
     "website_link" : artist.website_link,
     "seeking_venue" : artist.seeking_venue,
     "seeking_description" : artist.seeking_description,
     "past_shows": past_shows,
     "upcoming_shows": upcoming_shows,
     "past_shows_count":len(past_shows),
     "upcoming_shows_count": len(upcoming_shows)
   }
    custom_artist_list.append(data)
  return custom_artist_list

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  venue_list = Venue.query.all()

  return render_template('pages/venues.html', areas=venue_list)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venues = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
  venue_list = []
  now = datetime.now()
  for venue in venues:
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming = 0
      for show in venue_shows:
          if show.start_time > now:
              num_upcoming += 1
      venue_list.append({
          "id": venue.id,
          "name": venue.name
      })
  response = {
      "count": len(venues),
      "data": venue_list
  }
  
   
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    address = request.form['address']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_talent = True if request.form['seeking_talent'] == 'y' else False
    seeking_description = request.form['seeking_description']
    venue = Venue(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres,facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent,address = address,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist_list = Artist.query.all()
  return render_template('pages/artists.html', artists=artist_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artists = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  new_response = {
    "count":len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=new_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  data = fetch_artist(artist)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  real_artist = Artist.query.get(artist_id)
  artist={
    "id": real_artist.id,
    "name": real_artist.name,
    "genres": real_artist.genres,
    "city": real_artist.city,
    "state": real_artist.state,
    "phone": (real_artist.phone[:3] + '-' + real_artist.phone[3:6] + '-' + real_artist.phone[6:]),
    "website": real_artist.website_link,
    "facebook_link": real_artist.facebook_link,
    "seeking_venue": 'y' if real_artist.seeking_venue == True else 'n',
    "seeking_description": real_artist.seeking_description,
    "image_link": real_artist.image_link,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    update_artist = Artist.query.get(artist_id)
    db.session.add(update_artist)
    update_artist.name = request.form['name']
    update_artist.city = request.form['city']
    update_artist.state = request.form['state']
    update_artist.phone = request.form['phone']
    update_artist.image_link = request.form['image_link']
    update_artist.genres = request.form['genres']
    update_artist.facebook_link = request.form['facebook_link']
    update_artist.website_link = request.form['website_link']
    update_artist.seeking_venue = True if request.form['seeking_venue'] == 'y' else False
    update_artist.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' updated.')
  except:
    flash('An error occured. Artist ' + request.form['name'] + ' could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_venue = True if request.form['seeking_venue'] == 'y' else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link,facebook_link=facebook_link, website_link=website_link, seeking_venue=seeking_venue,seeking_description=seeking_description)
    for genre in genres:
       fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
       if fetch_genre:
           artist.genres.append(fetch_genre)
       else:
           new_genre = Genre(name=genre)
           db.session.add(new_genre)
           artist.genres.append(new_genre) 

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  my_list = []
  show_list = Show.query.all()

  for shows in show_list:
    newShow = {
      "venue_id" : shows.venue_id,
      "venue_name": shows.venue_name,
      "artist_name": shows.artist_name,
      "artist_image_link": shows.artist_image_link,
      "start_time": str(shows.start_time)
    }
    my_list.append(newShow)

  return render_template('pages/shows.html', shows=my_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    print("this is for start_time")
    print(start_time)
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    show = Show(artist_id=artist_id,artist_name=artist.name, artist_image_link=artist.image_link, venue_id=venue_id,venue_name=venue.name,start_time = start_time)
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
