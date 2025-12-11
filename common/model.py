import json

from peewee import *

with open(r'../config.json') as j:
    db_cfg = json.load(j)['dbconfig']
database = MySQLDatabase('folktale_jy_draft', **db_cfg)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Role(BaseModel):
    created_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    id = BigAutoField()
    name = CharField(null=True)
    story_id = IntegerField(null=True)
    traits = CharField(null=True)
    update_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 'role'

class Scenes(BaseModel):
    audio_path = CharField(null=True)
    caption = CharField(null=True)
    created_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    duration = FloatField(null=True)
    id = BigAutoField()
    image_index = IntegerField(constraints=[SQL("DEFAULT 1")], null=True)
    image_path1 = CharField(null=True)
    image_path2 = CharField(null=True)
    image_path3 = CharField(null=True)
    image_path4 = CharField(null=True)
    index = IntegerField()
    prompt = CharField(null=True)
    story_id = IntegerField(null=True)
    update_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    v_prompt = CharField(null=True)
    video_path1 = CharField(null=True)
    video_path2 = CharField(null=True)
    video_path3 = CharField(null=True)

    class Meta:
        table_name = 'scenes'

class Story(BaseModel):
    content = CharField(null=True)
    created_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    id = BigAutoField()
    name = CharField(null=True)
    update_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    video_scenes_num = IntegerField(constraints=[SQL("DEFAULT 2")], null=True)

    class Meta:
        table_name = 'story'