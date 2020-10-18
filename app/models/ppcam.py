import logging
import datetime
from app import db, ma
from app.models.blacklist_device_token import BlacklistDeviceToken
import jwt

class Ppcam(db.Model):
    __tablename__ = 'ppcam'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    serial_num = db.Column(db.String(250), unique = True, nullable = False)
    ip_address = db.Column(db.String(250), unique = True, nullable = False)
    created_date = db.Column(db.DateTime(timezone=True), nullable = False, default=datetime.datetime.utcnow())
    last_modified_date = db.Column(db.DateTime(timezone=True), nullable = False, default=datetime.datetime.utcnow())

    user = db.relationship('User',
        backref=db.backref('ppcams'), lazy = True)

    # def __repr__(self):
    #     return f"<Ppcam : {self.id}, {self.serial_num}>"


    def encode_auth_token(self, ppcam_id: int) -> str:
        '''
        Generate device auth token
        :Param: Integer
        :Return: String|String(error msg)
        '''
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': ppcam_id
            }
            from manage import app
            return jwt.encode(
                payload,
                app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(device_auth_token: str):
        """
        Decodes the device auth token
        :Params: String
        :Return: integer|string
        """
        try:
            from manage import app
            payload = jwt.decode(device_auth_token, app.config['JWT_SECRET_KEY'])
            is_blacklisted_token = BlacklistDeviceToken.check_blacklist(device_auth_token)
            if is_blacklisted_token:
                return 'Device token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def get_ppsnack(self, test=False):
        """
        request ppcam to get method for ppsnack
        params Boolean
        returns JSON(ppsnack data)
        """
        if(test):
            # FAKE DATA FOR TESTING
            return {
                "serial_num":"thisisfakedata",
                "connection":"True",
                "power":"True",
                "feedback_ratio":"1"
            }
        else:
            pass

    def put_ppsnack(self, feedback_ratio, test=False):
        """
        request ppcam to put method for ppsnack
        params Float, Boolean
        returns Boolean
        """
        if(test):
            # FAKE SUCCESS MSG TEMPLATE
            {
                "status":"FAKESUCCESS",
                "msg":"this is fake success"
            }
            return True
        else:
            pass

    @staticmethod
    def generate_fake(count):
        # Generate a number of fake ppcams for testing
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker
        from app.statics.test_samples import ppcam_samples

        fake = Faker()

        seed()
        for i in range(count):
            p = Ppcam(
                serial_num = ppcam_samples[(i % 10)], # 10 is number of samples
                ip_address = fake.ipv4(),
                # match one foreign_key by one user
                # user id start from 1
                user_id = i+1
            )
            db.session.add(p)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            
        logging.info('Successed to set fake ppcams')


class PpcamSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ppcam
        include_fk = True