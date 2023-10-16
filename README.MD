<div align="center">
    <a href="https://Hiyori.vip">
        <img src="https://github.com/jiangyuxiaoxiao/Hiyori/blob/master/Hiyori/Data/Web/ZSign/assets/catch02.png?raw=true" alt="Hiyori" style="height: 200px;width: auto">
    </a>
    <h1>Hiyori Bot</h1>
    <h3>基于Nonebot2框架的QQ聊天机器人</h3>
    <p align="center">
      <a href="https://www.python.org/">
        <img alt="Static Badge" src="https://img.shields.io/badge/python-3.10+-blue">
      </a>
      <a href="https://github.com/nonebot/nonebot2">
        <img alt="nonebot2-2.0.1" src="https://img.shields.io/badge/nonebot2-2.0.1-orange">
      </a>
      <a href="https://github.com/nonebot/adapter-onebot">
        <img alt="onebot-v11" src="https://img.shields.io/badge/onebot-V11-orange">
      </a>
      <a href="https://github.com/Mrs4s/go-cqhttp">
        <img alt="go cqhttp-1.1.0" src="https://img.shields.io/badge/go cqhttp-1.1.0-orange">
      </a>
      <a href="https://wakatime.com/badge/user/7b275a68-8fe7-44fb-9b22-86cfd199fc1e/project/3d1eb992-cc9a-4fee-8d6a-337d2fee4569">
        <img src="https://wakatime.com/badge/user/7b275a68-8fe7-44fb-9b22-86cfd199fc1e/project/3d1eb992-cc9a-4fee-8d6a-337d2fee4569.svg" alt="wakatime">
      </a>
    </p>  

   <a href="http://和泉妃爱.com">
       项目文档
    </a>
</div>

## 简介

超可爱的妃爱群聊机器人！

## 关于Go-Cqhttp [#2471](https://github.com/Mrs4s/go-cqhttp/issues/2471)
+ 复活吧！我的gocq！  
+ gocq，没有你我怎么活啊   
+ **收购tx已经刻不容缓了**   
+ 若未来没有支持`Onebot`标准的QQ客户端，Hiyori将完全重构，目前打算迁移至`Satori`，持续观望中

## 特色

+ 是超可爱的妃爱
+ 使用 Nonebot2 框架 + Go-Cqhttp QQ协议端 + OnebotV11 规范
+ 丰富的管理功能、Bot特性支持：
    + 插件开关
    + 插件菜单生成
    + 黑名单管理
    + 定时撤回
    + 调用冷却
    + 自定义物品开发
    + 多CQHTTP客户端连接支持：
        + 多Bot在同一群聊时不重复处理事件，自动选择指定Bot进行事件处理
        + 多Bot在同一群聊时，处理Bot下线后自动切换到备用Bot
    + 多API对接封装：百度网盘、百度翻译、华为云DNS
    + 群文件同步备份
+ 有趣的互动插件：
    + 群友购买
    + 自定义商店
    + 现货炒股
    + 群聊消息制作
    + 签到、抽签
    + 抽卡
    + 表情包制作
    + 重开模拟器
    + ...

## 妃爱，启动！

### windows启动

