import os
# 自动生成代码，将表内容按照格式放入，使用Python脚本运行即可
# 存放模型以及表名
# 示例：model_list = [{'name':'Group','verbose':'用户组表'},{'name':'User','verbose':'用户表'}]
model_list = []

try:
    for data in model_list:
        print(data)
        name = data.get('name')
        verbose = data.get('verbose')

        # 序列化器
        MySerializer = """

# {verbose} 序列化器
class {name}Serializer(serializers.ModelSerializer):
    updated = SerializerMethodField()
    created = SerializerMethodField()
    class Meta:
        model = {name}
        # fields = ('id','sort','updated','created')
        fields = '__all__'
    def get_updated(self,obj):
        if obj.updated:
            return time.strftime('%Y-%m-%d %H:%M',time.strptime(str(obj.updated),'%Y-%m-%d %H:%M:%S.%f'))
        else:
            return ''
    def get_created(self,obj):
        if obj.created:
            return time.strftime('%Y-%m-%d %H:%M',time.strptime(str(obj.created),'%Y-%m-%d %H:%M:%S.%f'))
        else:
            return ''
        """.format(name=name, verbose=verbose)

        MyViewSet = """
class {name}ViewSet(viewsets.ModelViewSet):
    serializer_class = {name}Serializer
    queryset = {name}.objects.all()""".format(name=name, verbose=verbose)

        # API视图
        MyApiView = """

# {verbose} 视图
class {name}View(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    serializer_class = {name}Serializer
    def get(self,request):
        '''
        获取{verbose}接口
        无需登录便可访问
        参数：
        id 传入id返回该条详细数据；否则返回全部数据
        page 页码
        page_size 每页数据量
        '''
        
        try:
            json_data = {{"message": "ok", "errorCode": 0, "data": {{}}}}
            id = request.GET.get('id')
            print('是否存在ID',id)
            if not id:
                my_queryset = {name}.objects.all().order_by('sort','-created')
                pagination_clas = SchoolShopPagination()
                page_list = pagination_clas.paginate_queryset(queryset=my_queryset,request=request,view=self)
                serializer = {name}Serializer(instance=page_list, many=True)
                json_data['data'] = serializer.data
                json_data['tatol'] = len(my_queryset)
            else:
                my_queryset = {name}.objects.filter(id=id).first()
                serializer = {name}Serializer(instance=my_queryset)
                json_data['data'] = serializer.data
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({{"message": "网络错误", "errorCode": 1, "data": {{}}}})
    def post(self,request):
        '''
        新增{verbose}接口
        需要登录才可访问
        参数：
        如接口示或联系后端人员
        '''
        
        try:
            if not request.auth:
                return Response({{"message": "请先登录", "errorCode": 2, "data": {{}}}})
            json_data = {{"message": "ok", "errorCode": 0, "data": {{}}}}
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({{"message": str(serializer.errors), "errorCode": 4, "data": {{}}}})
            serializer.save()
            json_data['data'] = serializer.data
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({{"message": "网络错误", "errorCode": 1, "data": {{}}}})
    def patch(self,request):
        '''
        修改{verbose}接口
        需要登录才可访问
        参数：
        如接口示或联系后端人员
        '''
        
        try:
            if not request.auth:
                return Response({{"message": "请先登录", "errorCode": 2, "data": {{}}}})
            json_data = {{"message": "ok", "errorCode": 0, "data": {{}}}}
            id = request.data.get('id')
            if not id:
                return Response({{"message": "id为必要字段", "errorCode": 2, "data": {{}}}})
            item = {name}.objects.filter(id=id).first()
            if not item:
                return Response({{"message": "数据不存在或已经被删除", "errorCode": 2, "data": {{}}}})
            serializer = self.get_serializer(item,data=request.data)
            if not serializer.is_valid():
                return Response({{"message": str(serializer.errors), "errorCode": 4, "data": {{}}}})
            serializer.save()
            json_data['data'] = serializer.data
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({{"message": "网络错误", "errorCode": 1, "data": {{}}}})
    def delete(self,request):
        '''
        删除{verbose}接口
        需要登录才可以访问
        参数：
        如接口示或联系后端人员
        '''
        
        try:
            if not request.auth:
                return Response({{"message": "请先登录", "errorCode": 2, "data": {{}}}})
            json_data = {{"message": "ok", "errorCode": 0, "data": {{}}}}
            id = request.data.get('id')
            if not id:
                return Response({{"message": "id为必要字段", "errorCode": 2, "data": {{}}}})
            item = {name}.objects.filter(id=id).first()
            if not item:
                return Response({{"message": "数据不存在或已经被删除", "errorCode": 2, "data": {{}}}})
            item.delete()
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({{"message": "网络错误", "errorCode": 1, "data": {{}}}})
        """.format(name=name, verbose=verbose)

        def underscore(str):
            return "".join(map(lambda x: "_" + x if x.isupper()  else x, str))[1:].lower()

        # 路由
        MyUrl = """# path(r'{lower}',views.{name}View.as_view(),name='{lower}'),""".format(name=name, verbose=verbose,lower=underscore(name))
        
        # 开始自动生成代码
        # 生成 serializers 序列化器 'serializers.py'
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'serializers.py'),'a') as f:
            f.write(MySerializer)
        # 生成 view 视图
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'views.py'),'a') as f:
            f.write(MyApiView)
        # 生成 path 路由
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'urls.py'),'a') as f:
            f.write(MyUrl)
        print("%s生成完毕！"%name)
except Exception as e:
    print(e)
    print("代码生成过程出错...")