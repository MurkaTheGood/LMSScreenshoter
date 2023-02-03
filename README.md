# LMSScreenshoter
This program screenshots every question on Polytech questions overview

## Requirements
Tested on Linux Mint 20.3.
You must have some requirements satisfied on your workstation to make this app work:
1. Python
  - use `apt install python3.9` to install Python on systems those use `apt-get` as their packet manager
2. Selenium
  - use `python3.9 -m pip install selenium` to install the Selenium
3. Firefox webdriver (geckodriver)
  - sorry, I don't know how to install it. Google something like `install geckodriver linux`

## How to use
`
git clone https://github.com/MurkaTheGood/LMSScreenshoter
cd LMSScreenshoter
python3.9 screenshoter.py
`
Further instructions will be printed in terminal

## Where are the screenshots?
Screenshots are saved to directory `screenshots/DATE/`, where `DATE` is date and time of screenshots saving
