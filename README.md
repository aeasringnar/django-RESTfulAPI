# django-RESTfulAPI

基于 django 2.X的 RESTfulAPI 风格的项目模板，用于快速构建高性能的服务端。

## 技术栈

- **框架选择**：基于 django 2.X + django-rest-framework
- **数据模型**：基于 PyMySQL 存储，测试也可使用内置 sqlite3
- **授权验证**：基于 JWT
- **内置功能**：代码生成、文件处理、用户系统、异常处理、异步处理、接口返回格式化、日志格式化、分页、模糊查询、过滤、排序、缓存、导出等

## 快速入门

如需进一步了解，参见 [django 文档][https://docs.djangoproject.com/zh-hans/2.1/]。

### 本地开发

```bash
$ pip install -r requirements.txt
$ python manage.py ruserver
$ open http://localhost:8000/
```

### 部署

```bash
$ nohup python manage.py ruserver &
```