+ 安装Python3.10
+ 下载妃爱release包
+ 配置[Go-cqhttp](https://github.com/Mrs4s/go-cqhttp)的config.yml，填写QQ号与密码
+ 运行 `环境安装.bat` （第一次运行时）
+ 运行 `Qsign，启动！.bat`
+ 运行 `妃爱，启动！.bat`
+ 等待Qsign服务开始
+ 运行 `CQHTTP，启动！.bat`

### linux启动

+ 下载配置[Go-cqhttp](https://github.com/Mrs4s/go-cqhttp)及[qsign](https://github.com/fuqiuluo/unidbg-fetch-qsign)
  1.1.0（2023/08/11）
+ 安装Python3.10
+ 下载妃爱
+ 根据requirements.txt安装python环境
+ 在环境下运行`meme download`

```shell
cd ./Hiyori
python3 hiyori.py
```

## 快速使用手册

+ [项目文档：http://和泉妃爱.com](http://和泉妃爱.com)

+ 超级管理员设置    
  在`.env.hiyori`中设置`SUPERUSERS=["你的QQ号"]`，可参考[Nonebot2配置文档](https://nonebot.dev/docs/appendices/config#superusers)

+ 黑名单管理
    + 所有群聊默认为拉黑状态，超级管理员可以使用`#unban -g`指令进行解封
    + 解封/拉黑对话所在群聊：`#unban -g`/`#ban -g`
    + 解封/拉黑特定群聊：`#unban -g 群号`/`#ban -g 群号`
    + 解封/拉黑指定人：`#unban -u QQ号`/`#ban -u QQ号` 或 `#unban -u @人`/`#ban -u @人`

+ 插件手册  
  `#帮助`

+ 设置群聊/用户的冷却权重  
  `#change cd -u 权重数值` `#change cd -g 权重数值`  
  用户默认权重20，群聊默认权重30。权重越大回复的上限频率越高

+ 多Bot连接配置
    + 指令配置：在群聊中使用指令`妃爱启动 @指定bot`：该群聊默认由该bot进行响应
    + 配置文件配置：修改`Hiyori/Data/MultiBot_Support/config.json`文件后重启。其中默认优先顺序为无群组规则时bot响应的优先顺序，配置文件书写示例如下所示：

```json
{
  "默认优先顺序": [
    "QQ号",
    "QQ号",
    "QQ号"
  ],
  "群组规则": {
    "群号1": "QQ号",
    "群号2": "QQ号",
    "群号3": "QQ号"
  }
}
```

+ 广播  
  使用指令`#broadcast 要说的话`，会广播到当前没有关闭或者没有被封禁的所有群中。广播容易引发风控，广播消息容易发送失败，谨慎使用。

## Todo List

+ Web控制台
    + 插件管理
    + 功能调用统计
    + 消息处理
    + 好友、群聊申请处理
    + 服务器状态监控
+ UI重构
+ 市场功能新增
+ 冷却功能添加新特性：支持单日功能调用次数限制、支持单次调用间隔
+ 更多管理支持：
    + 更多修改用户数据指令
    + 预设情景支持
+ 插件调用耗时统计
+ 更多物品
+ 更多互动事件
+ 添加单元测试

## 致谢

妃爱在开发过程中使用了如下项目，感谢这些开发者与项目对妃爱的贡献：

+ [nonebot/nonebot2](https://github.com/nonebot/nonebot2)
+ [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
+ [nonebot/adapter-onebot](https://github.com/nonebot/adapter-onebot)
+ [fuqiuluo/unidbg-fetch-qsign](https://github.com/fuqiuluo/unidbg-fetch-qsign)
+ [nonebot/plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler)
+ [he0119/nonebot-plugin-datastore](https://github.com/he0119/nonebot-plugin-datastore)
+ [kexue-z/nonebot-plugin-htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender)
+ [noneplugin/nonebot-plugin-imageutils](https://github.com/noneplugin/nonebot-plugin-imageutils)
+ [nonebot/plugin-localstore](https://github.com/nonebot/plugin-localstore)
+ [MountainDash/nonebot-plugin-send-anything-anywhere](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere)
+ [mengshouer/nonebot_plugin_analysis_bilibili](https://github.com/mengshouer/nonebot_plugin_analysis_bilibili)
+ [Melodyknit/nonebot_plugin_animeres](https://github.com/Melodyknit/nonebot_plugin_animeres)
+ [KafCoppelia/nonebot_plugin_fortune](https://github.com/KafCoppelia/nonebot_plugin_fortune)
+ [mnixry/nonebot-plugin-guild-patch](https://github.com/mnixry/nonebot-plugin-guild-patch)
+ [noneplugin/nonebot-plugin-memes](https://github.com/noneplugin/nonebot-plugin-memes)
+ [lgc-NB2Dev/nonebot-plugin-picmcstat](https://github.com/lgc-NB2Dev/nonebot-plugin-picmcstat)
+ [lgc-NB2Dev/nonebot-plugin-picstatus](https://github.com/lgc-NB2Dev/nonebot-plugin-picstatus)
+ [noneplugin/nonebot-plugin-remake](https://github.com/noneplugin/nonebot-plugin-remake)
+ [MinatoAquaCrews/nonebot_plugin_tarot](https://github.com/MinatoAquaCrews/nonebot_plugin_tarot)
+ [glamorgan9826/nonebot-plugin-today-waifu](https://github.com/glamorgan9826/nonebot-plugin-today-waifu)
+ [SEAFHMC/nonebot-plugin-who-at-me](https://github.com/SEAFHMC/nonebot-plugin-who-at-me)
+ [Kaguyaya/nonebot_plugin_ygo_trade](https://github.com/Kaguyaya/nonebot_plugin_ygo_trade)

