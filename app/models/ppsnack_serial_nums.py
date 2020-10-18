import datetime
import logging
from app import db

class PpsnackSerialNums(db.Model):
    '''
    Serial numbers are decided in ppsnack production.
    Saved for device authentication.
    ---Serial number rules---
    String length = 16
    Product code / Production region / Production line / Production date / Product number
    ___/_/_/P______/N___
    ex: PS1K1P210101N001
    '''
    __tablename__ = 'ppsnack_serial_nums'

    serial_num = db.Column(db.String(16), primary_key = True)
    production = db.Column(db.Integer, nullable = False, default=0)
    sold = db.Column(db.Integer, nullable = False, default=0)
    created_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    last_modified_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    
    @staticmethod
    def generate_fake() -> None:
        '''
        Generate a fake serial numbers for dev
        '''
        from sqlalchemy.exc import IntegrityError
        from app.statics.test_samples import ppsnack_samples
        
        for i in range(len(ppsnack_samples)):
            fake_record = PpsnackSerialNums(
                serial_num = ppsnack_samples[i]
                # other fields have default values
            )
            db.session.add(fake_record)
        # commit once
        try:
            db.session.commit()
            logging.info('Success to generate fake ppsnack serial number records in table.')
        except IntegrityError:
            db.session.rollback()
            logging.error('Generation of fake ppsnack serial numbers is failed in db.session.commit(IntegrityError).')
