from griptapecli.core.models import Event, Run, Structure


class TestModels:
    def test_event_model_init(self):
        assert Event(value={})

    def test_run_model_init(self):
        assert Run()

    def test_structure_model_init(self):
        assert Structure(
            directory="directory",
            main_file="main_file",
        )
