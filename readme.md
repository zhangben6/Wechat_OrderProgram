# Python Flask 订餐系统

### author: rapzhang
### env: python3.5
### Email: rapzhang97@163.com
### Github: http://github.com/zhangben6

********************************
## 1.命令行启动项目
    export ops_config=local|production && python manager.py runserver
## 2.使用 flask-sqlacodegen 扩展 方便快速生成 ORM model
**例如:flask-sqlacodegen 'mysql+pymysql://root:123456@127.0.0.1/food_db' --tables user --outfile "common/models/user.py"  --flask**
