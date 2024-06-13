import uuid

from datetime import datetime, timezone

from config.base_worker import BaseWorker, get_logger
from config.models import Message

logger = get_logger('worker-response-handler')


class Worker(BaseWorker):
    def on_message(self, body: dict, message) -> None:
        message_id = body.get('message_id')
        if not message_id:
            logger.warning('Message ID not found in body')
            return

        logger.info(f'Start processing message: {message_id}')
        message = Message.get_or_none(Message.id == message_id)

        if message is None:
            logger.info(f'Message {message_id} does not exist')
            return

        try:
            if body.get('failed'):
                raise ValueError('Message processing failed')
            self.process_response(message, body)
        except Exception as e:
            self.handle_processing_error(message, 'Error processing message', e)
        finally:
            logger.info(f'Finished processing message: {message_id}')

    def handle_processing_error(self, message: Message, log_message: str, exception: Exception) -> None:
        logger.exception(log_message, exc_info=exception)
        self.update_message_state(message, Message.FAILED)

    def process_response(self, message: Message, body: dict) -> None:
        task = body.get('task')
        task_methods = {
            'gpt': self._process_gpt_task,
            'tts': self._process_tts_task,
            'stt': self._process_stt_task,
        }

        method = task_methods.get(task)
        if method:
            method(message, body)
        else:
            logger.error(f'Unknown task: {task}')

    def _process_gpt_task(self, message: Message, body: dict) -> None:
        response = self.create_response_message(message, body, Message.TASK_GPT, body['result'])
        next_state, next_task = self._get_next_step(message.room, message.kind, Message.TASK_GPT)

        self.send_task_if_needed(response, next_task, response.text)
        self.send_notification_if_needed(message, response)

    def _process_tts_task(self, message: Message, body: dict) -> None:
        response = self.create_response_message(message, body, Message.TASK_TTS, audio=body['result'])

        self.send_notification_if_needed(message, response)

    def _process_stt_task(self, message: Message, body: dict) -> None:
        response = self.create_response_message(
            message,
            body,
            Message.TASK_GPT,
            body['result'], body['content']['language']
        )
        next_state, next_task = self._get_next_step(message.room, message.kind, Message.TASK_STT)

        self.send_task_if_needed(response, next_task, response.text)
        self.send_notification_if_needed(message, response)

    def create_response_message(
        self,
        message: Message,
        body: dict,
        current_task: str,
        text: str = '',
        audio: bytes = None,
        language: str = None
    ) -> Message:

        response = Message.create(
            id=uuid.uuid4(),
            sender_id=message.room.assistant_id if current_task == Message.TASK_GPT else message.room.user_id,
            room=message.room,
            kind=Message.KIND_AUDIO if audio else Message.KIND_TEXT,
            delivery_status=Message.UNDELIVERED,
            response=message,
            text=text,
            audio=audio,
            current_task=current_task,
            state=Message.DONE,
            deleted=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            language=language
        )

        self.update_message_state(message, Message.DONE)
        return response

    def _get_next_step(self, room, kind: str, current_task: str) -> tuple:
        next_state = Message.DONE
        next_task = current_task

        if kind == Message.KIND_AUDIO:
            if current_task == Message.TASK_STT and room.gpt:
                next_task = Message.TASK_GPT
                next_state = Message.RUNNING
            elif current_task == Message.TASK_GPT and room.tts:
                next_task = Message.TASK_TTS
                next_state = Message.RUNNING
        elif kind == Message.KIND_TEXT:
            if current_task == Message.TASK_GPT and room.tts:
                next_task = Message.TASK_TTS
                next_state = Message.RUNNING

        return next_state, next_task

    def send_task_if_needed(self, response: Message, next_task: str, text: str) -> None:
        if next_task == Message.TASK_TTS:
            params = {
                'message_id': str(response.id),
                'task': next_task,
                'content': {
                    'text': text,
                    'actor': response.room.actor,
                    'language': response.room.assistant.language,
                },
            }
            self.send_message(routing_key=next_task, message=params)

    def send_notification_if_needed(self, original_message: Message, response: Message) -> None:
        pass

    def update_message_state(self, message: Message, state: str) -> None:
        message.state = state
        message.updated_at = datetime.now(timezone.utc)
        message.save()


if __name__ == '__main__':
    worker = Worker()
    worker.run()
