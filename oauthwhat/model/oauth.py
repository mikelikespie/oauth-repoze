from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relation
from oauthwhat.model.meta import metadata
from oauthwhat.model.meta import Base


#Some of this is inspired by http://tav.github.com/tweetapp

class OAuthToken(Base):
    __tablename__ = 'oauth_tokens'
    oauth_token = Column(String, primary_key=True)
    oauth_token_secret = Column(String)
    specifier = Column(String) #This is the username and whatnot
    authorized = Column(Boolean)
    created = Column(DateTime, onupdate=func.current_timestamp())


    def __init__(self, oauth_token = None, oauth_token_secret = None, specifier = None, authorized = False):
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.specifier = specifier
        self.authorized = authorized

    def __repr__(self):
        return u"<OAuthToken (%s, %s, %s, %s, %s, %s)>" % (
                self.oauth_token,
                self.oauth_token_secret,
                self.specifier,
                self.authorized,
                self.created)
    


