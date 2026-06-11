from event_people.config import Config

class Listener:
    @staticmethod
    def on(event_name, callback=None, max_attempts=None, delay_strategy=None, dlq_name=None):
        retry_config = Config.get_retry_config()
        resolved_max_attempts = max_attempts if max_attempts is not None else retry_config['max_attempts']
        resolved_delay_strategy = delay_strategy if delay_strategy is not None else retry_config['delay_strategy']
        resolved_dlq_name = dlq_name if dlq_name is not None else retry_config['dlq_name']

        broker_callback = callback if callback else Listener.basic_callback
        queue_names = [event_name]
        broker = Config.get_broker()
        channel = broker.get_connection()

        if len(event_name.split('.')) == 3:
            queue_names = [f'{event_name}.all', f'{event_name}.{Config.APP_NAME}']

        retry_params = {
            'max_retries': resolved_max_attempts,
            'delay_strategy': resolved_delay_strategy,
            'dlq_name': resolved_dlq_name,
        }

        for queue_name in queue_names:
            broker.consume(queue_name, broker_callback, continuous=False, retry_params=retry_params)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:#pragma: no cover
            channel.stop_consuming()#pragma: no cover

    def basic_callback(event, context):
        print(event.name)#pragma: no cover
        print(event.header)#pragma: no cover
        print(event.body)#pragma: no cover
        context.success()#pragma: no cover

