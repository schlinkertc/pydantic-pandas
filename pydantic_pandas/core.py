# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['TypedArray', 'ArrayMeta', 'Array', 'conarray', 'PandasDataFrame', 'DataFrameModelMetaclass', 'BaseFrame']

# Internal Cell

from pandas.core.frame import DataFrame
from pydantic import (
    validator,
    root_validator
)
from pydantic import BaseModel as PydanticBaseModel
from pydantic.main import ModelMetaclass
from .default_standard_lib import *
from .utils import delegates

# Cell

class TypedArray(pd.Series):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type

    @classmethod
    def __modify_schema__(cls,field_schema:Dict)->Dict:
        field_schema.update(
            type="<Pandas Series>"
        )

    @classmethod
    def validate_type(cls,val):
        print('validating array')
        print(val)
        return cls(val)

class ArrayMeta(type):
    def __getitem__(self,t):
        return type('Array', (TypedArray,), {'inner_type':t})

class Array(pd.Series,metaclass=ArrayMeta):
    pass

def conarray(*args,**kwargs) -> Type[TypedArray]:

    return type('ConstrainedArray',(TypedArray,), kwargs)

# Cell

class PandasDataFrame(DataFrame):
    """
    Pandas DataFrame Validation
    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            type='Pandas DataFrame'
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, pd.DataFrame):
            raise TypeError(f'Dataframe required. Got {type(v)} instead')
        if v.empty:
            raise ValueError("Dataframe can't be empty")
        return v
    def __init__(self,*args,**kwargs):
        print('making the pandas data frame')
        super(PandasDataFrame,self).__init__(*args,**kwargs)

# Internal Cell

DataFrameModelMetaclass = ForwardRef('DataFrameModelMetaclass')

def extract_ddf_from_model_fields(model:ModelMetaclass) -> 'PandasDataFrame':
    """Returns default df for DataFrameModelMetaclass ._repr_html_() method"""
    d={}
    for k,v in model.__fields__.items():
        d[k]=[v.required,v.type_]
    return pd.DataFrame(d,index=['required','type'])

# Cell

class DataFrameModelMetaclass(ModelMetaclass):
    def __new__(cls,name,bases,dct):
        print("in DF Meta __new__")
        print(name)
        print(bases)

        d = dct.get('__annotations__')
        if d:
            d = {k:conarray(v) for k,v in d.items()}
            dct['__annotations__']=d
        print(dct)
        model = ModelMetaclass.__new__(cls,name,bases,dct)
        model._default_df_ = extract_ddf_from_model_fields(model)

        return model
#     def __getitem__(self,t):
#         return type('Array', (TypedArray,), {'inner_type':t})

#     def _repr_json_(cls):

#         both_schemas = dict(
#             pandas_schema = json.loads(cls._default_df_.to_json()),
#             pydantic_schema = cls.schema()
#         )
#         return both_schemas

    def _repr_html_(cls):
        return cls._default_df_.to_html()

class BaseFrame(PydanticBaseModel,PandasDataFrame,metaclass=DataFrameModelMetaclass):
    """Doc from BaseFame"""
    def __init__(self,*args,**kwargs):
        print("base frame init")
        super(BaseFrame,self).__init__(**kwargs)
        super(PandasDataFrame,self).__init__(self.dict())

    @root_validator()
    def _base_frame_root_validator(cls,values):
        print('In Base Frame Root validator')
        return values
