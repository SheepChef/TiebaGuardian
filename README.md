# TiebaGuardian

A powerful, useful Tieba-managing Python script.

## Functions

(Warning：This part is Machine-Translated from Chinese, the accuracy might be low.)

1. Reply, post content keyword filtering

2. Explosion proof bar detection for posts (frequency detection, submergence detection)

3. Instant blocking function (detect posts with too high frequency, directly block and delete posts, without further judgment of the content, effectively prevent the explosion)

4. Illegal account detection for all content publishers (number of concerns, number of fans, number of historical posts)

5. Post / reply content length detection

6. Customize the scanning range (i.e. count back from the first post on the home page to the set value)

7. Black / white list for publishers

8. Feature function: white keywords (if these keywords are detected in the post, the violation weight will be reduced)

9. Weight calculation system, multi factor violation judgment (that is, each detection item has corresponding weight, the range of weight increase or decrease can be customized, and the weight judgment threshold of blocking / deleting posts can also be customized)

## Getting Started

The instructions below will let you quickly know how to use the script.
Let's get right into it!

### Requirements

Here are the requirements of running the script.

#### Network

The basic requirement is that your device need to **be able connect to Baidu Tieba server**, you can try accessing http://tieba.baidu.com to see whether you can or not.

The network lag limit that can basicly support the script run perfectly is **≤200ms**.

#### RAM

According to the experiment, the lowest RAM requirement is **25 MB** (depend on what configuration you've set). Make sure you have enough memory left.

#### System & Software

You need to install **Python 3.7 and up** on your device.

The script is tested on **Windows 10 and Ubuntu v18.04**. The other system should be compatible.

### How to deploy the script

TiebaGuardian is a python script. In order to make it easy to use, the whole script is a single execution process, so when you run the script, it runs only once.

To realize auto scanning, we use **Linux Crontab** or **Windows Task Schedule** to run the script regularly.

You can check the detail on [Wiki](Wiki)

## Authors

* [**SheepChef**](https://github.com/SheepChef)

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details

## Other Languages

简体中文Readme, [请见此处](README_zh-cn.md)
