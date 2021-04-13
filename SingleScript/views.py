from django.shortcuts import render
from .RosAPI3 import Core
import os
from datetime import datetime, timedelta

# Create your views here.

def check_host(host):
    response = os.system('ping -c 1 -W 1 ' + host) #.decode('UTF-8')
    if response == 0:
        return True
    else:
        return False

def run_script(ip, inUser='', inPass='', commandos=''):
    if inUser == '':
        inUser='admin'
        inPass=''
    if check_host(ip):
        try:
            tik = Core(ip, DEBUG=False)
            tik.login(inUser, inPass)
            API_zapros = tik.response_handler(tik.talk(["/system/scheduler/print", "?name=ch_fr_script",]))
            for API_result in API_zapros:
                if API_result[".id"]:
                    tik.response_handler(tik.talk(["/system/scheduler/remove", "=.id=" + API_result[".id"],]))
            API_zapros = tik.response_handler(tik.talk(["/system/clock/print", ]))
            for API_result in API_zapros:
                my_on_time = datetime.strptime("{} {}".format(API_result["date"],API_result["time"]), "%b/%d/%Y %H:%M:%S") + timedelta(seconds=2)
            tik.response_handler(tik.talk(["/system/scheduler/add", "=interval=0s",
                    "=start-date=" + my_on_time.strftime("%b/%d/%Y"), "=start-time=" + my_on_time.strftime("%H:%M:%S"),
                    "=name=ch_fr_script", "=on-event=" + " /system scheduler remove [ find name=ch_fr_script ];" + commandos]))
        except:
            return False
        else:
            return True
    else:
        return False

def mainform(request):
    #if request.user.is_authenticated:
    #    full_name = request.user.get_full_name()
    #else:
    #    return HttpResponseRedirect(reverse('logins', args=[]))
    error_message = ''
    my_result = ''

    if request.method == 'POST':
        login = request.POST['login']
        password = request.POST['pass']
        adresses = request.POST['ips']
        commands = request.POST['commands']
        for i in adresses.split('\r'):
            if not i == '\n':
                #my_result = my_result + '{}-OK'.format(i)
                if run_script(i, login, password, commands):
                    my_result = my_result + '{}-Ok'.format(i)
                else:
                    my_result = my_result + '{}-Error'.format(i)
            # else:
            #     my_result = my_result + '\nPusto'

    return render(request, 'main.html', { 'error_message': error_message, 'result': my_result})

def new_list(request):
    my_result = ''
    login = request.GET['login']
    password = request.GET['pass']
    adresses = request.GET['ips']
    commands = request.GET['commands']
    for i in adresses.split('\n'):
        # print("!!!!{}".format(i))
        if i.strip():
            if run_script(i, login, password, commands):
                my_result = my_result + '{}-Ok\n'.format(i)
            else:
                my_result = my_result + '{}-Error\n'.format(i)
    return render(request, 'new_list.html', {'result': my_result})