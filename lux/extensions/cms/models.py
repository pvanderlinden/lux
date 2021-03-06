from datetime import datetime

import odm

from odm.types import JSONType

from sqlalchemy.orm import relationship
from sqlalchemy import (Column, Integer, String, Text, Boolean, ForeignKey,
                        DateTime)


class Template(odm.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    body = Column(Text)


class Page(odm.Model):
    id = Column(Integer, primary_key=True)
    path = Column(String(256), unique=True)
    title = Column(String(256))
    description = Column(Text)
    template_id = Column(Integer, ForeignKey('template.id'),
                         doc='Body Template')
    layout = Column(JSONType)
    published = Column(Boolean, default=False)
    updated = Column(DateTime, default=datetime.utcnow)
    root = Column(String(256))
    '''An identifier for a group of pages.'''

    template = relationship(Template)
