from django_flow_forge.models import BatchHandler, PipelineBatch
from django.conf import settings

def get_pipeline_batches(total_batch_count, batch_ref_name=None, del_prev_batch_data=False, **kwargs):
    
    if settings.DEBUG and not batch_ref_name:
        print('Creating a batch in debug mode')
        batch_ref_name = 'DEBUG_MODE'

    if batch_ref_name:
        batch_handler, created = BatchHandler.objects.get_or_create(batch_ref_name=batch_ref_name)
        if del_prev_batch_data and not created:
            batch_handler.delete()
            batch_handler, created = BatchHandler.objects.get_or_create(batch_ref_name=batch_ref_name)

        batch_handler.total_batch_count = total_batch_count
        batch_handler.save(update_fields=['total_batch_count'])

    else:
        print('Creating a new batch handler')
        batch_handler = BatchHandler.objects.create(total_batch_count=total_batch_count)
        batch_handler.save()

    for batch_number in range(total_batch_count):
        batch = PipelineBatch.objects.get_or_create(batch_handler=batch_handler, pipeline_batch_number=batch_number)

    print(f'Created a BatchHandler with {total_batch_count} PipelineBatch objects')

    pipeline_batches = batch_handler.batch.all().order_by('pipeline_batch_number')

    return pipeline_batches