from __future__ import absolute_import

from allauth.account.adapter import get_adapter
from celery import Task
from .models import EmailTaskRecord




class SendEmailTaskMixin(Task):
    abstract = True
    success_handler = True


    def run(self, instance, template, **kwargs):
        emails = self.get_emails_to(instance)
        

        if emails:
            context = self.get_context_data(kwargs)

            for email in emails:
                self.register_email_record_task(template,self.request.id,email,**kwargs)
                get_adapter().send_mail(
                    template,
                    email,
                    context,
                )

            return 'Task scheduled'

    def get_email_record_task_data(self,template,task_id,to_email,**kwargs):

        d = {
            'to':to_email,
            'template':template,
            'data': self.get_context_data(kwargs),
            'task_id':task_id,
        }


        return d


    def register_email_record_task(self,template,task_id,to_email,**kwargs):
        data = self.get_email_record_task_data(template,task_id,to_email,**kwargs)
        email_task_record = EmailTaskRecord(**data)
        email_task_record.save()

    def get_context_data(self,instance):
        data = {}
        return data

    def get_emails_to(self, instance):
        return []

    def on_success(self, retval, task_id, args, kwargs):

        if self.success_handler:
            email_task_record = EmailTaskRecord.objects.get(task_id=task_id)
            email_task_record.send = True
            email_task_record.save()

# class SendEmailTaskMixin(Task):
#     abstract = True
#     success_handler = True

#     def create_email_record_task(self,template,data):
#         data ={
#             'to':data.get('email'),
#             'template':template,
#             'data':data,
#         }
#         email_task_record = EmailTaskRecord(**data)
#         return email_task_record




#     def run(self, instance, template, **kwargs):
#         emails = self.get_emails_to(instance)
        

#         if emails:

#             context = self.get_context_data(instance)
#             self.create_email_record_task(template,kwargs['context'])

#             # if not instance:
#             #     data = kwargs['context']
#             #     email_task_record = EmailTaskRecord(**data)
#             #     context = self.get_context_data(kwargs['context'])
#             #     for email in emails:
#             #         get_adapter().send_mail(
#             #             template,
#             #             email,
#             #             context,
#             #         )


#             #     return 'Task scheduled'

#             # for celery_task in instance.tasks.all():
#             #     task = self.AsyncResult(celery_task.task_id)
#             #     if task.state == 'PENDING':
#             #         break
#             # else:
           
#             for email in emails:
#                 get_adapter().send_mail(
#                     template,
#                     email,
#                     context,
#                 )
            
#             self.register_task(instance)

#                 return 'Task scheduled'