import os
import json

from app.database import DATABASE_INSTANCES, InterfaceDataBase
from app.config import DATABASE

status = os.environ.get('APP_STATUS', 'stoped')

database = DATABASE_INSTANCES[0] if status == 'running' else InterfaceDataBase(db=DATABASE)

class BaseModel:

    def __init__(self, *args, **kwargs):
        self.properties = kwargs if kwargs is not None else {}
        for k, v in kwargs.items():
            self.__dict__[k] = v    
    
    def __setattr__(self, __name: str, __value: object) -> None:
        self.__dict__[__name] = __value
        self.__dict__['properties'][__name] = __value
        if '__class__' in self.properties:
            del self.properties['__class__']
        if 'properties' in self.properties:
            del self.properties['properties']
        
    def save(self, *args, **kwargs) -> object:
        table = self.__meta__.table
        if 'id' in self.__dict__:
            self.__update(*args, **kwargs)
        else:
            columns = ','.join(self.properties.keys())
            values = []
            for k, v in self.properties.items():
                if type(v) == str:
                    values.append('"'+ v +'"')
                else:
                    values.append(str(v))
            values = ','.join(values)
            sql = "insert into {table} ({columns}) values ({values})".format(table=table, columns=columns, values=values)        
            sql_result =  database.execute(sql)
            self.id = sql_result
            self.__save_references()
        return self
    
    def __update(self, *args, **kwargs):
        table = self.__meta__.table
        values = []
        for k, v in self.properties.items():
            field = "{}={}".format(k, v)
            if type(v) == str:
                field = "{}='{}'".format(k, v)
            values.append(field)
        values = ','.join(values)
        filtro = 'id = {}'.format(self.id)
        sql = "update {table} set {values} where {filtro}".format(table=table, values=values, filtro=filtro)        
        result = database.execute(sql)
        self.__update_references()
        return result

    def __save_references(self):
        table = self.__meta__.table
        sql = "pragma foreign_key_list('{}')".format(table)
        result = database.execute(sql)
        updated = []
        if result:
            for r in result:
                parent = r['table']
                parent_id_value = getattr(self, r['from'])
                sql = '''insert into 
                    back_refers (object, object_id, item, item_id) 
                    values ('{parent}',{parent_id_value},'{table}',{id})
                '''.format(parent=parent, parent_id_value=parent_id_value, table=table, id=self.id)
                updated.append(database.execute(sql))
        return True if len(updated) > 0 else False

    def __update_references(self):        
        table = self.__meta__.table
        updated_fields = []
        sql_pragma = "pragma foreign_key_list('{table}')".format(table=table)
        fg_list_result = database.execute(sql_pragma)
        if fg_list_result:
            for fg_item in fg_list_result:
                self_fg_key = fg_item['from']
                sql = "select * from back_refers where item = '{}' and  item_id = {}".format(table, self.id)
                parents = database.execute(sql)
                if parents:
                    for p in parents:                        
                        new_value_fg_key = getattr(self, self_fg_key)
                        if new_value_fg_key != p['object_id']:
                            sql_update = "update back_refers set object_id = {new_value} where id = {id}".format(new_value=new_value_fg_key, id=p['id'])
                            result = database.execute(sql_update)
                            updated_fields.append(result)
        return True if len(updated_fields) > 0 else False
    
    @classmethod
    def get(cls, *args, **kwargs) -> object:
        table = cls.__meta__.table
        params = []
        for k, v in kwargs.items():
            param = ''
            if type(v) == str:
                param = "{column}='{value}'"
            else:
                param = '{column}={value}'
            params.append(param.format(column=k, value=v))
        filtro = ' and '.join(params)
        sql = "select * from {table} where {filtro} limit 1".format(table=table, filtro=filtro)
        sql_result = database.execute(sql)
        if len(sql_result) > 0:
            objeto = cls(**sql_result[0])
            return objeto
        raise Exception('Registro nao encontrado')
    
    
    @classmethod
    def list(cls, *args, **kwargs) -> list:
        _list = []
        table = cls.__meta__.table
        limit = kwargs.get("limit", 10)
        filtro = []
        for k, v in kwargs.items():
            param = ''
            if type(v) == str:
                param = "{column} = '{value}'"
            else:
                param = "{column} = {value}"
            filtro.append(param.format(column=k, value=v))            
        filtro = ' and '.join(filtro)
        if len(kwargs) > 0:
            sql = "select * from {table} where {filtro} limit {limit}".format(table=table, limit=limit, filtro=filtro)
        else:
            sql = "select * from {table} limit {limit}".format(table=table, limit=limit)

        result = database.execute(sql)
        if len(result) > 0:
            for r in result:
                o = cls(**r)
                _list.append(o)
            return _list
        return []

    @property
    def parents(self) -> dict:
        table = self.__meta__.table
        parents = {}
        sql_pragma = "pragma foreign_key_list('{table}')".format(table=table)
        fg_list_result = database.execute(sql_pragma)
        if fg_list_result:
            for fg_item in fg_list_result:
                obj_related = fg_item['table'].capitalize()
                value = getattr(self, fg_item['from'])
                objeto = eval("{classe}.get(id={value})".format(classe=obj_related, value=value))
                parents[obj_related] = objeto
        return parents

    
    @property
    def children(self) -> dict:
        table = self.__meta__.table        
        items_related_to = {}
        sql = "select * from back_refers where object = '{table}' and object_id = {value}".format(table=table, value=self.id)
        result = database.execute(sql)
        for r in result:
            classe = r['item'].capitalize()
            objetos = eval('{classe}.list({pk}={value})'.format(classe=classe, pk='id', value=r['item_id']))
            items_related_to[classe] = objetos
        return items_related_to

    
    def to_json(self):
        raise NotImplementedError
    
    def to_dict(self):
        raise NotImplementedError


class Collection(BaseModel):
    items = []

    @staticmethod
    def append(item):
        Collection.items.append(item.to_json())
    
    @staticmethod
    def to_json():
        d = {'accounts':Collection.items}
        return json.dumps(d)
                

class Accounts(BaseModel):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)        
      
    def to_dict(self):
        return self.properties
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    class __meta__:
        table = 'accounts'

class Locations(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
    
    def to_dict(self):
        return self.properties
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    class __meta__:
        table = 'locations'

class Reviews(BaseModel):
    class __meta__:
        table = 'reviews'

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return self.properties

class Reviewer(BaseModel):
    class __meta__:
        table = 'reviewer'

    def to_dict(self):
        return self.properties

    def to_json(self):
        return json.dumps(self.to_dict())

class ReviewReply(BaseModel):
    class __meta__:
        table = 'review_reply'

    def to_dict(self):
        return self.properties

    def to_json(self):
        return json.dumps(self.to_dict())
        