from collections import defaultdict

from marshmallow import Schema, fields, validate, validates_schema, exceptions
import numpy as np


class Float64(fields.Number):
    """
    Define field to match up with numpy float64 type
    """

    num_type = np.float64


class Int8(fields.Number):
    """
    Define field to match up with numpy int8 type
    """

    num_type = np.int8


class Bool_(fields.Boolean):
    """
    Define field to match up with numpy bool_ type
    """

    num_type = np.bool_


class CompatibleDataSchema(Schema):
    """
    Schema for Compatible data object
    {
        "compatible_data": {"data1": bool, "data2": bool, ...}
    }
    """

    puf = fields.Boolean()
    cps = fields.Boolean()


class RangeSchema(Schema):
    """
    Schema for range object
    {
        "range": {"min": field, "max": field}
    }
    """

    _min = fields.Field(
        data_key="min", attribute="min"
    )  # fields.Float(attribute='min')
    _max = fields.Field(
        data_key="max", attribute="max"
    )  # fields.Float(attribute='max')


class EnsureList(fields.List):
    """
    Tax-Calculator col_label sometimes is a list and sometime is not. When it
    is not a list, it is an empty string. This field just makes sure it's a
    list
    """

    def _serialize(self, value, attr, obj):
        if not isinstance(value, list):
            value = list(value)
        return super()._serialize(value, attr, obj)

    def _deserialize(self, value, attr, data):
        if not isinstance(value, list):
            value = list(value)
        return super()._deserialize(value, attr, data)


class BaseParamSchema(Schema):
    """
    Defines a base parameter schema. This specifies the required fields and
    their types.
    {
        "long_name": str,
        "description": str,
        "notes": str,
        "type": str (limited to 'int', 'float', 'bool', 'str'),
        "number_dims": int,
        "value": `BaseValidatorSchema`, "value" type depends on "type" key,
        "range": range schema ({"min": ..., "max": ..., "other ops": ...}),
        "out_of_range_minmsg": str,
        "out_of_range_maxmsg": str,
        "out_of_range_action": str (limited to 'stop' or 'warn')
    }

    This class is defined further by a JSON file indicating extra fields that
    are required by the implementer of the schema.
    """

    long_name = fields.Str(required=True)
    description = fields.Str(required=True)
    notes = fields.Str(required=True)
    _type = fields.Str(
        required=True,
        validate=validate.OneOf(choices=["str", "float", "int", "bool"]),
        attribute="type",
        data_key="type",
    )
    number_dims = fields.Integer(required=True)
    value = fields.Field(required=True)  # will be specified later
    _range = fields.Nested(
        RangeSchema(), required=True, data_key="range", attribute="range"
    )
    out_of_range_minmsg = fields.Str(required=True)
    out_of_range_maxmsg = fields.Str(required=True)
    out_of_range_action = fields.Str(
        required=True, validate=validate.OneOf(choices=["stop", "warn"])
    )


class EmptySchema(Schema):
    """
    An empty schema that is used as a base class for creating other classes via
    the `type` function
    """

    pass


class BaseValidatorSchema(Schema):
    """
    Schema that validates parameter revisions such as:
    ```
    {
        "STD": [{
            "year": 2017,
            "MARS": "single",
            "value": "3000"
        }]
    }
    ```

    Information defined for each variable on the `BaseParamSchema` is utilized
    to define this class and how it should validate its data. See
    `build_schema.SchemaBuilder` for how parameters are defined onto this
    class.
    """

    @validates_schema
    def validate_params(self, data):
        """
        Loop over all parameters defined on this class. Validate them using
        the `self.validate_param_method`. Errors are stored until all
        parameters have been validated. Note that all data has been
        type-validated. These methods only do range validation.
        """
        errors = defaultdict(list)
        errors_exist = False
        for name, specs in data.items():
            for spec in specs:
                iserrors = self.validate_param(name, spec, data)
                if iserrors:
                    errors_exist = True
                    errors[name] += iserrors
        if errors_exist:
            raise exceptions.ValidationError(errors)

    def validate_param(self, param_name, param_spec, raw_data):
        """
        Do range validation for a parameter.
        """
        param_info = self.context["base_spec"][param_name]
        min_value = param_info["range"]["min"]
        min_value = self.resolve_op_value(
            min_value, param_name, param_spec, raw_data
        )
        max_value = param_info["range"]["max"]
        max_value = self.resolve_op_value(
            max_value, param_name, param_spec, raw_data
        )

        def comp(v, min_value, max_value):
            if v < min_value:
                return [f"{param_name} must be greater than {min_value}"]
            if v > max_value:
                return [f"{param_name} must be less than {max_value}"]
            return []

        value = param_spec["value"]
        errors = comp(value, min_value, max_value)
        return errors

    def resolve_op_value(self, op_value, param_name, param_spec, raw_data):
        """
        Operator values (`op_value`) are the values pointed to by the "min"
        and "max" keys. These can be values to compare against, another
        variable to compare against, or the default value of the revised
        variable.
        """
        if op_value in self.fields:
            return self.get_comparable_value(
                op_value, param_name, param_spec, raw_data
            )
        if op_value == "default":
            return self.get_comparable_value(
                param_name, param_name, param_spec, raw_data
            )
        return op_value

    def get_comparable_value(
        self, oth_param_name, param_name, param_spec, raw_data
    ):
        """
        Get the value that the revised variable will be compared against.

        TODO: if min/max point to another variable, first check whether that
        variable was specified in the revision.
        """
        oth_param = self.context["base_spec"][oth_param_name]
        vals = oth_param["value"]
        dims_to_check = tuple(k for k in param_spec if k != "value")
        iterres = filter(
            lambda item: all(item[k] == param_spec[k] for k in dims_to_check),
            vals,
        )
        res = list(iterres)
        assert len(res) == 1
        return res[0]["value"]


# A few fields that have not been instantiated yet
CLASS_FIELD_MAP = {
    "str": fields.Str,
    "int": fields.Integer,
    "float": fields.Float,
    "bool": fields.Boolean,
}


# A few fields that have been instantiated
FIELD_MAP = {
    "str": fields.Str(),
    "int": fields.Integer(),
    "float": fields.Float(),
    "bool": fields.Boolean(),
    "ensure_list": EnsureList(fields.Str()),
    "compatible_data": fields.Nested(CompatibleDataSchema()),
}


def get_param_schema(base_spec):
    """
    Read in data from the initializing schema. This will be used to fill in the
    optional parameters on classes derived from the `BaseParamSchema` class.
    This data is also used to build validators for schema for each parameter
    that will be set on the `BaseValidatorSchema` class
    """
    optional_fields = {}
    for k, v in base_spec["optional_params"].items():
        fieldtype = FIELD_MAP[v["type"]]
        if v["number_dims"] is not None:
            d = v["number_dims"]
            while d > 0:
                fieldtype = fields.List(fieldtype)
                d -= 1
        optional_fields[k] = fieldtype

    ParamSchema = type(
        "ParamSchema",
        (BaseParamSchema,),
        {k: v for k, v in optional_fields.items()},
    )
    dim_validators = {}
    for name, dim in base_spec["dims"].items():
        validator_cls = getattr(validate, dim["validator"]["name"])
        validator = validator_cls(**dim["validator"]["args"])
        fieldtype = CLASS_FIELD_MAP[dim["type"]]
        dim_validators[name] = fieldtype(validate=validator)
    return ParamSchema, dim_validators
