#!/bin/bash
current_dir=$(dirname $(readlink -f $0))
wsgi_patch="${current_dir}/base_django_api/wsgi.py"
port=8000
echo "项目地址：${current_dir}"
echo "web服务绑定的端口：${port}"
pid_list=`lsof -i:${port} | grep -v PID | awk '{print $2}'`
if [ $# != 0 ]
then
    if [ $1 == "start" ]
    then
        if [ "$pid_list" ]
        then
            kill -9 ${pid_list}
        fi
        `uwsgi --chdir ${current_dir} --wsgi-file ${wsgi_patch} --socket 0.0.0.0:${port} uwsgi.ini`
        echo "web服务启动成功..."
        tail -f /dev/null
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
        echo "start：开启(or 重启)服务；stop：停止服务；show：显示详情；help：帮助信息"
    fi
else
    echo "参数错误，可以尝试命令：bash server.sh help"
fi
