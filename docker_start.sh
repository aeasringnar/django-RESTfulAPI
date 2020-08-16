#!/bin/bash
current_dir=$(dirname $(readlink -f $0))
proj_name="base_django_api"
wsgi_patch="${current_dir}/${proj_name}/wsgi.py"
if [ $1 ]
then
    port=$1
else
    port=8000
fi
echo "项目地址：${current_dir}"
echo "web服务绑定的端口：${port}"
pid_list=`lsof -i:${port} | grep -v PID | awk '{print $2}'`
if [ $# != 0 ]
then
    if [ "$pid_list" ]
    then
        kill -9 ${pid_list}
    fi
    if [ $2 ]
    then
        if [ $2 == "prod" ]
        then
            echo 'prod'
            `cp ${current_dir}/config/prod_settings.py ${current_dir}/${proj_name}/settings.py`
        else
            echo 'dev'
            `cp ${current_dir}/config/dev_settings.py ${current_dir}/${proj_name}/settings.py`
        fi
    else
        echo 'dev'
        `cp ${current_dir}/config/dev_settings.py ${current_dir}/${proj_name}/settings.py`
    fi
    if [ $3 ]
    then
        if [ $3 == "uwsgi" ]
        then
            echo 'choice uwsgi server'
            `uwsgi --chdir ${current_dir} --wsgi-file ${wsgi_patch} --socket 0.0.0.0:${port} uwsgi.ini`
        elif [ $3 == "uvicorn" ]
        then
            echo 'choice uvicron server'
            `nohup uvicorn ${proj_name}.asgi:application --host 0.0.0.0 --port ${port} > /dev/null 2>&1 &`
        elif [ $3 == "tornado" ]
        then
            echo 'choice tornado server'
            `nohup python3 -u tornado_server.py runserver 0.0.0.0:${port} > /dev/null 2>&1 &`
        else
            echo 'choice uvicorn server'
            `nohup uvicorn ${proj_name}.asgi:application --host 0.0.0.0 --port ${port} > /dev/null 2>&1 &`
        fi
    else
        echo 'choice uvicorn server'
        `nohup uvicorn ${proj_name}.asgi:application --host 0.0.0.0 --port ${port} > /dev/null 2>&1 &`
    fi
    echo "web服务启动成功..."
    tail -f /dev/null
else
    if [ "$pid_list" ]
    then
        kill -9 ${pid_list}
    fi
    echo 'dev'
    `cp ${current_dir}/config/dev_settings.py ${current_dir}/${proj_name}/settings.py`
    echo 'choice uvicron server'
    `nohup uvicorn ${proj_name}.asgi:application --host 0.0.0.0 --port ${port} > /dev/null 2>&1 &`
    echo "web服务启动成功..."
    tail -f /dev/null
fi