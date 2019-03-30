from app import db

class Board(db.Model):

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    length = db.Column(db.Integer)
    volume = db.Column(db.Integer)
    shaper = db.Column(db.String(256))
    display_name = db.Column(db.String(256))
    description = db.Column(db.String(256))

    def __init__(id, name, length, volume, shaper, display_name, description):
        self.id = id
        self.name = name
        self.length = length
        self.volume = volume
        self.shaper = shaper
        self.display_name = display_name
        self.description = description

class Entry(db.Model):

    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    beach = db.Column(db.String(256), nullable=True)
    board = db.Column(db.String(256), nullable=False)
    swell = db.Column(db.String(256), nullable=False)
    wind = db.Column(db.String(256), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(5000), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    time_in = db.Column(db.DateTime(timezone=False))
    time_out = db.Column(db.DateTime(timezone=False))
    beach_name = db.Column(db.String(256), nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(id, beach, board, swell, wind, score, notes, duration, time_in, time_out, beach_name, deleted):
        self.id = id
        self.beach = beach
        self.board = board
        self.swell = swell
        self.wind = wind
        self.score = score
        self.notes = notes
        self.duration = duration
        self.time_in = time_in
        self.time_out = time_out
        self.beach_name = beach_name
        self.deleted = deleted

class Beach(db.Model):

    __tablename__ = 'beaches'

    id = db.Column(db.Integer, primary_key=True)
    beach_name = db.Column(db.String(256))
    lat = db.Column(db.Decimal)
    long = db.Column(db.Decimal)
    beach_description = db.Column(db.String(256))

    def __init__(id, beach_name, lat, long, beach_description):
        self.id = id
        self.beach_name = beach_name
        self.lat = lat
        self.long = long
        self.beach_description = beach_description