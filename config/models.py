from config import db


class Assistant(db.Model):
    id = db.UUIDField(primary_key=True)
    kind = db.CharField(max_length=10)
    language = db.CharField(max_length=10)
    name = db.CharField(max_length=100)

    class Meta:
        database = db.get_db()
        table_name = 'chat_assistant'


class Room(db.Model):
    id = db.UUIDField(primary_key=True)
    user_id = db.UUIDField()
    name = db.CharField(max_length=50, null=True)
    actor = db.IntegerField()
    assistant = db.ForeignKeyField(Assistant, backref='rooms')
    auto = db.BooleanField(default=True)
    notifications = db.BooleanField(default=True)
    gpt = db.BooleanField(default=True)
    tts = db.BooleanField(default=True)
    stt = db.BooleanField(default=True)
    deleted = db.BooleanField(default=False)

    class Meta:
        database = db.get_db()
        table_name = 'chat_room'


class Message(db.Model):

    INITIAL = 'initial'
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    RETRY = 'retry'
    DONE = 'done'

    KIND_AUDIO = 'audio'
    KIND_TEXT = 'text'

    TASK_TTS = 'tts'
    TASK_GPT = 'gpt'
    TASK_STT = 'stt'

    UNDELIVERED = 'undelivered'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    FAILED = 'failed'

    id = db.UUIDField(primary_key=True)
    sender_id = db.CharField(
        max_length=100,
        null=True,
    )
    response = db.ForeignKeyField('self', backref='responses', null=True)
    room = db.ForeignKeyField(Room, backref='messages')
    audio = db.TextField()
    text = db.TextField(null=True)
    language = db.CharField(max_length=20, null=True)
    current_task = db.CharField(max_length=100)
    state = db.CharField(max_length=50)
    delivery_status = db.CharField(max_length=20)
    kind = db.CharField(max_length=10)
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()
    deleted = db.BooleanField(default=False)

    class Meta:
        database = db.get_db()
        table_name = 'chat_message'
