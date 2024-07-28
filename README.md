# 站点
## 关于我们

该项目为满足个人记录学习、工作、兴趣的需求进行开发。

**该项目是很多技术和思路均借鉴于 [DjangoBlog](https://github.com/liangliangyy/DjangoBlog) 项目，甚至可以说是魔改，在这里非常感谢 [DjangoBlog](https://github.com/liangliangyy/DjangoBlog) 项目！！！**

## 联系我们

邮箱: spaceprivate#163.com(#->@)

## 更新日志

2024年07月27日

手动部署上线

2024年07月23日

网站主体功能完成

## 手动部署

在 `./mysite/settings/py` 中 ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS 添加自己的 IP, 或者域名(**docker 部署也需要修改**)

依赖 mysql8.0, redis, elasticsearch8.12.2, [analysis-ik](https://github.com/infinilabs/analysis-ik), gunicorn, nginx

注意静态文件收集在 `/var/www/static`

网上有许多教程不再赘述

## docker 部署

如 docker_start.sh 无权限，请在 docker 环境外也赋予权限

```shell
chmod +x ./bin/docker_start.sh
```

docker 部署方案与 [DjangoBlog](https://github.com/liangliangyy/DjangoBlog) 项目类似，可参考其部署方法

添加域名，ssl证书请自行修改 `./bin/nginx.conf`

使用 es 版

使用 https 和设置密码请自行研究

>在 `docker-compose.yml` 文件中 `mysite`中添加以下内容

```yaml
environment:
  ELASTICSEARCH_HOST: es
  ELASTICSEARCH_PORT: 9200
depends_on:
      - es
```

```shell
chown -R 1000:1000 /usr/share/elasticsearch/data
docker-compose -f docker-compose.yml -f docker-compose-es.yml build
docker-compose -f docker-compose.yml docker-compose-es.yml up -d
```