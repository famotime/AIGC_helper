# AIGC_helper
AI绘画辅助脚本，包括自动解析从Civitai网站例图拷贝的生成参数，通过脚本传递到SD WebUI的API作画，相比手工操作提升效率。

## 操作步骤

1. 在Civitai网站拷贝例图生成参数；
    ![image-20230311233953065](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20230311233953065.png)

2. 在SD WebUI选择合适的模型；

   ![image-20230311234019615](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20230311234019615.png)

3. 运行脚本（parse_and_create.py），调用API生成图像，并保存到本地；

   ![image-20230311234515362](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20230311234515362.png)

   ![(extremely detailed photo 8k), full body shot photo of the most beautiful artwork in the world, beautiful woman engineer, ( rainbow hair), cleava_0](E:\novelai-webui\outputs\txt2img-images\(extremely detailed photo 8k), full body shot photo of the most beautiful artwork in the world, beautiful woman engineer, ( rainbow hair), cleava_0.png)

## 脚本说明

- **parse_and_create.py:** 解析Civitai网站例图生成参数，或者从现有图片文件读取生成参数，并调用SD WebUI的API作画
- **training_helper.py:** 模型训练辅助脚本，批量增删标签、统计标签频次
- **create_with_webuiapi.py:** 使用webuiapi库调用API作画
