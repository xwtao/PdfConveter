# PDF在线转换平台

一个专业的在线PDF文件转换平台，提供多种文件格式转换服务，采用现代化技术栈和用户友好的界面设计。

## 功能特点

- 🚀 快速转换：支持PDF与Word、Excel、PPT等格式互转
- 🔒 安全可靠：文件加密传输，自动清理，保护隐私
- 💎 高级功能：OCR识别、批量处理、水印处理等
- 🌐 跨平台：支持Web端和离线客户端
- 🎯 精准转换：保持原文档格式和样式

## 技术栈

- 前端：Vue.js 3 + TypeScript + Tailwind CSS
- 后端：FastAPI + Celery
- 数据库：PostgreSQL
- 文件存储：七牛云对象存储
- 部署：Docker + Nginx

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/your-username/pdf-converter.git
cd pdf-converter
```

2. 安装后端依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息
```

5. 启动开发服务器
```bash
# 后端
uvicorn app.main:app --reload

# 前端
npm run dev
```

## 项目结构

```
pdf-converter/
├── frontend/          # 前端Vue项目
├── backend/           # 后端FastAPI项目
├── docs/             # 项目文档
│   ├── requirements.md   # 需求文档
│   ├── interaction.md    # 交互设计文档
│   └── ui-design.md     # UI设计规范
└── tests/            # 测试用例
```

## 文档

- [需求文档](docs/requirements.md)
- [交互设计文档](docs/interaction.md)
- [UI设计规范](docs/ui-design.md)

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系我们

- 网站：[https://www.pdfconverter.com](https://www.pdfconverter.com)
- 邮箱：support@pdfconverter.com
- 微信公众号：PDF转换助手 