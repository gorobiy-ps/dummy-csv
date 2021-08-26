from django.conf import settings
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from .models import *
import os
import random
import time
import hashlib


def login_required(view_func):
    def inner(request, *args, **kwargs):
        try:
            session = request.session.get('logged')
            if (session is None) or (session is not True):
                raise ValueError('User not logged')
        except KeyError as e:
            return redirect("login")
        except ValueError as e:
            return redirect("login")
        else:
            return view_func(request, *args, **kwargs)
    return inner


def check_pass(str_pass):
    hash_object = hashlib.sha1(str_pass.encode())
    return hash_object.hexdigest()


def get_prepeared_fields(post_data):
    list_of_fields = []
    names_of_columns = iter(post_data.getlist('column-name'))
    types_of_columns = iter(post_data.getlist('type'))
    orders = iter(post_data.getlist('order'))
    phone_masks = iter(post_data.getlist('phone-mask'))
    range_from = post_data.getlist('range-from')
    range_to = post_data.getlist('range-to')
    if range_from is not None:
        ranges_adj = adjust_ranges(range_from, range_to)
    else:
        ranges_adj = None
    extras = {'range': ranges_adj, 'mask': phone_masks}
    while True:
        range_data, mask = None, None
        try:
            name = next(names_of_columns)
            order = int(next(orders))
            field_type_obj = FieldType.objects.get(
                id=int(next(types_of_columns))
            )
            if field_type_obj.extra == 'mask':
                mask = next(extras['mask'])
            if field_type_obj.extra == 'range':
                range_data = next(extras['range'])
            list_of_fields.append({
                'name': name,
                'order': order,
                'field_type': field_type_obj,
                'mask': mask,
                'range': range_data
            })
        except StopIteration:
            break
    return list_of_fields


def get_schema_object(request):
    schema = Schema(
        name=request.POST.get('schema-name'),
        user=User.objects.get(id=request.session.get('uid')),
        separator=Separator.objects.get(id=request.POST.get('schema-separator')),
        text_char=TextChar.objects.get(id=request.POST.get('schema-character'))
    )
    return schema


def adjust_ranges(range_from, range_to):
    ranges_adj = []
    for i in range(len(range_from)):
        ranges_adj.append((
            int(range_from[i]),
            int(range_to[i])
            ))
    return iter(ranges_adj)


def create_dataset(schema_obj, rows):
    schema_name = schema_obj.name.strip().replace(' ', '_')
    timestamp = str(int(time.time()))
    filename = schema_name + '_' + str(rows) + '_' + timestamp + '.csv'
    dataset_obj = DataSet(
        status='pending',
        schema=schema_obj,
        link_to_file=filename
    )
    dataset_obj.save()
    return dataset_obj


def generate_data(schema, rows_quantity):
    data_lines = []
    line_generator = LineGenerator(schema)
    first_line = line_generator.get_headers()
    data_lines.append(first_line)
    for _ in range(rows_quantity):
        new_line = line_generator.get_line()
        data_lines.append(new_line)
    return data_lines


def save_csv_file(data_lines, dataset_obj):
    with default_storage.open(dataset_obj.link_to_file, 'w') as f:
        f.write('\n'.join(data_lines))
    return 'ready'


class LineGenerator:
    def __init__(self, schema):
        self.__schema = schema
        self.__fields = SchemaField.objects.filter(schema=schema).order_by('order')
        self.__sample_data = self.__get_sample_data()
        self.check = len(self.__sample_data)

    def get_line(self):
        data_line = self.__generate_data()
        return self.__schema.separator.value.join(data_line)

    def get_headers(self):
        column_headers = [field.name for field in self.__fields]
        return self.__schema.separator.value.join(column_headers)

    def __generate_data(self):
        data = []
        full_name = None
        if ('firstname' in self.__set_of_types) or ('domen' in self.__set_of_types):
            full_name = self.__choose_random_full_name()
        for field in self.__fields:
            if field.field_type.id == 1:
                data.append(full_name)
            if field.field_type.id == 2:
                data.append(self.__get_email(full_name))
            if field.field_type.id == 3:
                data.append(self.__get_phone(field.mask))
            if field.field_type.id == 4:
                rand_num = random.randint(field.range.lower, field.range.upper)
                data.append(str(rand_num))
            if field.field_type.id == 5:
                sentences_qty = random.randint(field.range.lower, field.range.upper)
                data.append(self.__get_text(sentences_qty))
        return data

    def __choose_random_full_name(self):
        firstnames = self.__sample_data.filter(type='firstname')
        lastnames = self.__sample_data.filter(type='lastname')
        f_name = random.choice(firstnames).text
        l_name = random.choice(lastnames).text
        return f_name + ' ' + l_name

    def __get_email(self, full_name):
        separate = full_name.split(' ')
        domens = self.__sample_data.filter(type='domen')
        domen = random.choice(domens).text
        lastname = separate[1].lower()
        firstname = separate[0][0:1].lower()
        return lastname + '.' + firstname + '@' + domen

    def __get_phone(self, mask):
        while '#' in mask:
            mask = mask.replace('#', str(random.randint(0, 9)), 1)
        return mask

    def __get_text(self, sentences_quantity):
        sentences_objs = list(self.__sample_data.filter(type='text'))
        random_items = random.sample(sentences_objs, sentences_quantity)
        sentences = [item.text for item in random_items]
        text = ' '.join(sentences)
        text_char = self.__schema.text_char.value
        return text_char + text + text_char

    def __get_sample_data(self):
        self.__set_of_types = self.__get_samples_types()
        return Sample.objects.filter(type__in=self.__set_of_types)

    def __get_samples_types(self):
        set_of_types = set()
        for field in self.__fields:
            if field.field_type.id == 1:
                set_of_types.update(['firstname', 'lastname'])
            if field.field_type.id == 2:
                set_of_types.update(['firstname', 'lastname', 'domen'])
            if field.field_type.id == 5:
                set_of_types.update(['text'])
        return set_of_types
