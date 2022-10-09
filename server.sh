#!/bin/bash
current_dir=$(pwd $(readlink -f $0))
proj_name="drfAPI"
wsgi_patch="${current_dir}/${proj_name}/wsgi.py"
port=8080
# 获取web服务进程
pid_list=`lsof -i:${port} | grep -v PID | awk '{print $2}'`
# 获取Celery worker进程
celery_list=`ps -ef | grep "${proj_name} worker" | grep -v grep | awk '{print $2}'`
# 获取Celery beat进程
beat_list=`ps -ef | grep "${proj_name} beat" | grep -v grep | awk '{print $2}'`
# 设置传参的默认值
arg1=${1:-help}
arg2=${2:-dev}
if [ $# != 0 ]
then
    if [ $arg1 == "start" ]
    then
        echo "项目地址：${current_dir}"
        echo "web服务绑定的端口：${port}"
        if [ $arg2 == "prod" ]
        then
            echo "启动生产环境..."
            export ENV="prod"
        else
            echo "启动开发环境..."
            export ENV="dev"
        fi
        if [ "$pid_list" ]
        then
            kill -9 ${pid_list}
            `rm -f ${current_dir}/logs/${proj_name}.log`
            `sleep 1`
        fi
        `uwsgi --chdir ${current_dir} --wsgi-file ${wsgi_patch} --socket 127.0.0.1:${port} uwsgi.ini`
        echo "web服务启动成功..."
        if [ "$celery_list" ]
        then
            kill -9 ${celery_list}
            `sleep 1`
        fi
        `nohup celery -A ${proj_name} worker -l info > ${current_dir}/logs/celery.log 2>&1 &`
        echo "celery服务启动成功..."
        if [ "$beat_list" ]
        then
            kill -9 ${beat_list}
            `sleep 1`
        fi
        `nohup celery -A ${proj_name} beat -l info > ${current_dir}/logs/beat.log 2>&1 &`
        echo "celery beat服务启动成功..."
        # tail -f /dev/null
    elif [ $arg1 == 'stop' ]
    then
        if [ "$pid_list" ]
        then
            kill -9 ${pid_list}
            `rm -f ${current_dir}/logs/${proj_name}.log`
            echo "web服务停止成功..."
        else
            echo "web服务未启动，无需停止..."
        fi
        if [ "$celery_list" ]
        then
            kill -9 ${celery_list}
            echo "celery服务停止成功..."
        else
            echo "celery服务未启动，无需停止..."
        fi
        if [ "$beat_list" ]
        then
            kill -9 ${beat_list}
            echo "celery beat服务停止成功..."
        else
            echo "celery beat服务未启动，无需停止..."
        fi
    elif [ $arg1 == 'show' ]
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
        if [ "$celery_list" ]
        then
            echo "celery服务运行中..."
            echo "进程信息："
            ps -ef | grep "${proj_name} worker" | grep -v grep
        else
            echo "celery服务未启动..."
        fi
        if [ "$beat_list" ]
        then
            echo "celery beat服务运行中..."
            echo "进程信息："
            ps -ef | grep beat | grep -v grep
        else
            echo "celery beat服务未启动..."
        fi
    else
        echo "start：开启(or 重启)服务。"
        echo "stop：停止服务。"
        echo "show：显示详情。"
        echo "help：帮助信息。"
    fi
else
    echo "参数错误，可以尝试命令：bash server.sh help"
fi