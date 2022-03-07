# Streamr Node Earnings Checker
Python script that shows statistics of your node earnings (see image for an example of all statistics).<br>
<br><b>Help a poor student in need 😁 </b><br>
Donations are very welcome (DATA, MATIC, ETH, ... everything else available on Polygon): <b>0x720D3842198A21403482C919841B81958B5220e1 </b> (Polygon and Etherium chain)
<br>
<h4><b>Only things to change</b></h4>

- Add your node addresses in the ```nodes.json``` file.
- Optional: add in which interval you would like to loop the script by changing variable ```output_frequency``` in Python file (default = 3600, don't recommend going lower than 3600 because the script requests a lot of information).


<h4><b>Requires the following imports to be installed</b></h4>

- requests
- datetime
- json
- apscheduler
- collections (installed by default on most systems).
- warnings (to suppress an annoying pandas package warning).
- pandas
- tabulate
- colorama

<h4><b>Sample output</b> <br><br></h4>

![image](https://user-images.githubusercontent.com/38588045/157060314-01209893-eb85-4777-bd06-0ae5802643a4.png)


<h4><b>How to run (presuming you have installed the required packages via pip + changed nodes.json) </b></h4>

```
git clone https://github.com/zertyn/streamr_node_earnings_checker.git
cd streamr_node_earnings_checker/
python3 data_earnings_checker.py
```

<h4><b>Want this code in .exe format? </b><br></h4>
Follow the following link (Make sure the nodes.json file is in the same folder as the .exe file): <br>
https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9

<br>
<h4> Possible solutions to errors </h4>
If you receive an error, or the Python window closes immediately, go through the following steps:

<ol>
  <li>Make sure you have installed all neccessary packages with the pip installer.</li>
  <li>Make sure you have filled in your nodes in the nodes.json file correctly (see example nodes file).</li>
  <li>Make sure when you launch the Python script, that you are in the correct directory.</li>
  <li>Make sure you launch the python script with by typing 'python data_earnings_checker.py' when in the correct directory.</li>
</ol>
