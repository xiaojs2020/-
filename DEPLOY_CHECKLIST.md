# ✅ 部署检查清单

## 文件检查
- [x] `app.py` - 主应用文件
- [x] `wsgi.py` - WSGI入口文件
- [x] `requirements.txt` - 包含所有依赖
- [x] `gunicorn_config.py` - Gunicorn配置
- [x] `作息.csv` - 数据文件
- [x] `.gitignore` - Git忽略文件

## 代码检查
- [x] 应用端口设置为10000
- [x] 所有依赖都在requirements.txt中
- [x] 没有硬编码的本地路径
- [x] 数据文件能正确加载

## 部署步骤
1. [ ] 创建GitHub仓库
2. [ ] 推送代码到GitHub
3. [ ] 在Render上创建Web Service
4. [ ] 配置构建和启动命令
5. [ ] 等待部署完成
6. [ ] 测试应用功能

## 构建命令
```bash
pip install -r requirements.txt
```

## 启动命令
```bash
gunicorn wsgi:app.server --config gunicorn_config.py
```

## 预期结果
- 应用在 `https://your-app-name.onrender.com` 上运行
- 首次访问有30秒-1分钟的启动延迟
- 15分钟不活动后会自动休眠
