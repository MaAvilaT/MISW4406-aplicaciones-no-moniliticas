from flask import request, jsonify, current_app
from src.commands.process_lab_result_command import ProcessLabResultCommand
from src.events.lab_result_submitted_event import LabResultSubmittedEvent
from src.services.rabbitmq_service import RabbitMQService
import threading


class LabResultHandler:
    """
    Handler for processing HTTP requests related to lab results.
    Implements CQS pattern (Command Query Separation).
    Singleton pattern ensures only one instance exists.
    """

    _instance = None
    _lock = threading.Lock()  # Thread safety for Singleton initialization

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LabResultHandler, cls).__new__(cls)
                    cls._instance.__init_once()  # Call custom init method
        return cls._instance

    def __init_once(self):
        """Initialize only once (ensures RabbitMQ connection is reused)."""
        self.rabbitmq_service = RabbitMQService()

    def handle_request(self):
        """Handles the HTTP request to process lab results."""
        if not request.json:
            return jsonify({'error': 'Request must be JSON'}), 400

        try:
            data = request.json

            # Create and execute the command
            command = ProcessLabResultCommand(
                patient_id=data.get('patient_id'),
                lab_name=data.get('lab_name'),
                raw_data=data
            )

            command_data = command.to_dict()

            # Publish the message to RabbitMQ
            message_id = self.rabbitmq_service.publish_message(command_data)

            # Create and return the event
            event = LabResultSubmittedEvent(
                lab_id=command_data['lab_id'],
                patient_uuid=command_data['patient_uuid'],
                message_id=message_id
            )

            return jsonify({
                'status': 'success',
                'message': 'Lab result sent to processing queue',
                'details': event.to_dict()
            }), 202

        except Exception as e:
            current_app.logger.error(f'Error: {str(e)}')
            return jsonify({'error': str(e)}), 500
