#!/bin/bash
current_dir=$(dirname $(readlink -f $0))
proj_name="base_django_api"
wsgi_patch="${current_dir}/${proj_name}/wsgi.py"
port=8000
pid_list=`lsof -i:${port} | grep -v PID | awk '{print $2}'`
if [ $# != 0 ]
then
    if [ $1 == "start" ]
    then
        echo "项目地址：${current_dir}"
        echo "web服务绑定的端口：${port}"
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
        # `uwsgi --chdir ${current_dir} --wsgi-file ${wsgi_patch} --socket 0.0.0.0:${port} uwsgi.ini`
        echo "web服务启动成功..."
        # tail -f /dev/null
    elif [ $1 == 'stop' ]
    then
        if [ "$pid_list" ]
        then
            kill -9 ${pid_list}
            echo "web服务停止成功..."
        else
            echo "web服务未启动，无需停止..."
        fi
    elif [ $1 == 'show' ]
    then
        if [ "$pid_list" ]
        then
            echo "web服务运行中..."
            echo "进程信息："
            pid=`lsof -i:${port}  | grep -v PID | head -1 | awk '{print $2}'` && if [ "${pid}" ];then ps -ef | grep ${pid} | grep -v grep;fi
            echo "监听的tcp："
            lsof -i:${port}
        else
            echo "web服务未启动..."
        fi
    else
        echo "start：开启(or 重启)服务，参数：[prod/dev uwsgi/uvicron/tornado]，第一个参数指定运行场景，第二个参数指定http服务器。"
        echo "stop：停止服务。"
        echo "show：显示详情。"
        echo "help：帮助信息。"
    fi
else
    echo "参数错误，可以尝试命令：bash server.sh help"
fi
