# TiebaGuardian

A powerful, useful Tieba-managing Python script.

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

I won't describe how to create timed task in detail, make sure you have the basic knowledge of Windows and Linux. You can search how to use these two tools on the web.

#### Windows

1.Open Control Panel

2.Open Administrative Tools

3.Open Task Schedule

4.Click "Create Basic Task"

5.Just choose a appropriate frequency and create the timed task.

#### Linux

1.Run ```crontab -e``` in shell

2.Edit the crontab as you want, and save it.

## Authors

* [**SheepChef**](https://github.com/SheepChef)

## License

This project is licensed under the GNU License - see the [LICENSE.md](LICENSE.md) file for details

## Other Languages

简体中文Readme请见此处
