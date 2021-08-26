from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .helper import *
from .tasks import generate_dummy_csv
from celery import current_app


@login_required
def index(request):
    return redirect('my_schemes')


def login(request):
    if request.method == "GET":
        return render(request, 'dummy/login.html')
    if request.method == "POST":
        posted_username = request.POST.get('username')
        posted_password = request.POST.get('password')
        try:
            user = User.objects.get(name=posted_username)
            if user.password != check_pass(posted_password):
                raise User.DoesNotExist
            else:
                request.session.update({
                    'username': posted_username,
                    'logged': True,
                    'uid': user.id
                })
                request.session.save()
                return redirect("my_schemes")
        except User.DoesNotExist:
            data = {'title_class': 'text-danger', 'input_class': 'is-invalid'}
            return render(request, 'dummy/login.html', data)


def logout(request):
    request.session.update({'logged': False})
    request.session.save()
    return redirect('login')


@login_required
def my_schemes(request):
    list_of_schemes = Schema.objects.filter(user=request.session.get('uid'))
    data = {'schemes': list_of_schemes}
    return render(request, 'dummy/schemes_list.html', data)


@login_required
def new_schema(request):
    if request.method == "GET":
        data = {
            'separators_data': Separator.objects.all().order_by('id'),
            'text_chars_data': TextChar.objects.all().order_by('id'),
            'fields_type_data': FieldType.objects.all().order_by('id')
        }
        return render(request, 'dummy/new_schema.html', data)
    if request.method == "POST":
        schema = get_schema_object(request)
        fields = get_prepeared_fields(request.POST)
        schema.save()
        schemafields = []
        for field in fields:
            schemafields.append(SchemaField(schema_id=schema.id, **field))
        SchemaField.objects.bulk_create(schemafields)
        return redirect('my_schemes')


@login_required
def edit_schema(request, schema_id):
    try:
        schema = Schema.objects.get(id=schema_id)
    except Schema.DoesNotExist:
        return redirect('page_404')
    fields = SchemaField.objects.filter(schema=schema_id).order_by('order')
    if request.method == "GET":
        data = {
            'separators_data': Separator.objects.all().order_by('id'),
            'text_chars_data': TextChar.objects.all().order_by('id'),
            'fields_type_data': FieldType.objects.all().order_by('id'),
            'schema': schema,
            'fields': fields
        }
        return render(request, 'dummy/edit_schema.html', data)
    if request.method == "POST":
        # update existing schema
        schema.name = request.POST.get('schema-name')
        schema.separator_id = request.POST.get('schema-separator')
        schema.text_char_id = request.POST.get('schema-character')
        schema.save()
        # delete old set of fields for this schema
        SchemaField.objects.filter(schema_id=schema_id).delete()
        # insert new set of fields for this schema
        new_fields = get_prepeared_fields(request.POST)
        schemafields = []
        for field in new_fields:
            schemafields.append(SchemaField(schema_id=schema_id, **field))
        SchemaField.objects.bulk_create(schemafields)
        return redirect('my_schemes')


@login_required
def my_datasets(request):
    list_of_schemes = Schema.objects.filter(user=request.session.get('uid'))
    datasets = DataSet.objects.filter(schema__in=list_of_schemes).order_by('id')
    data = {'schemes': list_of_schemes, 'datasets': datasets}
    return render(request, 'dummy/generate.html', data)


@login_required
def download_file(request, f_name):
    with default_storage.open(f_name, 'rb') as fl:
        cont = fl.read()
    response = HttpResponse(cont, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename={}".format(f_name)
    return response


def page_404(request):
    response = HttpResponse('<h1>Error 404: Page not found. Сорян братан</h1>')
    response.status_code = 404
    return response


@login_required
def put_csv(request):
    if request.method == "GET":
        return redirect('my_datasets')
    if request.method == "POST":
        schema_id = request.POST.get('schema_id')
        rows_quantity = int(request.POST.get('rows_quantity'))
        try:
            schema_obj = Schema.objects.get(id=schema_id)
            dataset_obj = create_dataset(schema_obj, rows_quantity)
            task_obj = generate_dummy_csv.delay(
                schema_id,
                rows_quantity,
                dataset_obj.id
                )
            dataset_obj.task_id = task_obj.task_id
            dataset_obj.save()
            response = {'status': True, 'redirect': '/my_datasets'}
            return JsonResponse(response)
        except Schema.DoesNotExist:
            response = {
                'status': False,
                'message': 'This scheme no longer exists. Refresh page \
                and try again'
                }
            return JsonResponse(response)


@login_required
def check_task_status(request):
    if request.method == "POST" and request.is_ajax():
        task_id = request.POST.get('task_id')
        task_obj = current_app.AsyncResult(task_id)
        if task_obj.status == 'SUCCESS':
            dataset = DataSet.objects.get(task_id=task_id)
            response = {'status': True, 'link': dataset.link_to_file}
        else:
            response = {'status': False}
        return JsonResponse(response)


@login_required
def get_snippet(request):
    if request.method == "POST" and request.is_ajax():
        data_iden = request.POST.get('data_iden')
        snippet = request.POST.get('type')
        data = {'data_iden': data_iden}
        response = {
            'html': render_to_string(
                        f'dummy/snippets/snippet_{snippet}.html',
                        data
                        )
        }
        return JsonResponse(response)
    else:
        return redirect('my_schemes')
