import json
import vk_api

from django.http import HttpResponse
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from apps.webimtest.graph import get_graph
from apps.webimtest.models import UserVK


class AuthenticateMixin(LoginRequiredMixin, View):
    """
        Миксин перенаправляющий неавторизованных
        пользователей на страницу авторизации
    """
    login_url = reverse_lazy('login')


class IndexAction(AuthenticateMixin, TemplateView):
    """
        Страница отобращениия всех данных
    """
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexAction, self).get_context_data(**kwargs)

        # Получение текущего пользователя
        user = self.request.user
        user = UserVK.objects.filter(user_ptr=user).first()

        # Вызов vk api для получения данных
        api = vk_api.VkApi(token=user.token, api_version='5.74').get_api()
        vk_profile = api.users.get(fields="photo_200_orig")[0]
        friends = api.friends.get(
            user_id=user.username,
            fields='first_name,last_name,bdate',
            order="random",
            count=10)['items']

        context["vk_profile"] = vk_profile
        context["friends"] = friends
        return context

    def post(self, request, *args, **kwargs):
        # Формирования социального графа
        if request.is_ajax():
            result = {}
            user = self.request.user
            user = UserVK.objects.filter(user_ptr=user).first()
            result["graph"] = get_graph(user.username, user.token)
            return HttpResponse(json.dumps(result))
