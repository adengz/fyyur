#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import logging
from logging import Formatter, FileHandler
from forms import ShowForm, VenueForm, ArtistForm
import re
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CSRFProtect(app)

def format_phone(value):
    return '-'.join(re.findall(r'\(?(\d{3})\)?[ -]?(\d{3})-?(\d{4})', value)[0])


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='venue', cascade='all, delete-orphan')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='artist', cascade='all, delete-orphan')


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

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
    areas = []
    for city, state in Venue.query.with_entities(Venue.city, Venue.state).distinct().all():
        d = {'city': city, 'state': state, 'venues': []}
        for venue in Venue.query.with_entities(Venue.id, Venue.name).filter_by(city=city, state=state).order_by(Venue.id).all():
            dv = {'id': venue.id, 'name': venue.name}
            dv['num_upcoming_shows'] = len(Show.query.filter_by(venue_id=venue.id).filter(Show.start_time>=datetime.now()).all())
            d['venues'].append(dv)
        areas.append(d)
    return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    response = {'data': []}
    for venue in Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.like('%{}%'.format(search_term))).all():
        d = {'id': venue.id, 'name': venue.name}
        d['num_upcoming_shows'] = len(Show.query.filter_by(venue_id=venue.id).filter(Show.start_time>=datetime.now()).all())
        response['data'].append(d)
    response['count'] = len(response['data'])
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        abort(404)
    shows = Show.query.filter_by(venue_id=venue_id)

    def get_show_info(show):
        d = {'artist_id': show.artist_id, 'start_time': str(show.start_time)}
        artist = show.artist
        d['artist_name'] = artist.name
        d['artist_image_link'] = artist.image_link
        return d

    venue.past_shows, venue.upcoming_shows = [], []
    for show in shows.filter(Show.start_time<datetime.now()).order_by(Show.start_time.desc()).all():
        venue.past_shows.append(get_show_info(show))
    for show in shows.filter(Show.start_time>=datetime.now()).order_by(Show.start_time).all():
        venue.upcoming_shows.append(get_show_info(show))
    venue.past_shows_count = len(venue.past_shows)
    venue.upcoming_shows_count = len(venue.upcoming_shows)
    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue = Venue()
    form = VenueForm()
    if not form.validate_on_submit():
        flash('Invalid value found in ' + ', '.join(form.errors.keys()) + ' field(s).')
        return render_template('forms/new_venue.html', form=form)
    else:
        error = False
        try:
            form.populate_obj(venue)
            venue.phone = format_phone(venue.phone)
            db.session.add(venue)
            db.session.flush()
            venue_id = venue.id
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
            return redirect(url_for('index'))
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        abort(404)
    name = venue.name
    error = False
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash('Venue ' + name + ' was successfully deleted!')
        return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.with_entities(Artist.id, Artist.name).order_by(Artist.id).all()
    return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    response = {'data': []}
    for artist in Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.like('%{}%'.format(search_term))).all():
        d = {'id': artist.id, 'name': artist.name}
        d['num_upcoming_shows'] = len(Show.query.filter_by(artist_id=artist.id).filter(Show.start_time>=datetime.now()).all())
        response['data'].append(d)
    response['count'] = len(response['data'])
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        abort(404)
    shows = Show.query.filter_by(artist_id=artist_id)

    def get_show_info(show):
        d = {'venue_id': show.venue_id, 'start_time': str(show.start_time)}
        venue = show.venue
        d['venue_name'] = venue.name
        d['venue_image_link'] = venue.image_link
        return d

    artist.past_shows, artist.upcoming_shows = [], []
    for show in shows.filter(Show.start_time<datetime.now()).order_by(Show.start_time.desc()).all():
        artist.past_shows.append(get_show_info(show))
    for show in shows.filter(Show.start_time>=datetime.now()).order_by(Show.start_time).all():
        artist.upcoming_shows.append(get_show_info(show))
    artist.past_shows_count = len(artist.past_shows)
    artist.upcoming_shows_count = len(artist.upcoming_shows)
    return render_template('pages/show_artist.html', artist=artist)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    artist = Artist()
    form = ArtistForm()
    if not form.validate_on_submit():
        flash('Invalid value found in ' + ', '.join(form.errors.keys()) + ' field(s).')
        return render_template('forms/new_artist.html', form=form)
    else:
        error = False
        try:
            form.populate_obj(artist)
            artist.phone = format_phone(artist.phone)
            db.session.add(artist)
            db.session.flush()
            artist_id = artist.id
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
            return redirect(url_for('index'))
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('show_artist', artist_id=artist_id))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        abort(404)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    if Artist is None:
        abort(404)
    name = Artist.name
    form = ArtistForm()
    if not form.validate_on_submit():
        flash('Invalid value found in ' + ', '.join(form.errors.keys()) + ' field(s).')
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        error = False
        try:
            edited = Artist()
            form.populate_obj(edited)
            for col in Artist.__table__.columns.keys():
                if col != 'id':
                    setattr(artist, col, getattr(edited, col))
            name = artist.name
            artist.phone = format_phone(artist.phone)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Artist ' + name + ' could not be updated.')
            return redirect(url_for('index'))
        else:
            flash('Artist ' + name + ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        abort(404)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        abort(404)
    name = venue.name
    form = VenueForm()
    if not form.validate_on_submit():
        flash('Invalid value found in ' + ', '.join(form.errors.keys()) + ' field(s).')
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        error = False
        try:
            edited = Venue()
            form.populate_obj(edited)
            for col in Venue.__table__.columns.keys():
                if col != 'id':
                    setattr(venue, col, getattr(edited, col))
            name = venue.name
            venue.phone = format_phone(venue.phone)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Venue ' + name + ' could not be updated.')
            return redirect(url_for('index'))
        else:
            flash('Venue ' + name + ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = []
    for show in Show.query.order_by(Show.start_time).all():
        d = {'venue_id': show.venue_id, 'artist_id': show.artist_id, 'start_time': str(show.start_time)}
        d['venue_name'] = show.venue.name
        artist = show.artist
        d['artist_name'] = artist.name
        d['artist_image_link'] = artist.image_link
        shows.append(d)
    return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show = Show()
    form = ShowForm()
    if not form.validate_on_submit():
        flash('Invalid value found in ' + ', '.join(form.errors.keys()) + ' field(s).')
        return render_template('forms/new_show.html', form=form)
    else:
        error = False
        try:
            form.populate_obj(show)
            db.session.add(show)
            db.session.flush()
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')
        return redirect(url_for('index'))

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
