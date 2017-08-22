# A simple but beautiful blog

### 简介

这是我编写的一个多页博客，后端使用的是`Flask`+`Mysql`，前端使用的是`UIkit+Vue`，使用`Gunicorn`+`Nginx`部署在阿里云服务器上。
### GitHub地址

<a href="https://github.com/william302/blog">点我</a>

### 功能

<ul>
	<li>注册，登录</li>
	<li>发布文章</li>
	<li>发布，回复,管理评论</li>
	<li>后台管理功能</li>
</ul>

### 本地使用

安装需要的库
```
$ pip install -r requirements.txt
```
更新数据库，获得角色权限
```
$ main.py deploy
```
运行
```
$ main.py runserver --host 0.0.0.0
```
打开本地浏览器访问`127.0.0.1：8080`即可。



### 阿里云部署

本网站是部署在阿里云上，利用Gunicorn+Nginx部署

在阿里云上部署较为复杂，具体部署参考文章：[文章地址](http://blog.csdn.net/u012675539/article/details/50836775)

### Enjoy it.
