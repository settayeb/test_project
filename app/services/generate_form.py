from typing import Any, Dict

from baml_client.type_builder import TypeBuilder
from baml_client.async_client import BamlAsyncClient
import asyncio

class SchemaAdder:
    '''
    A class to dynamically parse a JSON schema and add types to a TypeBuilder.
    '''
    # Taken from https://github.com/BoundaryML/baml-examples/blob/main/json-schema-to-baml/parse_json_schema.py and modified to
    # make entries other than 'objects' optional, to allow for null values when LLMs do not provide a value for a field.
    def __init__(self, tb: TypeBuilder, schema: Dict[str, Any]):
        self.tb = tb
        self.schema = schema
        self._ref_cache = {}

    def _parse_object(self, json_schema: Dict[str, Any], title: str = None):
        assert json_schema["type"] == "object"
        if title is None:
            name = json_schema.get("title")
        else:
            name = title
        if name is None:
            raise ValueError("Title is required in JSON schema for object type")

        required_fields = json_schema.get("required", [])
        assert isinstance(required_fields, list)

        new_cls = self.tb.add_class(name)
        if properties := json_schema.get("properties"):
            assert isinstance(properties, dict)
            for field_name, field_schema in properties.items():
                assert isinstance(field_schema, dict)
                default_value = field_schema.get("default")
                field_type = self.parse(field_schema, title=field_name)
                if field_name not in required_fields:
                    if default_value is None:
                        field_type = field_type.optional()
                property = new_cls.add_property(field_name, field_type)
                if description := field_schema.get("description"):
                    assert isinstance(description, str)
                    if default_value is not None:
                        description = (
                            description.strip() + "\n" + f"Default: {default_value}"
                        )
                        description = description.strip()
                    if len(description) > 0:
                        property.description(description)
        print(type(new_cls), type(new_cls.type()))
        return new_cls.type()

    def _parse_string(self, json_schema: Dict[str, Any], title: str = None):
        assert json_schema["type"] == "string"
        if title is None:
            title = json_schema.get("title")

        if enum := json_schema.get("enum"):
            assert isinstance(enum, list)
            if title is None:
                # Treat as a union of literals
                return self.tb.union([self.tb.literal_string(value) for value in enum])
            new_enum = self.tb.add_enum(title)
            for value in enum:
                new_enum.add_value(value)
            return self.tb.union([new_enum.type(), self.tb.null()])
        return self.tb.string().optional()

    def _load_ref(self, ref: str):
        assert ref.startswith("#/"), f"Only local references are supported: {ref}"
        _, left, right = ref.split("/", 2)

        if ref not in self._ref_cache:
            if refs := self.schema.get(left):
                assert isinstance(refs, dict)
                if right not in refs:
                    raise ValueError(f"Reference {ref} not found in schema")
                self._ref_cache[ref] = self.parse(refs[right])
        return self._ref_cache[ref] 

    def parse(self, json_schema: Dict[str, Any], title: str = None):
        if any_of := json_schema.get("anyOf"):
            assert isinstance(any_of, list)
            return self.tb.union([self.parse(sub_schema) for sub_schema in any_of])

        if ref := json_schema.get("$ref"):
            assert isinstance(ref, str)
            return self._load_ref(ref)

        type_ = json_schema.get("type")
        if type_ is None:
            raise ValueError(f"Type is required in JSON schema: {json_schema}")
        parse_type = {
            "string": lambda: self._parse_string(json_schema, title=title),
            "number": lambda: self.tb.float(),
            "integer": lambda: self.tb.int(),
            "object": lambda: self._parse_object(json_schema, title=title),
            "array": lambda: self.parse(json_schema["items"]).list(),
            "boolean": lambda: self.tb.bool(),
            "null": lambda: self.tb.null(),
        }

        if type_ not in parse_type:
            raise ValueError(f"Unsupported type: {type_}")

        field_type = parse_type[type_]()

        return field_type


def parse_json_schema(json_schema: Dict[str, Any], tb: TypeBuilder):
    parser = SchemaAdder(tb, json_schema)
    return parser.parse(json_schema)


async def fill_form(message, json_schema, b: BamlAsyncClient) -> Dict[str, Any]:
    tb = TypeBuilder()
    res = parse_json_schema(json_schema, tb)
    tb.FilledForm.add_property("data", res)
    response = await b.FillForm(message, {"tb": tb})
    data = response.data  # type: ignore
    return data


async def stream_fill_form(message: str, json_schema: Dict[str, Any], b: BamlAsyncClient):
    tb = TypeBuilder()
    res = parse_json_schema(json_schema, tb)
    tb.FilledForm.add_property("data", res)
    stream = b.stream.FillForm(message, {"tb": tb})
    async for chunk in stream:
        yield (str(chunk.model_dump_json()) + "\n")
        await asyncio.sleep(
            0
        )
