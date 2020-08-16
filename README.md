# django-RESTfulAPI

基于 django 3.X 的 RESTfulAPI 风格的项目模板，用于快速构建高性能的服务端。

## 技术栈

- **框架选择**：基于 django 3.X + django-rest-framework
- **数据模型**：基于 MySQLClient 存储，测试也可使用内置 sqlite3
- **授权验证**：基于 JWT
- **内置功能**：代码生成、文件处理、用户系统、异常处理、异步处理、全文检索、动态权限、接口返回格式化、日志格式化、分页、模糊查询、过滤、排序、缓存、导出、微信&支付宝支付等

## 快速入门

如需进一步了解，参见 [django 文档](https://docs.djangoproject.com/zh-hans/3.0/)。

### 本地开发

```bash
$ pip install -r requirements.txt
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py loaddata apps/user/user.json
$ python manage.py ruserver
$ open http://localhost:8000/
```

### 线上部署

```bash
bash server.sh start  # 获取帮助：bash sever.sh help 默认启动端口为 8001
```