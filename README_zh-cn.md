# TiebaGuardian 贴吧守护者

一个基于Python的，强大实用的百度贴吧吧务自动管理脚本。
## 功能

1.回复，帖子内容关键词过滤

2.针对帖子的防爆吧检测（频率检测，淹没检测）

2*.瞬间封禁功能（检测到频率过高的帖子，直接封禁删帖，不对内容进行进一步判断，有效防止爆吧）

3.针对所有内容发布者的小号发帖检测（关注数量，粉丝数量，历史发帖数量）

4.帖子/回复内容长度检测

5.自定义扫描范围（即从首页第一个帖子向后计数，直到设定值）

6.针对发布者的 黑/白名单

7.特色功能：白色关键词（若帖子中检测到这些关键词，则减少违规权值）

8.权值计算系统，多因素违规判断（即每一个检测项都有对应的权值，所有增减权值的幅度可自定义，封禁/删帖的权值判断门限也可自定义）

## 入门

以下这些说明将详细快速地让您知道如何部署和使用脚本。
让我们开始吧！

### 运行要求

这里是脚本正常运行的要求

#### 网络要求

您设备的网络必须 **能够连接百度贴吧服务器**, 尝试访问 http://tieba.baidu.com 来确定。

最佳的网络延迟为**≤200ms**，高于此界限可能在一定程度上拖慢脚本的运行速度。

#### 内存要求

根据实测, 最低内存要求是 **25 MB** (取决于你设置的配置)，请确保内存充足。

#### 系统&软件要求

你需要在设备中安装 **Python 3.7 及以上版本**

脚本已经在 **Windows 10 和 Ubuntu v18.04** 上进行过测试，对于其他系统的兼容性暂时未知。

### 部署教程

TiebaGuardian是一个Python脚本。为了使它易于使用，整个脚本是一个单一的执行过程，因此当您运行脚本时，它只运行一次。

为了实现自动扫描，我们使用**Linux Crontab**或**Windows 计划任务**定期运行脚本。

我不会详细描述如何创建定时任务，请确保您具有Windows和Linux的基本知识。您可以在网上搜索如何使用这两个工具。

您需要同时下载脚本文件和对应的配置文件，确保这两个文件在同一个目录下，确保配置文件填写完整，脚本并不会自动生成配置文件，也不会自动缺省没有填写的配置项。

您可以查看本项目的[Wiki](https://github.com/SheepChef/TiebaGuardian/wiki)来查看更多信息

## 项目开发者

* [**SheepChef**](https://github.com/SheepChef)

## 许可证

本项目使用 GNU 许可 - 参阅 [LICENSE](LICENSE) 文件。

## 其他语言 / Other Languages

English Readme is [here](README.md)
