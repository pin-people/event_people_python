from event_people.config import Config

class Listener:
    @staticmethod
    def on(event_name, callback=None):
        """Subscribe to a specific event or pattern.

        When eventName has 3 parts, the lib subscribes to both the .all and
        .{appName} variants automatically (using ONE queue with TWO bindings).

        Retry configuration is resolved from Config defaults (set via
        Config.configure()). To override per-listener, use a BaseListener
        subclass with class-level retry attributes instead.
        """
        retry_config = Config.get_retry_config()

        broker_callback = callback if callback else Listener.basic_callback
        queue_names = [event_name]
        broker = Config.get_broker()
        channel = broker.get_connection()

        if len(event_name.split('.')) == 3:
            queue_names = [f'{event_name}.all', f'{event_name}.{Config.APP_NAME}']

        retry_params = {
            'max_retries': retry_config['max_attempts'],
            'initial_delay': retry_config['initial_delay'],
            'delay_strategy': retry_config['delay_strategy'],
            'dlq_name': retry_config['dlq_name'],
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

