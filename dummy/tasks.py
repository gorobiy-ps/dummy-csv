from .helper import *
from celery import shared_task


@shared_task
def generate_dummy_csv(schema_id, rows_quantity, dataset_id):
    schema = Schema.objects.get(id=schema_id)
    data_lines = generate_data(schema, rows_quantity)
    dataset_obj = DataSet.objects.get(id=dataset_id)
    status = save_csv_file(data_lines, dataset_obj)
    dataset_obj.status = status
    dataset_obj.save()
    return dataset_obj.id
