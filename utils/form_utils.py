from django.utils.html import escape


def ajax_response(form, msgSuccess=None, msgError=None):
    """
        Return:
            {
                "result": "error",
                "message": "Form No Valid",
                "errors": [
                    {
                        "field": "name_field_1", "errors": [ "This field is required." ]
                    },
                    {
                        "field": "name_field_2", "errors": [ "This field is required." ]
                    }
                ]
            }
    """

    if not msgSuccess:
        msgSuccess = 'Form Valid'
    if not msgError:
        msgError = 'Form No Valid'

    is_valid = form.is_valid()
    errors = []
    data = []

    for field in form:
        if field.errors:
            errors.append({'field': field.html_name, \
                           'errors': map(lambda x: escape(x), field.errors)})
        if field.html_name in form.data:
            data.append({'name': field.html_name, \
                         'value': escape(form.data[field.html_name])})

    return {
    'result': 'success' if is_valid else 'error',
    'data': data,
    'message': msgSuccess if is_valid else msgError,
    'errors': errors
    }