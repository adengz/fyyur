from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, Optional


_states = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

_genres = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]


NAME = StringField('name', validators=[DataRequired()])
CITY = StringField('city', validators=[DataRequired()])
STATE = SelectField('state', validators=[DataRequired()], choices=_states)
PHONE = StringField(
    'phone',
    validators=[
        DataRequired(),
        Regexp(r'\(?\d{3}\)?[ -]?\d{3}-?\d{4}')
    ]
)
GENRES = SelectMultipleField('genres', validators=[DataRequired()], choices= _genres)
IMAGE_LINK = StringField('image_link', validators=[Optional(), URL()])
WEBSITE = StringField('website', validators=[Optional(), URL()])
FB_LINK = StringField('facebook_link', validators=[Optional(), URL()])
SEEK_DESC = StringField('seeking_description')


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    name = NAME
    city = CITY
    state = STATE
    address = StringField('address', validators=[DataRequired()])
    phone = PHONE
    genres = GENRES
    image_link = IMAGE_LINK
    website = WEBSITE
    facebook_link = FB_LINK
    seeking = BooleanField('seeking_talent')
    seeking_description = SEEK_DESC

class ArtistForm(FlaskForm):
    name = NAME
    city = CITY
    state = STATE
    phone = PHONE
    genres = GENRES
    image_link = IMAGE_LINK
    website = WEBSITE
    facebook_link = FB_LINK
    seeking = BooleanField('seeking_venue')
    seeking_description = SEEK_DESC
