# 用户手册

## 情况
- dify.cn 
- dify.com
- do it for you!!!

## 前置条件
创建dify bot

# 项目

## 结构
```textyour_project/
├── Dockerfile
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py
    └── other_module.py
```


## 环境变量
```text
   API_BASE=http(s)://xxxx/v1
```

## model

```text 
chatbot:blocking
目前只支持到 /chat-messages 接口类型的bot(chatbot,agent,chatflow)
```

### 调试
![1726218901113.jpg](doc%2F1726218901113.jpg)
![请求体](doc/img_1.png)
![接口返回](doc/img_2.png)
content是list,元素有可能是多个图片链接，多个内容。使用时注意下。

##  效果
### dify of wechat
![img.png](doc/img.png)
# 部署
## 本地启动
```base 
    python run.py
```
## docker
docker build -t dify2openai:latest .
```bash
docker run --name dify2openai --restart=always -d -p 3000:3000 -e API_BASE={{API_BASE}}  dify2openai:latest
```

# 广告
最小化开发成本（近免费）可落地AI项目：本项目文档讲述利用头条，微头条/文章的AI自动生成的方式赚取收益
学习到python技术，服务器部署，国内模型有效利用，AI应用开发，AI应用平台使用，行业热门工具，系统架构集成
价值：启发，启蒙，编程，超级个体
https://icnyfaw3mn0d.feishu.cn/wiki/EahJwFXmji6RY0k4QAbcPodRnoc?from=from_copylink

