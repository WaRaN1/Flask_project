import logging
import requests
import base64
import json
import sys
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from arbitrage import settings
from .authentication import BearerTokenAuthentication
from .forms import TaskForm
from .helpers import UrlBuilder, UrlBuilderRepeated, formation_payload_for_workers, request_for_worckers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Task

logger = logging.getLogger(__name__)


def send_post_request(url, payload):
    requests.post(url, json=payload)


class API(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'error': 'Method not allowed'}, status=405)

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if not token or token != f'Bearer {settings.AUTHORIZATION_TOKEN}':
            return Response({'error': 'Unauthorized'}, status=401)
        statistics = {'mp4', 'no_ads', 'errors', 'task_id', 'work_time'}
        if statistics.issubset(request.data):
            mp4 = request.data.get('mp4')
            no_ads = request.data.get('no_ads')
            errors = request.data.get('errors')
            task_id = request.data.get('task_id')
            work_time = request.data.get('work_time')
            task = get_object_or_404(Task, id=task_id)

            task.statistics = {'mp4': mp4 + task.statistics["mp4"], 'no_ads': no_ads + task.statistics["no_ads"],
                               'errors': errors + task.statistics["errors"],
                               'work_time': work_time + task.statistics["work_time"]}
            task.step_in_pull += 1
            task.save()
            url_data_objects_repeated = UrlBuilderRepeated(task)
            url_list, time_limit, unused_uip_sufficient = url_data_objects_repeated.build_urls()
            if unused_uip_sufficient:
                print('PAYLOAD GENERATION STARTED')
                json_data = json.dumps(url_list)
                encoded_url_list = base64.b64encode(json_data.encode()).decode()
                payload = {'url_list': encoded_url_list, 'time_limit': time_limit, 'task_id': task.id}
                print('REQUEST SENDING')
                response = requests.post('http://45.61.129.118', json=payload)
                print(response)
                print('REQUEST SEND')
            else:
                pass
            return Response({'status': 'success'})
        return Response({'error': 'Invalid request'}, status=400)


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            url_data_objects = UrlBuilder(form)
            url_list, time_limit = url_data_objects.build_urls()
            print('url_list = ', url_list)

            all_list_payload = formation_payload_for_workers(task, url_list, time_limit)

            # json_data = json.dumps(url_list)
            # encoded_url_list = base64.b64encode(json_data.encode()).decode()
            # payload = {'url_list': encoded_url_list, 'time_limit': time_limit, 'task_id': task.id}

            # print(len(payload))
            # print('Size of payload:', sys.getsizeof(payload), 'bytes')
            # print('REQUEST SENDING')

            response = request_for_worckers(all_list_payload)

            # response = requests.post('http://45.61.129.118', json=payload)

            print(response)
            print('REQUEST SENDED')
            return redirect('admin:index')
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})
