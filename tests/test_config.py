class TestConfig:


    def test_env_exists(self, setup):
        from event_people.config import Config
        assert Config().RABBIT_URL == 'amqp://guest:guest@localhost:5672'
        assert Config().APP_NAME == 'service_name'
        assert Config().VHOST == 'event_people'
        assert Config().TOPIC_NAME == 'event_people'

    def test_config_get_broker(self, setup):
        from event_people.config import Config
        config = Config()
        broker = config.get_broker()
        assert broker is not None



