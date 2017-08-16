# A simple but beautiful blog

### 简介

这是一个使用 `Python` 的 `Flask` 框架编写的部署在阿里云上的一个适合多人使用的社交型网站。
头像使用的是gravatar头像系统，由于gravatar在国外，所以因为网络原因有时头像会无法显示- -！
博客带有分页展示功能，博客管理页面使用的是AJAX实时刷新文章

### 地址

<a href="www.william902.com">www.william902.com</a> 

### 功能

<ul>
	<li>注册，登录</li>
	<li>发布文章</li>
	<li>发布，回复,管理评论</li>
	<li>设置资料</li>
	<li>管理员功能</li>
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

本网站是部署在阿里云上，利用Flask+Gunicorn+Nginx部署

在阿里云上部署较为复杂，具体部署参考文章：[文章地址](http://blog.csdn.net/u012675539/article/details/50836775)

### Enjoy it.
