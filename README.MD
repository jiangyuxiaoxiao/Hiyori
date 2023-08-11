<div align="center">
    <a href="https://Hiyori.vip">
        <img src="https://github.com/jiangyuxiaoxiao/Hiyori/blob/master/Hiyori/Data/Web/ZSign/assets/catch02.png?raw=true" alt="Hiyori" style="height: 200px;width: auto">
    </a>
    <h1>Hiyori Bot</h1>
    <h3>基于Nonebot2框架的QQ聊天机器人</h3>
    <a href="https://Hiyori.vip">
       项目文档
    </a>
    <p align="left">
      <img alt="Static Badge" src="https://img.shields.io/badge/python-3.10+-blue">
      <a href="https://github.com/nonebot/nonebot2">
        <img alt="nonebot2-2.0.1" src="https://img.shields.io/badge/nonebot2-2.0.1-orange">
      </a>
      <a href="https://github.com/nonebot/adapter-onebot">
        <img alt="onebot-v11" src="https://img.shields.io/badge/onebot-V11-orange">
      </a>
      <a href="https://github.com/Mrs4s/go-cqhttp">
        <img alt="go cqhttp-1.1.0" src="https://img.shields.io/badge/go cqhttp-1.1.0-orange">
      </a>
    </p>  

</div>

## 简介

## 特色

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
+ 有趣的互动插件：
    + ...

## 妃爱，启动！

## Todo List

+ Web控制台
    + 控制台开关插件
    + 功能调用统计
    + 消息处理
    + 好友、群聊申请处理
    + 服务器状态监控
+ UI重构
+ 市场功能新增
+ 冷却功能添加新特性：支持单日功能调用次数限制、支持单次调用间隔
+ 更多管理支持：指令修改用户数据
+ 插件调用耗时统计
+ 添加单元测试