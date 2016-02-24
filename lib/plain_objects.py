#!/usr/bin/python


class TimecardEntry:
    _id = None
    _time_stamp = None
    _in_out_flag = None
    _location_raw = None
    _latitude = None
    _longitude = None
    _altitude = None
    _city = None
    _state = None
    _zipcode = None
    _timecard_entered_flag = None

    def from_dict(self, record):
        if not isinstance(record, dict):
            raise ValueError('record is not of type dict.')

        self._id = record.get('id')
        self._id = record.get('id')
        self._time_stamp = record.get('time_stamp')
        self._in_out_flag = record.get('in_out_flag')
        self._location_raw = record.get('location_raw')
        self._latitude = record.get('latitude')
        self._longitude = record.get('longitude')
        self._altitude = record.get('altitude')
        self._city = record.get('city')
        self._state = record.get('state')
        self._zipcode = record.get('zipcode')
        self._timecard_entered_flag = record.get('timecard_entered_flag')
        if self._timecard_entered_flag is not None and self._timecard_entered_flag == 'Y':
            self._timecard_entered_flag = True
        elif self._timecard_entered_flag is not None and self._timecard_entered_flag == 'N':
            self._timecard_entered_flag = False

    def to_dict(self):
        d = {}
        if self._id is not None:
            d.update({'id': self._id})
        if self._time_stamp is not None:
            d.update({'time_stamp': self._time_stamp})
        if self._in_out_flag is not None:
            d.update({'in_out_flag': self._in_out_flag})
        if self._location_raw is not None:
            d.update({'location_raw': self._location_raw})
        if self._latitude is not None:
            d.update({'latitude': self._latitude})
        if self._longitude is not None:
            d.update({'longitude': self._longitude})
        if self._altitude is not None:
            d.update({'altitude': self._altitude})
        if self._city is not None:
            d.update({'city': self._city})
        if self._state is not None:
            d.update({'state': self._state})
        if self._zipcode is not None:
            d.update({'zipcode': self._zipcode})
        if self._timecard_entered_flag is not None:
            d.update({'timecard_entered_flag': self._timecard_entered_flag})

        return d

    def set_id(self, id):
        self._id = id

    def get_id(self):
        return self._id

    def set_time_stamp(self, time_stamp):
        self._time_stamp = time_stamp

    def get_time_stamp(self):
        return self._time_stamp

    def set_in_out_flag(self, in_out_flag):
        self._in_out_flag = in_out_flag

    def get_in_out_flag(self):
        return self._in_out_flag

    def set_location_raw(self, location_raw):
        self._location_raw = location_raw

    def get_location_raw(self):
        return self._location_raw

    def set_latitude(self, latitude):
        self._latitude = latitude

    def get_latitude(self):
        return self._latitude

    def set_longitude(self, longitude):
        self._longitude = longitude

    def get_longitude(self):
        return self._longitude

    def set_altitude(self, altitude):
        self._altitude = altitude

    def get_altitude(self):
        return self._altitude

    def set_city(self, city):
        self._city = city

    def get_city(self):
        return self._city

    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self._state

    def set_zipcode(self, zipcode):
        self._zipcode = zipcode

    def get_zipcode(self):
        return self._zipcode

    def set_timecard_entered_flag(self, timecard_entered_flag):
        self._timecard_entered_flag = timecard_entered_flag

    def get_timecard_entered_flag(self):
        return self._timecard_entered_flag