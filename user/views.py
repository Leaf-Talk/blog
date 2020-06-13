from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.db import DatabaseError
import re
from user.models import User
from django.contrib.auth import login, authenticate, logout


class RegisterView(View):
    ''' 注册 '''

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        # 验证数据
        # 参数是否齐全
        if not all([mobile, password, password2]):
            return HttpResponseBadRequest('缺少必要的参数')
        # 手机号的格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号不符合规则')
        #  密码是否符合格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位密码，密码是数字，字母')
        # 密码和确认密码要一致
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        # 3.保存注册信息
        # create_user 可以使用系统的方法来对密码进行加密
        try:
            user = User.objects.create_user(username=mobile,
                                            phone=mobile,
                                            password=password)
        except DatabaseError as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(e)
            return HttpResponseBadRequest('注册失败')

        login(request, user)
        # 返回响应跳转到指定页面
        response = redirect(reverse('home:index'))

        # 设置cookie信息，以方便首页中 用户信息展示的判断和用户信息的展示
        response.set_cookie('is_login', True)
        response.set_cookie('username', user.username, max_age=7 * 24 * 3600)

        return response


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        if not all([mobile, password]):
            return HttpResponseBadRequest('请填写账号和密码')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号码不符合规则')

        user = authenticate(username=mobile, password=password)

        response = redirect(reverse('home:index'))

        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')

        login(request, user)

        if remember != 'on':
            request.session.set_expiry(0)
            response.set_cookie('is_login', True)
            response.set_cookie('username', user.username, max_age=14*24*3600)
        else:
            request.session.set_expiry(None)
            response.set_cookie('is_login', True, max_age=14*24*3600)
            response.set_cookie('username', user.username, max_age=14*24*3600)

        return response


class LogoutView(View):
       # ##
    def get(self, request):
        # 1.session数据清除

        logout(request)
        # 2.删除部分cookie数据
        response=redirect(reverse('home:index'))
        response.delete_cookie('is_login')
        #3.跳转到首页
        return response

