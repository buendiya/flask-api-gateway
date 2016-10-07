# flask-api-gateway
Api Gateway Built With Flask

用Flask实现的一个简单的API Gateway


## 已实现功能

### 加密签名

会为每个 User 分配一对 access_key 和 sercret_key, 用于计算签名。

### 流量控制

可以设置 User 对某个 API 的流量控制, 也可以对 API 单独设置流量控制。

### 防御重放攻击

可以通过设置 SIGNATURE_EXPIRE_SECONDS 来控制签名的过期时间，只有在这个时间内的请求才能访问成功。


## 路由规则说明

Gateway对外暴露的 url 和要路由到的 url 是一一对应的关系，两个都需要显式声明，这个可以在route表里配置


## 表结构说明

共有3张表，分表是user, route, user_route；表结构见schema.sql, 表内容示例见load_sample.py。

### user表

用于存储 access_key 和 secret_key 

### route表

配置路由规则。path 用于配置 Gateway path, url 用于配置要路由到的地址, seconds 和 limits 用于配置该时间范围内允许的请求数。

### user_route表

对每个user, 配置其对每个API的流量控制。


## 环境及依赖

测试的 Python 版本: 2.7

使用Redis 和 SQLite 3，相应的依赖包可以通过以下命令安装:

    pip install -r requirement.txt


## 运行

配置项可以写在settings.py里配置，也可以写在和settings.py同目录下的 CONFIGS.py 里；

```py
# 访问签名的有效时间, 秒
SIGNATURE_EXPIRE_SECONDS = 3600

# Redis 配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = 'your_password'

```

创建数据库

	python init_db.py

运行

    python run.py


## 其他

test/api_client.py 里的 APIRequest, 可用于发送包含签名的请求。


## 参考

- [Beluga](https://github.com/restran/api-gateway)

