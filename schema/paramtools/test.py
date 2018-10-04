import os

import pytest

from marshmallow import exceptions

from paramtools.build_schema import SchemaBuilder

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture
def reform():
    return {
        "_cpi_offset": [{"year": "2015", "value": 0.0025},
                        {"year": "2017", "value": 0.0025}],
        "_STD": [{"year": 2018, "MARS": "separate", "value": 12001.00}],
        "_II_em": [{"year": 2020, "value": 5000}],
        "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37649.00}]
    }

@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, 'base.json')


@pytest.fixture
def base_spec_path():
    return os.path.join(CURRENT_PATH, '../clp2.json')


def test_load_schema(reform, schema_def_path, base_spec_path):
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()

    with open(base_spec_path, 'r') as f:
        res = sb.param_schema.loads(f.read())
    res = sb.load_params(reform)


def test_schema_with_errors(reform, schema_def_path, base_spec_path):
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()

    a = reform.copy()
    a["_cpi_offset"][0]['year'] = 2000
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(a)

    b = reform.copy()
    b["_STD"][0]['MARS'] = "notastatus"
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(b)

    c = reform.copy()
    c["_II_brk1"][0]['value'] = "abc"
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(c)

    c = reform.copy()
    c["_II_em"][0]['value'] = [4000.0]
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(c)


def test_range_validation(schema_def_path, base_spec_path):
    reform = {
        "_II_em": [{"year": 2020, "value": 5000}]
    }
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    # parse baseline parameters to specified formats and store in
    # validator_schema context
    base_spec = sb.param_schema.load(sb.base_spec)
    sb.validator_schema.context['base_spec'] = base_spec
    sb.load_params(reform)


def test_range_validation_fail(schema_def_path, base_spec_path):
    reform = {
        "_II_em": [{"year": 2020, "value": -1}]
    }
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(reform)
    print(excinfo)


def test_range_validation_on_named_variable(schema_def_path, base_spec_path):
    reform = {
        "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37649.00}]
    }
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    sb.load_params(reform)


def test_range_validation_on_named_variable_fails(schema_def_path,
                                                  base_spec_path):
    reform = {
        "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37651.00}]
    }
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(reform)
    print(excinfo)


def test_range_validation_on_default_variable(schema_def_path, base_spec_path):
    reform = {
        "_STD": [{"year": 2018, "MARS": "separate", "value": 12001.00}]
    }
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    sb.load_params(reform)


def test_range_validation_on_default_variable_fails(schema_def_path,
                                                  base_spec_path):
    reform = {
        "_STD": [{"year": 2018, "MARS": "separate", "value": 11999.00}]
    }
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    with pytest.raises(exceptions.ValidationError) as excinfo:
        sb.load_params(reform)
    print(excinfo)