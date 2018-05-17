import time


class LoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()

        response = self.get_response(request)

        self.print_log(request, response)

        return response

    def print_log(self, request, response):
        ip = request.META['REMOTE_ADDR']
        try:
            person = "{:06}".format(int(request.logged_person_id))
        except (AttributeError, TypeError):
            person = 'anonym'
        code = response.status_code
        total_time = int(round((time.time() - request.start_time) * 1000))
        client = request.META.get('HTTP_USER_AGENT')
        path = "{} {}".format(request.method, request.get_full_path())

        log = 'ip={}\tperson={}\tclient={}\tcode={}\tpath="{}"\ttime={}ms' \
              .format(ip, person, client, code, path, total_time)

        if not request.META['SERVER_NAME'] == 'testserver':
            print(log)
