# streamr_node_earnings_checker
Simple Python script that shows basic statistics of your node earnings.<br>
&emsp; <b>Help a poor student in need 😁: </b><br>
&emsp; Donations are very welcome (DATA, ETH): 0x720D3842198A21403482C919841B81958B5220e1 (Polygon and Etherium chain)

<b>v1.2: Only things to change:</b>
- Add your node addresses in the ```nodes.json``` file.
- Optional: add in which interval you would like to loop the script by chaning the variable ```output_frequency``` (default = 3600, once per hour).

<b>Requires the following imports to be installed:</b>
- requests
- json
- apscheduler
- datetime (installed by default on most systems).

<b>Sample output:</b> <br><br>
![image](https://user-images.githubusercontent.com/38588045/156552210-f862cdfc-1666-4c63-a585-8fc6ca9b0155.png)

<b>How to run (presuming you have installed the required packages via pip already):</b>
```
git clone https://github.com/zertyn/streamr_node_earnings_checker.git
cd streamr_node_earnings_checker/
python3 data_earnings_checker.py
```
<b>Want this code in .exe format? Follow the following link:</b><br>
https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9

Make sure the config file is in the same folder as the .exe file.

<b> If you receive an error, or the Python window closes immediately, go through the following steps: </b>
1: Make sure you have installed all neccessary packages with the pip installer.
2: Make sure when you launch the Python script, that you are in the correct directory.
3: Make sure you have filled in your nodes in the nodes.json file.
3: Make sure you launch the python script with by typing 'python data_earnings_checker.py' when in the correct directory.
