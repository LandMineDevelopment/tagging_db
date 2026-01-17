"""
Database storage backend using SQLite.
Provides fast queries for large datasets.
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from .interfaces import StorageInterface

Base = declarative_base()

# Association table for many-to-many
file_tags = Table('file_tags', Base.metadata,
    Column('file_id', Integer, ForeignKey('files.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    Column('added_at', DateTime, default=None)
)

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    tags = relationship('Tag', secondary=file_tags, back_populates='files')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    files = relationship('File', secondary=file_tags, back_populates='tags')

class Exclusion(Base):
    __tablename__ = 'exclusions'
    id = Column(Integer, primary_key=True)
    tag1_id = Column(Integer, ForeignKey('tags.id'), nullable=False)
    tag2_id = Column(Integer, ForeignKey('tags.id'), nullable=False)

class DatabaseStorage(StorageInterface):
    """Storage implementation using SQLite database."""
    
    def __init__(self, config):
        self.config = config
        db_path = config.get('db_path', 'tags.db')
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def _extract_type(self, file_path):
        return Path(file_path).suffix.lstrip('.').lower() or 'unknown'
    
    def add_tags(self, file_path, tags):
        session = self.Session()
        try:
            # Get or create file
            file_obj = session.query(File).filter_by(path=file_path).first()
            if not file_obj:
                file_type = self._extract_type(file_path)
                file_obj = File(path=file_path, type=file_type)
                session.add(file_obj)
                session.flush()  # Get ID
            
            for tag_key, tag_value in tags:
                full_tag = f"{tag_key}{self.config.get('separator', '/')}{tag_value}" if tag_value else tag_key
                tag_obj = session.query(Tag).filter_by(name=full_tag).first()
                if not tag_obj:
                    tag_obj = Tag(name=full_tag)
                    session.add(tag_obj)
                    session.flush()
                
                # Check if association exists
                if tag_obj not in file_obj.tags:
                    file_obj.tags.append(tag_obj)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_tags(self, file_path):
        session = self.Session()
        try:
            file_obj = session.query(File).filter_by(path=file_path).first()
            if file_obj:
                return [tag.name for tag in file_obj.tags]
            return []
        finally:
            session.close()
    
    def search(self, query, type_filter=None, fuzzy=False):
        session = self.Session()
        try:
            from fuzzywuzzy import fuzz
            query_obj = session.query(File)
            if type_filter:
                query_obj = query_obj.filter(File.type == type_filter)
            
            results = {}
            for file_obj in query_obj:
                matching_tags = []
                for tag in file_obj.tags:
                    if fuzzy:
                        if any(fuzz.partial_ratio(query, part) >= 70 for part in tag.name.split('/')):
                            matching_tags.append(tag.name)
                    else:
                        # Regex search with wildcards
                        query_regex = query.replace('*', '.*')
                        try:
                            if re.search(query_regex, tag.name):
                                matching_tags.append(tag.name)
                        except re.error:
                            pass
                if matching_tags:
                    results[file_obj.path] = matching_tags
            return results
        finally:
            session.close()
    
    def remove_tags(self, file_path, tags):
        session = self.Session()
        try:
            file_obj = session.query(File).filter_by(path=file_path).first()
            if file_obj:
                for tag_key, tag_value in tags:
                    full_tag = f"{tag_key}{self.config.get('separator', '/')}{tag_value}" if tag_value else tag_key
                    tag_obj = session.query(Tag).filter_by(name=full_tag).first()
                    if tag_obj and tag_obj in file_obj.tags:
                        file_obj.tags.remove(tag_obj)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def batch_apply(self, folder_path, tag, type_filter=None):
        import os
        count = 0
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_type = self._extract_type(file_path)
                if not type_filter or file_type == type_filter:
                    self.add_tags(file_path, [tag])
                    count += 1
        return count
    
    def rename_tag(self, old_tag, new_tag):
        session = self.Session()
        try:
            tag_obj = session.query(Tag).filter_by(name=old_tag).first()
            if tag_obj:
                tag_obj.name = new_tag
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_tags(self):
        session = self.Session()
        try:
            tags = session.query(Tag.name).all()
            return [tag[0] for tag in tags]
        finally:
            session.close()
    
    def get_all_data(self):
        session = self.Session()
        try:
            data = {}
            for file_obj in session.query(File).all():
                data[file_obj.path] = [tag.name for tag in file_obj.tags]
            return data
        finally:
            session.close()