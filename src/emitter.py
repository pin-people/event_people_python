class Emitter:

    def trigger(self, *events):
        for event in events:
            Config.get_broker().produce(events)

        return events
