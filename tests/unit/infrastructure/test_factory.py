import pytest
from datajoint.user_tables import Lookup, Part

from repro.adapters.abstract import PartEntity
from repro.infrastructure.factory import RecordTableFactory


@pytest.fixture
def fake_schema():
    class FakeSchema:
        def __init__(self):
            self.table_cls = None
            self.context = None

        def __call__(self, cls, context=None):
            self.table_cls = cls
            self.context = context
            return cls

        def __repr__(self):
            return "FakeSchema()"

    return FakeSchema()


@pytest.fixture
def fake_parent():
    class FakeParent:
        pass

    return FakeParent


@pytest.fixture
def factory(fake_schema, fake_parent):
    return RecordTableFactory(fake_schema, parent=fake_parent)


@pytest.fixture
def produce_instance(factory):
    return factory()


@pytest.mark.usefixtures("factory")
def test_table_is_created_when_factory_is_initialized(fake_schema):
    assert fake_schema.table_cls


@pytest.mark.usefixtures("produce_instance")
class TestMasterClass:
    @staticmethod
    def test_class_has_correct_name(fake_schema):
        assert fake_schema.table_cls.__name__ == "FakeParentRecord"

    @staticmethod
    def test_class_is_lookup_table(fake_schema):
        assert issubclass(fake_schema.table_cls, Lookup)

    @staticmethod
    def test_class_has_correct_definition(fake_schema):
        assert fake_schema.table_cls.definition == "-> FakeParent"


@pytest.mark.parametrize("part", PartEntity.__subclasses__())
@pytest.mark.usefixtures("produce_instance")
class TestPartClasses:
    @staticmethod
    def test_part_classes_are_present_on_table_class(fake_schema, part):
        assert hasattr(fake_schema.table_cls, part.__name__)

    @staticmethod
    def test_part_classes_are_subclass_of_part_table(fake_schema, part):
        assert issubclass(getattr(fake_schema.table_cls, part.__name__), Part)

    @staticmethod
    def test_part_classes_have_correct_definitions(fake_schema, part):
        assert getattr(fake_schema.table_cls, part.__name__).definition == part.definition


@pytest.mark.usefixtures("produce_instance")
def test_schema_is_called_with_correct_context(fake_schema, fake_parent):
    assert fake_schema.context == {"FakeParent": fake_parent}


def test_if_instance_is_instance_of_class(produce_instance, fake_schema):
    assert isinstance(produce_instance, fake_schema.table_cls)


def test_instance_is_cached(factory):
    assert factory() is factory()


def test_repr(factory, fake_parent):
    assert repr(factory) == f"RecordTableFactory(schema=FakeSchema(), parent={repr(fake_parent)})"