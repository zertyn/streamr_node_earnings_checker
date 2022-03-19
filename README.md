# Streamr Node Earnings Checker
Python script that shows statistics of your node earnings (see image for an example of all statistics).<br>
<br><b>Help a poor student in need 😁 </b><br>
Donations are very welcome (DATA, MATIC, ETH, ... everything else available on Polygon): <b>0x720D3842198A21403482C919841B81958B5220e1 </b> (Polygon and Etherium chain)
<br>
<h4><b>Only things to change</b></h4>

- Add your node addresses in the ```config.json``` file.
- Optional: add your gmail email and extra settings in ```config.json``` to your liking (if you have 2FA gmail account, check this link to make a temporary password: https://support.google.com/accounts/answer/185833?hl=en). Leave the values 0 or false if you don't want emails. 
- Caution: Only change the time settings if you know what you're doing (don't go under 3600 with any value)! 

<h4><b>Uses the following imports/requires the following packages to be installed</b></h4>

- requests
- datetime
- json
- apscheduler
- collections (installed by default on most systems).
- warnings (to suppress an annoying pandas package warning).
- pandas
- tabulate
- email

<h4><b>Sample output</b> <br><br></h4>

![image](https://user-images.githubusercontent.com/38588045/157060314-01209893-eb85-4777-bd06-0ae5802643a4.png)


<h4><b>How to run in Python (presuming you have installed the required packages via pip + changed config.json) </b></h4>

```
git clone https://github.com/zertyn/streamr_node_earnings_checker.git
cd streamr_node_earnings_checker/
pip install -r requirements.txt
python3 data_earnings_checker.py
```

<br>
<h4> Possible solutions to errors </h4>
If you receive an error, or the Python window closes immediately, go through the following steps:

<ol>
  <li>Make sure you have installed all neccessary packages with the pip installer.</li>
  <li>Make sure you have filled in your information in the config.json file correctly (see example nodes file).</li>
  <li>Make sure you have generated a temporary password for your gmail account if you have 2FA enabled: https://support.google.com/accounts/answer/185833?hl=en.</li>
  <li>if you launch the script via Python: make sure when you launch the Python script, that you are in the correct directory.</li>
  <li>if you launch the script via the .exe: make sure the config.json is in the same directory as the .exe file </li>
</ol>
