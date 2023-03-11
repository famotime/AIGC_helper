# AIGC_helper
AI绘画辅助脚本，包括civiai例图参数解析，通过SD WebUI的API作画等。


- **parse_and_create.py:** 解析Civitai网站例图生成参数，或者从现有图片文件读取生成参数，并调用SD WebUI作画
- **training_helper.py:** 模型训练辅助脚本，批量增删标签、统计标签频次
- **create_with_webuiapi.py:** 使用webuiapi库调用API作画
