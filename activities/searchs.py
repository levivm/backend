import json
import re
from datetime import datetime
from django.conf import settings
from django.db.models import Q


from activities import constants


class ActivitySearchEngine(object):

    BLACKLIST = ('curso', 'cursos', 'taller', 'talleres', 'clase', 'clases', 'seminario', 'seminarios', 'certificacion',
                 'certificación', 'certificaciones', 'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las',
                 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es', 'lo', 'como', 'más', 'pero', 'sus', 'le',
                 'ya', 'o', 'fue', 'este', 'ha', 'sí', 'porque', 'esta', 'son', 'entre', 'está', 'cuando', 'muy', 'sin',
                 'sobre', 'ser', 'tiene', 'también', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado',
                 'desde', 'todo', 'nos', 'durante', 'estados', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'fueron',
                 'ese', 'eso', 'había', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo',
                 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual',
                 'sea', 'poco', 'ella', 'estar', 'haber', 'estas', 'estaba', 'estamos', 'algunas', 'algo', 'nosotros')

    SEARCH_ORDER_PRICE_ATTRIBUTE = 'closest_calendar_price'
    SEARCH_ORDER_MIN_PRICE_ATTRIBUTE = 'closest_calendar_price'
    SEARCH_ORDER_MAX_PRICE_ATTRIBUTE = '-closest_calendar_price'
    SEARCH_ORDER_SCORE_ATTRIBUTE = '-score'
    SEARCH_ORDER_SCORE_FREE_ATTRIBUTE = '-score_free'
    SEARCH_ORDER_CLOSEST_ATTRIBUTE = 'closest'
    SEARCH_ORDER_PRICE_SELECT = 'session_price'
    SEARCH_ORDER_CLOSEST_SELECT = 'initial_date'
    SEARCH_ORDER_SCORE_SELECT = 'score'

    def normalize_query(self, query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                        normspace=re.compile(r'\s{2,}').sub):
        if query_string:
            query = [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
            return list(set(query) - set(self.BLACKLIST))
        return list()

    def get_query(self, query_string, search_fields):
        query = None
        terms = self.normalize_query(query_string=query_string)
        for term in terms:
            or_query = None
            for field in search_fields:
                q = Q(**{'%s__unaccent__icontains' % field: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q

            if query is None:
                query = or_query
            else:
                query = query | or_query

        return query

    def extra_query(self, query_params, order):
        if order == constants.ORDER_CLOSEST:
            extra_parameter = self.SEARCH_ORDER_CLOSEST_ATTRIBUTE
            select_parameter = self.SEARCH_ORDER_CLOSEST_SELECT
        elif order == constants.ORDER_MIN_PRICE:
            extra_parameter = self.SEARCH_ORDER_PRICE_ATTRIBUTE
            select_parameter = self.SEARCH_ORDER_PRICE_SELECT
        elif order == constants.ORDER_MAX_PRICE:
            extra_parameter = self.SEARCH_ORDER_PRICE_ATTRIBUTE
            select_parameter = self.SEARCH_ORDER_PRICE_SELECT

        is_free = query_params.get('is_free', False)
        cost_end = query_params.get('cost_end')
        cost_start = query_params.get('cost_start')
        js_timestamp = query_params.get('date')
        timestamp = int(js_timestamp) // 1000 if js_timestamp else datetime.now().timestamp()
        date = datetime.fromtimestamp(timestamp).replace(second=0).strftime('%Y-%m-%d')
        if is_free:
            if order == self.SEARCH_ORDER_SCORE_SELECT:
                extra_parameter = self.SEARCH_ORDER_SCORE_FREE_ATTRIBUTE
                select_parameter = self.SEARCH_ORDER_SCORE_SELECT
            else:
                extra_parameter = self.SEARCH_ORDER_CLOSEST_ATTRIBUTE
                select_parameter = self.SEARCH_ORDER_CLOSEST_SELECT
            extra = {
                extra_parameter:
                    'SELECT "activities_calendar".' + select_parameter + ' '
                    'FROM "activities_calendar" '
                    'WHERE "activities_calendar"."activity_id" = "activities_activity"."id" '
                    'AND "activities_calendar"."initial_date" >= %s '
                    'AND "activities_calendar"."is_free" = TRUE '
                    'AND "activities_calendar"."available_capacity" > 0 '
                    'ORDER BY "activities_calendar"."initial_date" ASC LIMIT 1'
            }
            params = (date, cost_start)
            return {'select': extra, 'select_params': params}

        elif cost_start is not None and cost_end is not None:
            without_limit = True if int(cost_end) == settings.PRICE_RANGE.get('max') else False
            if without_limit:
                extra = {
                    extra_parameter:
                        'SELECT "activities_calendar".'+select_parameter+' '
                        'FROM "activities_calendar" '
                        'WHERE "activities_calendar"."activity_id" = "activities_activity"."id" '
                        'AND "activities_calendar"."initial_date" >= %s'
                        'AND "activities_calendar"."session_price" >= %s '
                        'AND "activities_calendar"."available_capacity" > 0'
                        'ORDER BY "activities_calendar"."initial_date" ASC LIMIT 1'
                }
                params = (date, cost_start)
            else:
                extra = {
                    extra_parameter:
                        'SELECT "activities_calendar".'+select_parameter+' '
                        'FROM "activities_calendar" '
                        'WHERE "activities_calendar"."activity_id" = "activities_activity"."id" '
                        'AND "activities_calendar"."initial_date" >= %s'
                        'AND "activities_calendar"."session_price" >= %s '
                        'AND "activities_calendar"."session_price" <= %s '
                        'AND "activities_calendar"."available_capacity" > 0'
                        'ORDER BY "activities_calendar"."initial_date" ASC LIMIT 1'
                }
                params = (date, cost_start, cost_end)

            return {'select':extra, 'select_params': params}


    def filter_query(self, query_params):
        subcategory = query_params.get('subcategory')
        category = query_params.get('category')
        date = query_params.get('date')
        city = query_params.get('city')
        cost_start = query_params.get('cost_start')
        cost_end = query_params.get('cost_end')
        level = query_params.get('level')
        certification = query_params.get('certification')
        weekends = query_params.get('weekends')
        is_free = query_params.get('is_free')

        query = Q(sub_category=subcategory) if subcategory else None
        if query is None:
            query = Q(sub_category__category=category) if category else None
        if query is not None:
            query = query & Q(published=True)
        else:
            query = Q(published=True)

        if date is not None:
            date = datetime.fromtimestamp(int(date) // 1000).replace(second=0)
            query = query & Q(calendars__initial_date__gte=date)

        if city is not None:
            query &= Q(location__city=city)

        if cost_start is not None and cost_end is not None and is_free is None:
            without_limit = True if int(cost_end) == settings.PRICE_RANGE.get('max') else False
            if without_limit:
                query &= Q(calendars__session_price__gte=(cost_start))
            else:
                query &= Q(calendars__session_price__range=(cost_start, cost_end))

        if level is not None and not level == constants.LEVEL_N:
            query &= Q(level=level)

        if bool(certification):
            query &= Q(certification=json.loads(certification))

        if bool(weekends) and json.loads(weekends):
            query &= Q(calendars__is_weekend=True)

        if bool(is_free):
            query &= Q(calendars__is_free=True)

        return query

    def get_order(self, order_param):
        if order_param == constants.ORDER_MIN_PRICE:
            order = [self.SEARCH_ORDER_MIN_PRICE_ATTRIBUTE]
        elif order_param == constants.ORDER_MAX_PRICE:
            order = [self.SEARCH_ORDER_MAX_PRICE_ATTRIBUTE]
        elif order_param == constants.ORDER_SCORE:
            order = [self.SEARCH_ORDER_SCORE_ATTRIBUTE]
        elif order_param == constants.ORDER_CLOSEST:
            order = [self.SEARCH_ORDER_CLOSEST_ATTRIBUTE]
        else:
            order = [self.SEARCH_ORDER_SCORE_ATTRIBUTE]

        return order