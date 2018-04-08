import json
import hashlib
import requests

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic.base import View, TemplateView
from django.contrib.auth import logout
from django.contrib import messages

from apps.webimtest.models import UserVK
from webimproject.settings import APP_ID, SECURE_KEY, DOMIAN


class LogoutAction(View):
    """
        Разлогиниться
    """
    def get(self, request):
        logout(request)
        messages.add_message(
            request,
            messages.SUCCESS,
            "Пользователь разлогинился"
        )
        return redirect(reverse_lazy("index"))


class LoginAction(TemplateView):
    """
        Страница с авторизацией
    """
    template_name = "login.html"


class VKAuthAction(View):
    """
        Авторизация
    """

    def get(self, request):
        auth_url = (
            "https://oauth.vk.com/authorize?client_id={app_id}"
            "&scope=offline,email"
            "&redirect_uri={domian}/auth/vk/login/callback/"
            "&response_type=code&v=5.74".format(app_id=APP_ID, domian=DOMIAN)
        )
        return redirect(auth_url)


class VKCallBack(View):
    """
        CallBack - получаем токен от VK
        И сохраняем результат
    """

    def get(self, request):

        # Запрашиваем токен и почту, для дальнейшего использования
        auth_url = (
                "https://oauth.vk.com/access_token?client_id={app_id}"
                "&client_secret={secure_key}"
                "&code={code}"
                "&redirect_uri={domian}/auth/vk/login/callback/".format(
                    app_id=APP_ID,
                    secure_key=SECURE_KEY,
                    code=request.GET["code"],
                    domian=DOMIAN)
            )

        response = requests.get(auth_url)
        data = json.loads(response.text)
        uid = data["user_id"]
        email = data.get("email", "")
        token = data["access_token"]

        password = hashlib.md5(
            '{app_id}{user_id}{secure_key}'.format(
                app_id=APP_ID, user_id=uid, secure_key=SECURE_KEY
            ).encode()).hexdigest()

        # Сохраняем или получаем пользователя
        user, created = UserVK.objects.get_or_create(
            username=uid,
            password=password,
            defaults={"token": token, "email": email}
        )

        # Авторизуем
        login(self.request, user)

        messages.add_message(
            request,
            messages.SUCCESS,
            "Пользователь {uid} авторизован".format(uid=uid)
        )

        return redirect(reverse_lazy("index"))
